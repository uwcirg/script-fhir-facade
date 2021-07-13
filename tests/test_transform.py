import pytest
from lxml import etree as ET

from script_facade.models.r4.medication_request import medication_request_factory
from conftest import load_xml


@pytest.fixture
def rxhistory_response_20170701(datadir):
    return load_xml(datadir, 'rxhistory-response.20170701.xml')


def test_script_20170701(rxhistory_response_20170701):
    "Test FHIR object generation from MedicationDispensed XML element"

    # TODO move to fixture
    root = ET.fromstring(rxhistory_response_20170701.encode('utf-8'))
    med_dispensed_elements = root.xpath('//*[local-name()="MedicationDispensed"]')

    parser = medication_request_factory("20170701", source_identifier='https://test.org/script-facade')
    med = parser.from_xml(med_dispensed=med_dispensed_elements[2])
    med_fhir = med.as_fhir()

    assert med_fhir['resourceType'] == 'MedicationRequest'
    assert med_fhir['authoredOn'] == '2020-04-18'
    assert med_fhir['requester']['display'] == 'RICHARD SCHAFFER'

    assert med_fhir['dispenseRequest']['expectedSupplyDuration'] == {
        'code': 'd',
        'system': 'http://unitsofmeasure.org',
        'unit': 'days',
        'value': 12.0,
    }
    assert med_fhir['dispenseRequest']['quantity']['value'] == 11.0

    assert med_fhir['medicationCodeableConcept']['text'] == 'TRAMADOL HCL ER 200 MG TABLET'
    ndc_coding = {
        'code': '68180069806',
        'display': 'TRAMADOL HCL ER 200 MG TABLET',
        'system': 'http://hl7.org/fhir/sid/ndc'
    }
    assert ndc_coding in med_fhir['medicationCodeableConcept']['coding']

    pharmacy_name_ext = {
        'url': 'http://cosri.org/fhir/pharmacy_name',
        'valueString': 'KMART OPERATIONS LLC',
    }
    assert pharmacy_name_ext in med_fhir['dispenseRequest']['extension']

    last_fill_ext = {'url': 'http://cosri.org/fhir/last_fill', 'valueDate': '2020-04-21'}
    assert last_fill_ext in med_fhir['dispenseRequest']['extension']

    facade_id = {'system': 'https://test.org/script-facade'}
    assert facade_id in med_fhir['identifier']


@pytest.fixture
def rxhistory_response_106(datadir):
    return load_xml(datadir, 'rxhistory-response.106.xml')


def test_script_106(rxhistory_response_106):
    "Test FHIR object generation from MedicationDispensed XML element"

    # TODO move to fixture
    root = ET.fromstring(rxhistory_response_106.encode('utf-8'))
    med_dispensed_elements = root.xpath('//*[local-name()="MedicationDispensed"]')

    parser = medication_request_factory("106", source_identifier='https://test.org/script-facade')

    med = parser.from_xml(med_dispensed=med_dispensed_elements[2])
    med_fhir = med.as_fhir()

    assert med_fhir['resourceType'] == 'MedicationRequest'
    assert med_fhir['authoredOn'] == '2018-09-19'
    assert med_fhir['requester']['display'] == 'TEST PRESCRIBER'

    assert med_fhir['dispenseRequest']['expectedSupplyDuration'] == {
        'code': 'd',
        'system': 'http://unitsofmeasure.org',
        'unit': 'days',
        'value': 10.0,
    }
    assert med_fhir['dispenseRequest']['quantity']['value'] == 10.0

    assert med_fhir['medicationCodeableConcept']['text'] == 'ZOLPIDEM TARTRATE 10 MG TABLET'
    ndc_coding = {
        'code': '16714062202',
        'display': 'ZOLPIDEM TARTRATE 10 MG TABLET',
        'system': 'http://hl7.org/fhir/sid/ndc'
    }
    assert ndc_coding in med_fhir['medicationCodeableConcept']['coding']

    pharmacy_name_ext = {
        'url': 'http://cosri.org/fhir/pharmacy_name',
        'valueString': 'TEST, DOCTOR',
    }
    assert pharmacy_name_ext in med_fhir['dispenseRequest']['extension']

    last_fill_ext = {'url': 'http://cosri.org/fhir/last_fill', 'valueDate': '2018-09-19'}
    assert last_fill_ext in med_fhir['dispenseRequest']['extension']

    facade_id = {'system': 'https://test.org/script-facade'}
    assert facade_id in med_fhir['identifier']
