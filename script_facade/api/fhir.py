import csv
from flask import Blueprint, request, current_app
import io
import timeit

from script_facade.client.client_106 import rx_history_query, patient_lookup_query
from script_facade.rxnav.transcode import add_rxnorm_coding


blueprint = Blueprint('fhir', __name__)


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

    rx_history_start_time = timeit.default_timer()
    med_order_bundle = rx_history_query(
        patient_fname=patient_fname,
        patient_lname=patient_lname,
        patient_dob=patient_dob,
        fhir_version=fhir_version,
    )
    current_app.logger.info("rx_history_query duration %s", timeit.default_timer() - rx_history_start_time)

    rx_nav_start_time = timeit.default_timer()
    if current_app.config['RXNAV_LOOKUP_ENABLED']:
        med_order_bundle = add_rxnorm_coding(
            med_order_bundle,
            rxnav_url=current_app.config['RXNAV_URL'],
        )
    current_app.logger.info("rxnav_lookup duration %s", timeit.default_timer() - rx_nav_start_time)
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


@blueprint.route('/upload/patient/csv', methods=['POST'])
def upload_patient_csv():
    """Given a CSV file (via request.files) upload contents"""

    def decode_file(binary_data):
        """Convert binary file data to file like string buffer

        Flask reads in multipart files as binary, which the csv lib can't
        handle.

        :returns: StringIO buffer of utf-8 decoded strings for file like use
        """
        buffer = io.StringIO()
        last_pos = binary_data.tell()
        while True:
            line = binary_data.readline()
            pos = binary_data.tell()
            if pos == last_pos:
                # Position stops progressing at EOF
                break
            last_pos = pos
            buffer.write(line.decode('utf-8'))

        buffer.seek(0)
        return buffer

    contents = request.files['file']
    csv.register_dialect('generic', skipinitialspace=True)
    reader = csv.DictReader(decode_file(contents), dialect='generic')
    for row in reader:
        if 'provider_last_name' in row:
            # Upsert provider
            pass
