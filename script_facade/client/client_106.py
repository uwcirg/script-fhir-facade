"""Client for NCPDP SCRIPT Standard version 10.6"""
import os
from lxml import etree as ET
from requests import Request, Session

from script_facade.models.r1.bundle import as_bundle
from script_facade.models.r1.medication_order import MedicationOrder
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

class RxRequest(object):
    def __init__(self, url):
        self.url = url

    def build_request(self, patient_fname, patient_lname, patient_dob):
        req = Request(
            method='GET',
            url=self.url,
            data=self.request_body(patient_fname, patient_lname, patient_dob),
            headers={'Content-Type': 'application/xml'},
        )
        prepped = req.prepare()

        return prepped

    def request_body(self, patient_fname, patient_lname, patient_dob):


        template_vars = {
            'FromQualifier': client_config.SCRIPT_CLIENT_QUALIFIER,
            #'DEA': client_config.SCRIPT_CLIENT_DEA_NUMBER,
            'NPI': client_config.SCRIPT_CLIENT_PROVIDER_ID,
            #'MutuallyDefined': client_config.SCRIPT_CLIENT_MUTUALLY_DEFINED,
            #'Specialty': '207R00000X',
            #'ClinicName': 'Fake Clinic Name',
            'PrescriberLName': 'Prescriber',
            'PrescriberFName': 'HID Test',

            #'PrescriberAddress1': '555 North Way',
            #'PrescriberAddress2': 'Building 101',
            #'PrescriberCity': 'Anytown',
            #'PrescriberState': 'WA',
            #'PrescriberZip': '99999',
            #'PrescriberPlaceLoc': 'AD2',

            #'ComNumber': '1234567890',
            #'ComQualifier': 'TE',

            #'PatientLName': 'Skywalker',
            'PatientLName': patient_lname,
            'PatientFName': patient_fname,
            'PatientGender': 'M',
            'PatientDOB': patient_dob,
            'BenEffectiveDate': '2012-01-01',
            'BenExpirationDate': '2019-12-11',
            'BenConsent': 'Y',
        }
        template_env = client_config.configure_templates()
        template = template_env.get_template('request_106.xml')
        xml_content = template.render(**template_vars)

        return xml_content


def parse_rx_history_response(xml_string):
    # LXML infers encoding from XML metadata
    root = ET.fromstring(xml_string.encode('utf-8'))

    # todo: use SCRIPT XML namespace correctly
    meds_elements = root.xpath('//*[local-name()="MedicationDispensed"]')

    meds = []
    for med_element in meds_elements:
        meds.append(MedicationOrder.from_xml(med_element))

    meds = [m.as_fhir() for m in meds]
    return as_bundle(meds, bundle_type='searchset')


def rx_history_query(patient_fname, patient_lname, patient_dob):
    api_endpoint = client_config.SCRIPT_ENDPOINT_URL
    request_builder = RxRequest(url=api_endpoint)
    request = request_builder.build_request(patient_fname, patient_lname, patient_dob)
    s = Session()
    response = s.send(request, **session_data)

    if not response.ok:
        print(response.content)
    response.raise_for_status()

    xml_body = response.text

    meds = parse_rx_history_response(xml_body)
    return meds
