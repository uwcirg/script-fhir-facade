"""Client for NCPDP SCRIPT Standard version 10.6"""

import os

from requests import Request
from .config import DefaultConfig as client_config

# data to confgure Session
session_data = {
    'cert': (
        # certificate
        client_config.SCRIPT_CLIENT_CERT,
        # private key
        client_config.SCRIPT_CLIENT_PRIVATE_KEY,
    ),
}

class RxRequest():
    def __init__(self, url):
        self.url = url

    def build_request(self):
        req = Request(
            method='GET',
            url=self.url,
            data=self.request_body(),
            headers={'Content-Type': 'application/xml'},
        )
        prepped = req.prepare()

        return prepped

    def request_body(self):


        template_vars = {
            'FromQualifier': client_config.SCRIPT_CLIENT_QUALIFIER,
            'DEA': client_config.SCRIPT_CLIENT_DEA_NUMBER,
            'NPI': client_config.SCRIPT_CLIENT_PROVIDER_ID,
            'MutuallyDefined': client_config.SCRIPT_CLIENT_MUTUALLY_DEFINED,
            'Specialty': '207R00000X',
            'ClinicName': 'Fake Clinic Name',
            'PrescriberLName': 'Prescriber',
            'PrescriberFName': 'HID Test',
            'PrescriberAddress1': '555 North Way',
            'PrescriberAddress2': 'Building 101',
            'PrescriberCity': 'Anytown',
            'PrescriberState': 'WA',
            'PrescriberZip': '99999',
            'PrescriberPlaceLoc': 'AD2',

            'ComNumber': '1234567890',
            'ComQualifier': 'TE',
            'PatientLName': 'Skywalker',
            'PatientFName': 'Luke',
            'PatientGender': 'M',
            'PatientDOB': '1977-01-12',
            'BenEffectiveDate': '2012-01-01',
            'BenExpirationDate': '2019-12-11',
            'BenConsent': 'Y',
        }
        template_env = client_config.configure_templates()
        template = template_env.get_template('request_106.xml')
        xml_content = template.render(**template_vars)

        return xml_content
