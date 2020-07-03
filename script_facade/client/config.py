import os
from jinja2 import Environment, PackageLoader, select_autoescape

class DefaultConfig(object):
    # SOAP endpoint URL
    SCRIPT_ENDPOINT_URL = os.environ.get('SCRIPT_ENDPOINT_URL', 'https://gateway-prep.pmp.appriss.com/ncpdp_requests')
#    SCRIPT_ENDPOINT_URL = os.environ.get('SCRIPT_ENDPOINT_URL', 'https://calm.cirg.us/cgi-bin2/ncpdp.cgi')

    # cert configuration
    SCRIPT_CLIENT_CERT = os.environ.get('SCRIPT_CLIENT_CERT', '/opt/app/config/certs/pdmp.crt')
    # private key; keep secret
    SCRIPT_CLIENT_PRIVATE_KEY = os.environ.get('SCRIPT_CLIENT_KEY', '/opt/app/config/certs/pdmp.key')

    SCRIPT_CLIENT_DEA_NUMBER = os.environ.get('SCRIPT_CLIENT_DEA_NUMBER', 'AB1234567')
    # NPI
    SCRIPT_CLIENT_PROVIDER_ID = os.environ.get('SCRIPT_CLIENT_PROVIDER_ID', '1132767439')
    SCRIPT_CLIENT_MUTUALLY_DEFINED = os.environ.get('SCRIPT_CLIENT_MUTUALLY_DEFINED')
    SCRIPT_CLIENT_QUALIFIER = os.environ.get('SCRIPT_CLIENT_QUALIFIER', 'COSRI')

    @classmethod
    def root_path(cls):
        return os.path.dirname(os.path.realpath(__file__))

    @classmethod
    def configure_templates(cls):
        env = Environment(
            loader=PackageLoader('script_facade.client', 'templates'),
            autoescape=select_autoescape(['xml'])
        )
        return env
