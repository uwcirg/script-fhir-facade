from requests import Session

from client.client_106 import RxRequest, session_data
from client.config import DefaultConfig as client_config


def main():
    api_endpoint = client_config.SCRIPT_ENDPOINT_URL

    request_builder = RxRequest(url=api_endpoint)
    request = request_builder.build_request()

    s = Session()
    response = s.send(request, **session_data)
    xml_body = response.text

    print(xml_body)

if __name__ == "__main__":
    main()
