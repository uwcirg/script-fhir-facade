import requests

rxnav_system_map = {
    'NDC': 'http://hl7.org/fhir/sid/ndc',
}


def to_rxnorm(coding):
    base_url = "https://rxnav.nlm.nih.gov"
    reverse_system_map = {v: k for k, v in rxnav_system_map.items()}
    querystring_params = {
        'idtype': reverse_system_map[coding['system']],
        'id': coding['code']
    }
    response = requests.get(
        url=f"{base_url}/REST/rxcui.json",
        params=querystring_params,
    )

    rxnorm_codes = response.json()['idGroup'].get('rxnormId', [])
    if not rxnorm_codes:
        return None

    coding_fhir = {
        'code': rxnorm_codes[0],
        'system': 'http://www.nlm.nih.gov/research/umls/rxnorm',
        'display': coding['display'],
    }
    return coding_fhir


def add_rxnorm_coding(medication_order_bundle):
    for medication_order in medication_order_bundle['entry']:
        medication = medication_order['medicationCodeableConcept']['medicationCodeableConcept']
        rxnorm_codings = []
        for coding in medication['coding']:
            # skip non-NDC codings
            if coding['system'] != 'http://hl7.org/fhir/sid/ndc':
                continue
            rxnorm_coding = to_rxnorm(coding)
            if not rxnorm_coding:
                continue

            if False:
                medication['coding'] = []
            rxnorm_codings.append(rxnorm_coding)

        medication['coding'].extend(rxnorm_codings)


    return medication_order_bundle
