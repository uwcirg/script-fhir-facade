from requests import Session
from lxml import etree as ET

from client.client_106 import RxRequest, session_data
from client.config import DefaultConfig as client_config

from models.r1.medication_order import MedicationOrder, parse_rx_history_response

def main():
    api_endpoint = client_config.SCRIPT_ENDPOINT_URL

    request_builder = RxRequest(url=api_endpoint)
    request = request_builder.build_request()
    s = Session()
    response = s.send(request, **session_data)
    xml_body = response.text

    meds = parse_rx_history_response(xml_body)

    print(*meds, sep='\n')

if __name__ == "__main__":
    main()
