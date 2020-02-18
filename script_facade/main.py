from fastapi import FastAPI


from script_facade.client.client_106 import rx_history_query
from script_facade.client.config import DefaultConfig as client_config
#from script_facade.models.r1.medication_order import MedicationOrder, parse_rx_history_response

app = FastAPI()
# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?patient=PATIENT_ID
@app.get("/v/r2/fhir/MedicationOrder")
def medication_order(patient=None, patient_fname=None, patient_dob=None):

    patient_fname = 'Terry'
    patient_lname = 'Jackson'
    patient_dob = '7/1/1968'

    bundle = rx_history_query(patient_fname=patient_fname, patient_lname=patient_lname, patient_dob=patient_dob)
    return bundle
