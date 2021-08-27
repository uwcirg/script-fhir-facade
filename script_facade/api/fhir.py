from flask import Blueprint, request, current_app
import timeit

from script_facade.client.client import rx_history_query, patient_lookup_query
from script_facade.rxnav.transcode import add_rxnorm_coding


blueprint = Blueprint('fhir', __name__)


def required_search_request_params(req, context):
    """Extract common request parameters for search APIs

    :param req: the live request
    :param context: calling context used in exception text
    :returns: dictionary of required and optional search parameters
    :raises: BadRequest if any required parameters are missing

    """
    patient_fname = req.args.get('subject:Patient.name.given')
    patient_lname = req.args.get('subject:Patient.name.family')
    patient_dob = req.args.get('subject:Patient.birthdate', '').split('eq')[-1]
    dea = req.args.get('dea')

    if not all((patient_fname, patient_lname, patient_dob, dea)):
        current_app.logger.warning(
            "%s search attempted without all required parameters"
            "{fname: %s, lname: %s, dob: %s, dea: %s",
            context, patient_fname, patient_lname, patient_dob, dea)
        return 'Required parameters not given', 400

    return {
        'patient_fname': patient_fname,
        'patient_lname': patient_lname,
        'patient_dob': patient_dob,
        'dea': dea,
        'script_version': req.args.get('script_version')
    }


# todo: version-based routing
# todo: support both types of queries:
# ?subject:Patient.name.given=FIRST_NAME&subject:Patient.name.family=LAST_NAME&subject:Patient.birthdate=eqYYYY-MM-DD
# ?patient=PATIENT_ID
@blueprint.route('/v/<fhir_version>/fhir/MedicationOrder')
def medication_order(fhir_version):
    kwargs = required_search_request_params(request, 'MedicationOrder')
    kwargs['fhir_version'] = fhir_version

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
    kwargs = required_search_request_params(request, 'Patient')
    kwargs['fhir_version'] = fhir_version

    patient_bundle = patient_lookup_query(**kwargs)
    return patient_bundle
