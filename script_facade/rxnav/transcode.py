import requests


rxnav_system_map = {
    'NDC': 'http://hl7.org/fhir/sid/ndc',
    'rxnorm': 'http://www.nlm.nih.gov/research/umls/rxnorm',
}

def to_rxnorm(coding, rxnav_url):
    """Return first RxNorm coding to given NDC coding"""
    reverse_system_map = {v: k for k, v in rxnav_system_map.items()}
    querystring_params = {
        'idtype': reverse_system_map[coding['system']],
        'id': coding['code']
    }
    response = requests.get(
        url=f"{rxnav_url}/REST/rxcui.json",
        params=querystring_params,
    )

    rxnorm_codes = response.json()['idGroup'].get('rxnormId', [])
    if not rxnorm_codes:
        return None

    coding_fhir = {
        'code': rxnorm_codes[0],
        'system': rxnav_system_map['rxnorm'],
        'display': coding['display'],
    }
    return coding_fhir


def add_rxnorm_coding(medication_order_bundle, rxnav_url):
    """Add rxnorm codings to each MedicationOrder in given FHIR bundle"""
    for medication_order in medication_order_bundle['entry']:
        # todo: fixup extra medicationCodeableConcept nesting in FHIR
        medication = medication_order['medicationCodeableConcept']['medicationCodeableConcept']
        rxnorm_codings = []
        for coding in medication['coding']:
            # skip non-NDC codings
            if coding['system'] != rxnav_system_map['NDC']:
                continue
            rxnorm_coding = to_rxnorm(coding, rxnav_url)
            if not rxnorm_coding:
                continue

            rxnorm_codings.append(rxnorm_coding)
        medication['coding'].extend(rxnorm_codings)

    return medication_order_bundle
