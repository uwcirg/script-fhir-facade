import os
import pytest
from conftest import load_json


@pytest.fixture
def med_order_bundle(datadir):
    return load_json(datadir, 'med_order_bundle.json')


def test_medication_order(client, mocker, med_order_bundle):
    mocker.patch(
        "script_facade.api.fhir.rx_history_query",
        return_value=med_order_bundle)
    response = client.get(
        '/v/v4/fhir/MedicationOrder',
        query_string={
          "subject:Patient.name.given": "Padme",
          "subject:Patient.name.family": "Amidfla",
          "subject:Patient.birthdate": "eq1945-01-15",
          "DEA": "ABC123"
        }
      )
    assert response.status_code == 200


def test_upload_patient(client, datadir):
    file = open(os.path.join(datadir, 'patients.csv'), 'rb')
    data = {'filename': 'patients.csv', 'file': file}
    client.post(
        '/upload/patient/csv',
        content_type='multipart/form-data',
        data=data)
