import dns.resolver
from .util import single

def locate_service(domain, service, proto='tcp'):
    service = '_' + service
    proto = '_' + proto
    query = '.'.join((service, proto, domain))

    # This can raise dns.resolver.NoAnswer
    records = dns.resolver.query(query, 'SRV')

    # TODO: Sort records by priority (lowest first), then by weight (highest first)

    for r in records:
        yield (r.target.to_text(True), r.port)


def locate_ldap_server(domain):
    return locate_service(domain, 'ldap', 'tcp')


def get_domain_ldap_servers(domain, proto=None):
    """Returns a list of ldap URIs for the given domain"""
    if proto is None:
        proto = 'ldap'

    for host, port in locate_ldap_server(domain):
        yield '{}://{}:{}'.format(proto, host, port)


def get_pdc_emulator_ldap_server(domain, proto=None):
    """Returns the ldap URI of the DC holding the PDC Emulator FSMO role"""
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/c1987d42-1847-4cc9-acf7-aab2136d6952
    domain = 'pdc._msdcs.' + domain
    return single(get_domain_ldap_servers(domain, proto=proto))


if __name__ == '__main__':
    import sys
    domain = sys.argv[1]
    print("PDC Emulator:", get_pdc_emulator_ldap_server(domain))
