"""SMART Client to query Patient resources"""

import datetime
import requests


def get_pdmp_params(fhir_base_url, patient_id, bearer_token):
    patient_url = "%s/Patient" % fhir_base_url

    response = requests.get(
        patient_url,
        patient=patient_id,
        headers={'Authorization: Bearer %s' % bearer_token}
    )
    patient_fhir = response.json

    patient = {
        'given': patient_fhir['name'][0]['given'],
        'family': patient_fhir['name'][0]['family'],
    }

    birthdate_str = patient_fhir['birthDate']
    if not birthdate_str.endswith('Z'):
        raise ValueError('unsupported timezone')
    # truncate timezone (Z)
    birthdate = datetime.datetime.fromisoformat(birthdate_str[:-1])

    # reformat to PDMP XML
    birthdate_str = birthdate.strftime('%Y-%m-%d')
    patient['birthDate'] = birthdate_str

    return patient
