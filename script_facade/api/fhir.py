import csv
from flask import Blueprint, request, current_app
import io
import timeit

from script_facade.client.client import rx_history_query, patient_lookup_query
from script_facade.jsonify_abort import jsonify_abort
from script_facade.rxnav.transcode import add_rxnorm_coding


blueprint = Blueprint('fhir', __name__)


def required_search_request_params(req, fhir_version, context):
    """Extract common request parameters for search APIs

    :param req: the live request
    :param context: calling context used in exception text
    :returns: dictionary of required and optional search parameters
    :raises: ValueError if any required parameters are missing

    """
    patient_fname = req.args.get('subject:Patient.name.given')
    patient_lname = req.args.get('subject:Patient.name.family')
    patient_dob = req.args.get('subject:Patient.birthdate', '').split('eq')[-1]
    DEA = req.args.get('DEA')

    if not all((patient_fname, patient_lname, patient_dob, DEA)):
        current_app.logger.warning(
            "%s search attempted without all required parameters"
            "{fname: %s, lname: %s, dob: %s, DEA: %s}",
            context, patient_fname, patient_lname, patient_dob, DEA)
        raise ValueError('Required parameters not given')

    return {
        'patient_fname': patient_fname,
        'patient_lname': patient_lname,
        'patient_dob': patient_dob,
        'DEA': DEA,
        'fhir_version': fhir_version,
        'script_version': req.args.get('script_version')
    }


def audit_entry(context, tags, **kwargs):
    message = (
        f"{context} lookup: ({kwargs['patient_fname']} {kwargs['patient_lname']}"
        f" -- {kwargs['patient_dob']})")
    current_app.logger.info(message, extra={'tags': tags, 'user': kwargs['DEA']})


# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?patient=PATIENT_ID
@blueprint.route('/v/<fhir_version>/fhir/MedicationOrder')
def medication_order(fhir_version):
    try:
        kwargs = required_search_request_params(request, fhir_version, 'MedicationOrder')
    except ValueError as error:
        return jsonify_abort(message=str(error), status_code=400)

    audit_entry(context='MedicationOrder', tags=['PDMP', 'search'], **kwargs)
    rx_history_start_time = timeit.default_timer()
    med_order_bundle = rx_history_query(**kwargs)
    current_app.logger.debug(
        "rx_history_query duration %s", timeit.default_timer() - rx_history_start_time)

    if current_app.config['RXNAV_LOOKUP_ENABLED']:
        rx_nav_start_time = timeit.default_timer()
        med_order_bundle = add_rxnorm_coding(
            med_order_bundle,
            rxnav_url=current_app.config['RXNAV_URL'],
        )
        current_app.logger.debug(
            "rxnav_lookup duration %s", timeit.default_timer() - rx_nav_start_time)
    return med_order_bundle


# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?subject:Patient.name.given=Luke&subject:Patient.name.family=Skywalker&subject:Patient.birthdate=eq1977-01-12
# ?patient=PATIENT_ID
@blueprint.route('/v/<fhir_version>/fhir/Patient')
def patient_search(fhir_version):
    try:
        kwargs = required_search_request_params(request, fhir_version, 'Patient')
    except ValueError as error:
        return jsonify_abort(message=str(error), status_code=400)

    audit_entry(context='Patient', tags=['PDMP', 'search'], **kwargs)
    try:
        patient_bundle = patient_lookup_query(**kwargs)
    except RuntimeError as error:
        return jsonify_abort(status_code=400, message=str(error))
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
