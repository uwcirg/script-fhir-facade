import requests
import requests_cache
from time import time
from flask import Blueprint, jsonify, request, current_app
from flask.json import JSONEncoder

from script_facade.client.client_106 import rx_history_query, patient_lookup_query
from script_facade.rxnav.transcode import add_rxnorm_coding


blueprint = Blueprint('fhir', __name__)


@blueprint.route('/test/<x>')
def test_cache(x):
    iterations = 60
    cache_method = None
    b4 = time()
    if x == 'x':
        cache_method = 'CachedSession'
        session = requests_cache.CachedSession('demo_cache')
        for i in range(iterations):
            session.get('http://httpbin.org/delay/1')
    elif x == 'y':
        cache_method = 'Uncached Session'
        session = requests.Session()
        for i in range(iterations):
            session.get('http://httpbin.org/delay/1')
    elif x == 'z':
        cache_method = 'requests configured cache'
        for i in range(iterations):
            requests.get('http://httpbin.org/delay/1')
    else:
        cache_method = 'requests context manager (no cache exception)'
        with requests_cache.disabled():
            for i in range(iterations):
                requests.get('http://httpbin.org/delay/1')

    return jsonify(cache_method=cache_method, duration=time()-b4)


@blueprint.route('/settings', defaults={'config_key': None})
@blueprint.route('/settings/<string:config_key>')
def config_settings(config_key):
    """Non-secret application settings"""

    # workaround no JSON representation for datetime.timedelta
    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            return str(obj)
    current_app.json_encoder = CustomJSONEncoder

    # return selective keys - not all can be be viewed by users, e.g.secret key
    blacklist = ('SECRET', 'KEY')

    if config_key:
        key = config_key.upper()
        for pattern in blacklist:
            if pattern in key:
                abort(400, f"Configuration key {key} not available")
        return jsonify({key: current_app.config.get(key)})

    config_settings = {}
    for key in current_app.config:
        matches = any(pattern for pattern in blacklist if pattern in key)
        if matches:
            continue
        config_settings[key] = current_app.config.get(key)

    return jsonify(config_settings)


# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?patient=PATIENT_ID
@blueprint.route('/v/<fhir_version>/fhir/MedicationOrder')
def medication_order(fhir_version):
    default_patient_fname = 'Luke'
    default_patient_lname = 'Skywalker'
    default_patient_dob = 'eq1977-01-12'

    patient_fname = request.args.get('subject:Patient.name.given', default_patient_fname)
    patient_lname = request.args.get('subject:Patient.name.family', default_patient_lname)
    patient_dob = request.args.get('subject:Patient.birthdate', default_patient_dob).split('eq')[-1]


    med_order_bundle = rx_history_query(
        patient_fname=patient_fname,
        patient_lname=patient_lname,
        patient_dob=patient_dob,
        fhir_version=fhir_version,
    )

    if current_app.config['RXNAV_LOOKUP_ENABLED']:
        med_order_bundle = add_rxnorm_coding(
            med_order_bundle,
            rxnav_url=current_app.config['RXNAV_URL'],
        )

    return med_order_bundle

# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?subject:Patient.name.given=Luke&subject:Patient.name.family=Skywalker&subject:Patient.birthdate=eq1977-01-12
# ?patient=PATIENT_ID
@blueprint.route('/v/<fhir_version>/fhir/Patient')
def patient_search(fhir_version):
    patient_fname = request.args.get('subject:Patient.name.given')
    patient_lname = request.args.get('subject:Patient.name.family')
    patient_dob = request.args.get('subject:Patient.birthdate', '').split('eq')[-1]

    if not all((patient_fname, patient_lname, patient_dob)):
        return 'Required parameters not given', 400

    patient_bundle = patient_lookup_query(patient_fname, patient_lname, patient_dob)
    return patient_bundle
