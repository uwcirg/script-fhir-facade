from script_facade.client.client_106 import rx_history_query


blueprint = Blueprint('fhir', __name__, url_prefix='/v/r2/fhir/')

# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?patient=PATIENT_ID
@blueprint.route('/MedicationOrder')
def medication_order():
    patient_fname = 'Luke'
    patient_lname = 'Skywalker'
    patient_dob = '1977-01-12'

    bundle = rx_history_query(patient_fname=patient_fname, patient_lname=patient_lname, patient_dob=patient_dob)
    return bundle
