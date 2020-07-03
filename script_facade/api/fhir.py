from flask import Blueprint, request, current_app

from script_facade.client.client_106 import rx_history_query, patient_lookup_query
from script_facade.rxnav.transcode import add_rxnorm_coding


blueprint = Blueprint('fhir', __name__)

# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?patient=PATIENT_ID
@blueprint.route('/v/<fhir_version>/fhir/MedicationOrder')
def medication_order(fhir_version):
    default_patient_fname = 'Marc'
    default_patient_lname = 'Jones'
    default_patient_dob = 'eq1961-01-31'

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
