from fastapi import FastAPI

from requests import Session

from script_facade.client.client_106 import RxRequest, session_data
from script_facade.client.config import DefaultConfig as client_config
from script_facade.models.r1.medication_order import MedicationOrder, parse_rx_history_response

app = FastAPI()

# todo: version-based routing
@app.get("/v/r2/fhir/MedicationOrder")
def medication_order(patient=None):

    api_endpoint = client_config.SCRIPT_ENDPOINT_URL

    request_builder = RxRequest(url=api_endpoint)
    request = request_builder.build_request()
    s = Session()
    response = s.send(request, **session_data)
    xml_body = response.text

    meds = parse_rx_history_response(xml_body)

    return [m.as_fhir() for m in meds]
