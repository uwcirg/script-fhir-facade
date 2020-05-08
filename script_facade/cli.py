import json

from requests import Session

from client.client_106 import RxRequest, session_data, parse_rx_history_response
from client.config import DefaultConfig as client_config


patient_fname = 'Luke'
patient_lname = 'Skywalker'
patient_dob = '1977-01-12'

def main():
    api_endpoint = client_config.SCRIPT_ENDPOINT_URL

    request_builder = RxRequest(url=api_endpoint)
    request = request_builder.build_request(patient_fname, patient_lname, patient_dob)
    s = Session()
    response = s.send(request, **session_data)
    xml_body = response.text

    meds = parse_rx_history_response(xml_body)

    print(json.dumps(meds, indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
