import pytest

from conftest import MockJsonResponse, load_json
from script_facade.rxnav.transcode import to_rxnorm


@pytest.fixture
def rx_response(datadir):
    return MockJsonResponse(load_json(datadir, 'rx_response.json'))


def test_to_rxnorm(rx_response, mocker):
    coding = {
        'system': 'http://hl7.org/fhir/sid/ndc',
        'code': '0023-6012',
        'display': ''}
    rxnav_url = 'https://rxnav.nlm.nih.gov'

    # Mock to avoid round-trip to nlm.nih.gov
    mocker.patch('requests.get', return_value=rx_response)

    result = to_rxnorm(coding, rxnav_url)

    assert result['code'] == '892598'
    assert result['system'] == 'http://www.nlm.nih.gov/research/umls/rxnorm'
