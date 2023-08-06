from datetime import datetime
import logging
from pprint import pformat
import ldap

from .types import SID
from .util import FILETIME_to_datetime, single

logger = logging.getLogger(__name__)

NOT_PRESENT = object()


class AttrBase:
    def __init__(self, name, ldapattr=None, writable=False, atomic=False):
        """
        Parameters:
        name        Python attribute name
        ldapattr    LDAP attribute name (defaults to name)
        writable    True if the attribute can be changed (defaults to False)
        atomic      True if LDAP modifiations should be made atomic (defaults to False)
        """
        self.name = name
        self.ldapattr = ldapattr or name

        if atomic and not writable:
            raise ValueError("atomic but not writable is nonsensical")
        self.writable = writable
        self.atomic = atomic

    def decode(self, in_bytes):
        raise NotImplementedError()

    def encode(self, val):
        raise NotImplementedError()


    def encode_values(self, values):
        """Convert Python values to python-ldap values"""
        # Values are always lists with python-ldap
        if not isinstance(values, list):
            values = [values]

        # And each value must be a bytes string, ugh.
        result = []
        for v in values:
            # Filter out None values
            # A scalar None in the Python side yields an empty list,
            # which results in a DELETE operation during commit.
            if v is None:
                continue

            # Encode to bytes string
            assert isinstance(v, self.basetype)
            result.append(self.encode(v))

        return result

# TODO: Handle encoding throughout these types

class StrAttr(AttrBase):
    basetype = str

    def decode(self, in_bytes):
        return in_bytes.decode()

    def encode(self, val):
        return val.encode()


class IntAttr(AttrBase):
    basetype = int

    def decode(self, in_bytes):
        # python-ldap returns decimal string (bytes)
        return int(in_bytes)

    def encode(self, val):
        return str(val).encode()


class SIDAttr(AttrBase):
    basetype = SID

    def decode(self, in_bytes):
        return SID.from_bytes(in_bytes)


class FILETIMEAttr(AttrBase):
    basetype = datetime

    def decode(self, in_bytes):
        return FILETIME_to_datetime(int(in_bytes))


class LdapObject:
    @classmethod
    def default_ldap_attrs(cls):
        return [a.ldapattr for a in cls._known_attrs]

    @classmethod
    def _get_known_attr(cls, name):
        for ka in cls._known_attrs:
            if ka.name == name:
                return ka
        raise KeyError(name)


    def __init__(self, ad, dn, **attrs):
        super().__setattr__('_data', {})
        super().__setattr__('_ad', ad)
        super().__setattr__('_dn', dn)
        super().__setattr__('_pending_changes', {})

        for ka in self._known_attrs:
            val = attrs.get(ka.ldapattr)
            if val is not None:
                # python-ldap always returns attributes as strings in a list
                assert isinstance(val, list)
                val = single(val)   # TODO: Handle multi-valued attributes
                val = ka.decode(val)

            self._data[ka.name] = val

    @property
    def dn(self):
        return self._dn

    def __str__(self):
        s = self.dn

        for ka in self._known_attrs:
            val = getattr(self, ka.name, None)
            if val is not None:
                s += ', {}={}'.format(ka.name, val)

        return s

    def __dir__(self):
        return super().__dir__() + list(self._data.keys())

    def __getattr__(self, name):
        # This is only called when normal method raises AttributeError which
        # makes our internal implementation easier

        # First see if it's in the pending changes
        try:
            return self._pending_changes[name]
        except KeyError:
            pass

        # Then try to get it from the normal data store
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self), name))


    def __setattr__(self, name, value):
        # See if this is a class attribute being set (property)
        try:
            v = getattr(type(self), name)
        except AttributeError:
            pass
        else:
            return super().__setattr__(name, value)

        # See if this is a known LDAP attribute
        try:
            ka = self._get_known_attr(name)
        except KeyError:
            # No creation of unknown attributes allowed
            raise AttributeError("'{}' object does not allow attribute '{}' to be set".format(type(self), name))

        if not ka.writable:
            raise AttributeError("'{}' object attribute '{}' is read-only".format(type(self), name))

        # Verify the the new value's type
        if value is not None:
            if not isinstance(value, ka.basetype):
                raise TypeError("'{}' object attribute '{}' must be type '{}'"
                        .format(type(self), name, type(ka.basetype)))


        # Is the actually a change, to either the backing value or an exising pending change?
        pending_change = self._pending_changes.get(name, NOT_PRESENT)
        if pending_change is not NOT_PRESENT:
            if value == pending_change:
                logger.debug("Identical pending change to attribute {} ({})".format(name, value))
                return

        if value == self._data.get(name, NOT_PRESENT):
            logger.debug("New value matches backing value for attribute {} ({})".format(name, value))
            try:
                del self._pending_changes[name]
            except KeyError:
                pass
            else:
                logger.debug("Pending change to attribute {} reverted ({})".format(name, value))
            return

        # Store the pending change
        logger.debug("Storing pending change: {} => {}".format(name, value))
        self._pending_changes[name] = value


    def _get_pending_modlist(self):
        modlist = []
        for k, new_values in self._pending_changes.items():
            # Keys are Python attributes; map them to ldap attributes
            ka = self._get_known_attr(k)

            new_values = ka.encode_values(new_values)

            if ka.atomic:
                # If the attrs are marked "atomic", then we include the old
                # values in the DELETE.
                # https://ldapwiki.com/wiki/LDIF%20Atomic%20Operations
                old_values = self._data[k]  # not optional!
                old_values = ka.encode_values(old_values)

                if old_values:
                    # If we are setting a currently-unset attribute, we must
                    # omit the DELETE. This is safe because if the attribute
                    # actually does have a value in LDAP, the subsequent ADD
                    # will fail (as it should).
                    modlist.append((ldap.MOD_DELETE, ka.ldapattr, old_values))
                if new_values:
                    modlist.append((ldap.MOD_ADD, ka.ldapattr, new_values))
            else:
                # Non-atomic: Use REPLACE so we don't care if there are
                # existing old values
                modlist.append((ldap.MOD_REPLACE, ka.ldapattr, new_values))

        return modlist


    def commit(self):
        modlist = self._get_pending_modlist()

        if modlist:
            logger.debug("Ready to modify {} with changelist:\n{}".format(
                self.dn, format_modlist(modlist)))
            self._ad._modify(self.dn, modlist)
        else:
            logger.debug("Nothing to modify in {}".format(self.dn))

        # Move everything from _pending_changes to _data
        self._data.update(self._pending_changes)
        self._pending_changes.clear()


def format_modlist(modlist):
    opnames = {
        ldap.MOD_ADD:       'MOD_ADD',
        ldap.MOD_DELETE:    'MOD_DELETE',
        ldap.MOD_REPLACE:   'MOD_REPLACE',
        ldap.MOD_INCREMENT: 'MOD_INCREMENT',
    }

    newlist = []
    for op, atype, val in modlist:
        opname = opnames[op]
        newlist.append((opname, atype, val))

    return pformat(newlist)
