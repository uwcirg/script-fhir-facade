import os

class DefaultConfig(object):
    # SOAP endpoint URL
    SCRIPT_ENDPOINT_URL = os.environ.get('SCRIPT_ENDPOINT_URL', 'https://uat-onehealthport-api.axwaycloud.com:8099/ncpdp_requests')

    # cert configuration
    SCRIPT_CLIENT_CERT = os.environ.get('SCRIPT_CLIENT_CERT', '/opt/app/config/certs/pdmp.crt')
    # private key; keep secret
    SCRIPT_CLIENT_PRIVATE_KEY = os.environ.get('SCRIPT_CLIENT_KEY', '/opt/app/config/certs/pdmp.key')

    SCRIPT_CLIENT_DEA_NUMBER = os.environ.get('SCRIPT_CLIENT_DEA_NUMBER', 'AB1234567')
    # NPI
    SCRIPT_CLIENT_PROVIDER_ID = os.environ.get('SCRIPT_CLIENT_PROVIDER_ID', '1234567890')
    SCRIPT_CLIENT_MUTUALLY_DEFINED = os.environ.get('SCRIPT_CLIENT_MUTUALLY_DEFINED')
    SCRIPT_CLIENT_QUALIFIER = os.environ.get('SCRIPT_CLIENT_QUALIFIER')

    @classmethod
    def root_path(cls):
        return os.path.dirname(os.path.realpath(__file__))
