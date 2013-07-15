from charmhelpers.core.hookenv import (
    config,
    relation_ids,
    related_units,
    relation_get
)
from charmhelpers.contrib.openstack.context import (
    OSContextGenerator,
    context_complete
)
from charmhelpers.contrib.hahelpers.apache import (
    get_cert
)
from base64 import b64decode
import os


class HAProxyContext(OSContextGenerator):
    def __call__(self):
        '''
        Extends the main charmhelpers HAProxyContext with a port mapping
        specific to this charm.
        '''
        ctxt = {
            'service_ports': {
                'dash_insecure': [80, 70],
                'dash_secure': [443, 433]
            }
        }
        return ctxt


class IdentityServiceContext(OSContextGenerator):
    def __call__(self):
        ''' Provide context for Identity Service relation '''
        ctxt = {}
        for r_id in relation_ids('identity-service'):
            for unit in related_units(r_id):
                ctxt['service_host'] = relation_get('service_host',
                                                    rid=r_id,
                                                    unit=unit)
                ctxt['service_port'] = relation_get('service_port',
                                                    rid=r_id,
                                                    unit=unit)
        if not context_complete(ctxt):
            return {}
        return ctxt


class HorizonContext(OSContextGenerator):
    def __call__(self):
        ''' Provide all configuration for Horizon '''
        ctxt = {
            'compress_offline': config('offline-compression') == 'yes',
            'debug': config('debug') == 'yes',
            'default_role': config('default-role'),
            "webroot": config('webroot')
        }
        return ctxt


class ApacheContext(OSContextGenerator):
    def __call__(self):
        ''' Grab cert and key from configuraton for SSL config '''
        ctxt = {
            'http_port': 70,
            'https_port': 433
        }
        return ctxt


class ApacheSSLContext(OSContextGenerator):
    def __call__(self):
        ''' Grab cert and key from configuration for SSL config '''
        (ssl_cert, ssl_key) = get_cert()
        if None not in [ssl_cert, ssl_key]:
            with open('/etc/ssl/certs/dashboard.cert', 'w') as cert_out:
                cert_out.write(b64decode(ssl_cert))
            with open('/etc/ssl/private/dashboard.key', 'w') as key_out:
                key_out.write(b64decode(ssl_key))
            os.chmod('/etc/ssl/private/dashboard.key', 0600)
            ctxt = {
                'ssl_configured': True,
                'ssl_cert': '/etc/ssl/certs/dashboard.cert',
                'ssl_key': '/etc/ssl/private/dashboard.key',
            }
        else:
            # Use snakeoil ones by default
            ctxt = {
                'ssl_configured': False,
            }
        return ctxt
