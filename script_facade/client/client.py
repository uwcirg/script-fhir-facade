"""Client for NCPDP SCRIPT Standard version 10.6"""
from datetime import datetime

from flask import current_app
from lxml import etree as ET
import requests_cache
import requests
from requests import Request, Session
from werkzeug.exceptions import NotFound

from script_facade.models.r1.bundle import as_bundle
from script_facade.models.r1.medication_order import MedicationOrder
from script_facade.models.r4.medication_request import medication_request_factory, SCRIPT_NAMESPACE
from script_facade.models.r1.patient import Patient
from .config import DefaultConfig as client_config

# data to configure Session
session_data = {
    'cert': (
        # certificate
        client_config.SCRIPT_CLIENT_CERT,
        # private key
        client_config.SCRIPT_CLIENT_PRIVATE_KEY,
    ),
}


def subtract_years(dt, years):
    """Subtract given years from given date, handling leap day gracefully"""
    try:
        dt = dt.replace(year=dt.year-years)
    except ValueError:
        dt = dt.replace(year=dt.year-years, day=dt.day-1)
    return dt


class RxRequest(object):
    def __init__(self, url, DEA, script_version):
        self.url = url
        self.DEA = DEA
        self.script_version = script_version

    def build_request(self, patient_fname, patient_lname, patient_dob):
        req = Request(
            method='POST',
            url=self.url,
            data=self.request_body(patient_fname, patient_lname, patient_dob),
            headers={'Content-Type': 'application/xml'},
        )
        prepped = req.prepare()

        return prepped

    def request_body(self, patient_fname, patient_lname, patient_dob):

        today = datetime.now()
        two_years_ago = subtract_years(dt=today, years=2)

        template_vars = {
            'FromQualifier': client_config.SCRIPT_CLIENT_QUALIFIER,
            'DEA': self.DEA,
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

            'FromQualifier': client_config.SCRIPT_FROM_QUALIFIER,
            'SenderTertiaryIdentification': client_config.SCRIPT_TERTIARY_IDENTIFICATION,

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
            'StartDate': two_years_ago.strftime('%Y-%m-%d'),
            'EndDate': today.strftime('%Y-%m-%d'),
        }
        template_env = client_config.configure_templates()
        template = template_env.get_template(f'request_{self.script_version}.xml')

        xml_content = template.render(**template_vars)

        return xml_content


def parse_rx_history_response(xml_string, fhir_version, script_version):
    # fixup missing colon in XML NS declaration
    xml_string = xml_string.replace('xmlns="http://www.ncpdp.org/schema/SCRIPT"', 'xmlns:SCRIPT="http://www.ncpdp.org/schema/SCRIPT"')
    # LXML infers encoding from XML metadata
    root = ET.fromstring(xml_string.encode('utf-8'))

    # todo: use SCRIPT XML namespace correctly
    meds_elements = root.xpath('//*[local-name()="MedicationDispensed"]')

    med_fhir_version_map = {
        'r1': MedicationOrder,
        'r2': MedicationOrder,
        'r4': medication_request_factory,
    }
    med_parser = med_fhir_version_map[fhir_version]

    meds_fhir = []
    for med_element in meds_elements:
        med_obj = med_parser(
            script_version=script_version,
            source_identifier=client_config.RX_SRC_ID,
        ).from_xml(med_element)

        meds_fhir.append(med_obj.as_fhir())

    return as_bundle(meds_fhir, bundle_type='searchset')


def parse_patient_lookup_query(xml_string, script_version):
    # LXML infers encoding from XML metadata
    try:
        root = ET.fromstring(xml_string.encode('utf-8'))
    except ET.XMLSyntaxError as se:
        current_app.logger.error("Couldn't parse PDMP XML: %s", se)
        raise RuntimeError("Invalid XML returned from PDMP")

    patient_script_version_map = {
        '106': '//script:Patient',
        '20170701': '//HumanPatient',
    }

    patient_elements = root.xpath(patient_script_version_map[script_version], namespaces=SCRIPT_NAMESPACE)

    patients = []
    for patient_element in patient_elements:
        patient = Patient.from_xml(patient_element, ns=SCRIPT_NAMESPACE)
        patients.append(patient.as_fhir())

    if len(patients) == 0:
        # Confirm expected no match code is present.  Otherwise
        # log and raise to avoid masking errors
        codes = root.findall('Body/Error/Code')
        if len(codes) == 1 and codes[0].text == '900':
            nomatch = True
        else:
            current_app.logger.error(
                "no patients; didn't find expected PDMP no-match error code within: %s",
                xml_string)
            raise RuntimeError("Unexpected PDMP response")
    return as_bundle(patients, bundle_type='searchset')


def _mock_pdmp_xml(script_version, patient_fname, patient_lname, patient_dob):
    """Return fixture XML when SCRIPT_MOCK_URL matches, otherwise None."""
    mock_url = client_config.SCRIPT_MOCK_URL
    if not mock_url:
        return None
    mock_base_url = mock_url.replace("github.com", "raw.githubusercontent.com")
    full_url = (
        f"{mock_base_url}/main/{script_version}/"
        f"{patient_fname.lower()}-{patient_lname.lower()}-{patient_dob}.xml"
    )
    with requests_cache.disabled():
        response = requests.get(full_url)
    if response.status_code != 200:
        return None
    return response.text


def _post_pdmp(patient_fname, patient_lname, patient_dob, DEA, script_version):
    """POST an NCPDP SCRIPT request using the configured client certificate."""
    request_builder = RxRequest(
        url=client_config.SCRIPT_ENDPOINT_URL,
        DEA=DEA,
        script_version=script_version,
    )
    request = request_builder.build_request(patient_fname, patient_lname, patient_dob)
    try:
        response = Session().send(request, **session_data)
    except OSError as e:
        current_app.logger.error("Missing PDMP certificates: %s", e)
        raise RuntimeError("Valid PDMP certificates not found")
    response.raise_for_status()
    return response.text


def fetch_pdmp_response(patient_fname, patient_lname, patient_dob, DEA, script_version, log_mock_hit=False):
    """Load PDMP XML from the mock repo or the live endpoint.

    Returns the response body and the SCRIPT version actually used.
    """
    script_version = script_version or client_config.SCRIPT_VERSION
    xml_body = _mock_pdmp_xml(script_version, patient_fname, patient_lname, patient_dob)
    if xml_body and log_mock_hit:
        current_app.logger.debug(
            "found mocked PDMP response for (%s, %s)", patient_lname, patient_fname)

    if not xml_body and client_config.SCRIPT_ENDPOINT_URL:
        xml_body = _post_pdmp(patient_fname, patient_lname, patient_dob, DEA, script_version)

    if not xml_body:
        raise NotFound()
    return xml_body, script_version


def rx_history_query(patient_fname, patient_lname, patient_dob, DEA, fhir_version, script_version):
    xml_body, script_version = fetch_pdmp_response(
        patient_fname, patient_lname, patient_dob, DEA, script_version, log_mock_hit=True)
    return parse_rx_history_response(xml_body, fhir_version, script_version)


def patient_lookup_query(patient_fname, patient_lname, patient_dob, DEA, script_version, fhir_version):
    xml_body, script_version = fetch_pdmp_response(
        patient_fname, patient_lname, patient_dob, DEA, script_version)
    return parse_patient_lookup_query(xml_body, script_version)
