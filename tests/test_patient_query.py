import os
import pytest

from script_facade.client.client import parse_patient_lookup_query


@pytest.fixture
def no_results_response(datadir):
    with open(os.path.join(datadir, 'no_results.xml'), 'r') as xml_file:
        data = xml_file.read()
    return data


def test_no_results(no_results_response):
    results = parse_patient_lookup_query(
        xml_string=no_results_response, script_version='20170701')
    assert results['resourceType'] == 'Bundle'
    assert len(results['entry']) == 0


def test_no_results_wo_expected(client, no_results_response):
    # who knows what unexpected to check for - remove the
    # published error on no match and expect a raise
    bogus_results_response = no_results_response.replace(
        '<Code>900</Code>', '<Code>666</Code>')
    with pytest.raises(RuntimeError):
        parse_patient_lookup_query(
            xml_string=bogus_results_response,
            script_version='20170701')
