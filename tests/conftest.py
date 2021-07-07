import json
import os
import pytest
from script_facade.app import create_app

SECRET = 'nonsense-testing-key'


def load_json(datadir, filename):
    with open(os.path.join(datadir, filename), 'r') as json_file:
        data = json.load(json_file)
    return data


def load_xml(datadir, filename):
    with open(os.path.join(datadir, filename), 'r') as xml_file:
        data = xml_file.read()
    return data


class MockJsonResponse:
    """Given data, present behind `json()` attribute"""
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


@pytest.fixture()
def app():
    return create_app(testing=True)
