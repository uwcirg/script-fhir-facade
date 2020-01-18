from fastapi import FastAPI

from requests import Session

from script_facade.client.client_106 import RxRequest, session_data
from script_facade.client.config import DefaultConfig as client_config
from script_facade.models.r1.medication_order import MedicationOrder, parse_rx_history_response

app = FastAPI()

# todo: version-based routing
@app.get("/v/r2/fhir/MedicationOrder")
def medication_order(patient_fname=None, patient_lname=None, patient_dob=None):
    api_endpoint = client_config.SCRIPT_ENDPOINT_URL
    request_builder = RxRequest(url=api_endpoint)

    patient_fname = 'Luke'
    patient_lname = 'Skywalker'
    patient_dob = '1977-01-12'

    request = request_builder.build_request(patient_fname, patient_lname, patient_dob)
    s = Session()
    response = s.send(request, **session_data)

    if not response.ok:
        print(response.content)
    response.raise_for_status()

    xml_body = response.text
    meds = parse_rx_history_response(xml_body)

    # todo use FHIR bundle
    return [m.as_fhir() for m in meds]
