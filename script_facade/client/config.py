import os
from jinja2 import Environment, PackageLoader, select_autoescape

class DefaultConfig(object):
    # System used in MedicationOrder, MedicationRequest identifiers
    RX_SRC_ID = os.getenv("RX_SRC_ID", "https://github.com/uwcirg/script-fhir-facade/")

    # NCPDP SCRIPT version
    SCRIPT_VERSION = os.environ.get('SCRIPT_VERSION', '20170701')

    # SOAP endpoint URL
    SCRIPT_ENDPOINT_URL = os.environ.get('SCRIPT_ENDPOINT_URL', 'https://uat-onehealthport-api.axwaycloud.com:8099/ncpdp_requests')
    # link to repo of mock XML files
    SCRIPT_MOCK_URL = os.environ.get('SCRIPT_MOCK_URL')

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

    @classmethod
    def configure_templates(cls):
        env = Environment(
            loader=PackageLoader('script_facade.client', 'templates'),
            autoescape=select_autoescape(['xml'])
        )
        return env
