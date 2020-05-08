# https://www.hl7.org/fhir/terminologies-systems.html
# todo: convert from from National Drug Code to RxNorm
# http://www.nlm.nih.gov/research/umls/rxnorm
# https://rxnav.nlm.nih.gov/REST/rxcui.json?idtype=NDC&id=NDC_ID
drug_code_system_map = {
    # todo: interpolate dashes as necessary for NDC
    'ND': 'http://hl7.org/fhir/sid/ndc'
}

class MedicationOrder(object):

    def __init__(self, med, dispense_request=None, prescriber=None, date_written=None, date_ended=None):
        # todo: support medicationReference and medicationCodeableConcept
        self.medication = med
        self.dispense_request = dispense_request
        self.prescriber = prescriber

        self.date_written = date_written
        self.date_ended = None


    @classmethod
    def from_xml(cls, xml_element):
        # todo: separate finding/extract into separate steps
        drug_description = xml_element.xpath('.//DrugDescription/text()')[0]

        drug_coded = xml_element.xpath('.//DrugCoded')[0]
        product_code = drug_coded.xpath('.//ProductCode/text()')[0]
        product_code_qualifier = drug_coded.xpath('.//ProductCodeQualifier/text()')[0]


        # attempt code system lookup
        product_code_qualifier = drug_code_system_map.get(product_code_qualifier, product_code_qualifier)

        #strength = drug_coded.xpath('.//*[local-name()="Strength"]')[0].text

        date_written = xml_element.xpath('.//WrittenDate/Date/text()')[0]

        med_cc = {
            'medicationCodeableConcept': {
                'coding': [{
                    'system': product_code_qualifier,
                    'code': product_code,
                    'display': drug_description,
                }],
                'text': drug_description,
            }
        }

        quantity_dispensed = xml_element.xpath('.//Quantity/Value/text()')[0]
        dispense_request = {}
        if quantity_dispensed:
            dispense_request = {
                'quantity': {
                    'value': int(quantity_dispensed)
                }
            }

        # todo: move these extensions to a separate MedicationDispense resource
        pharmacy_name = xml_element.xpath('.//Pharmacy/StoreName/text()')[0]
        if pharmacy_name:
            dispense_request.setdefault('extension', [])
            dispense_request['extension'].append(
                {
                    'url': 'http://cosri.org/fhir/pharmacy_name',
                    'valueString': pharmacy_name,
                }
            )

        last_fill = xml_element.xpath('.//LastFillDate/Date/text()')[0]
        if last_fill:
            dispense_request.setdefault('extension', [])
            dispense_request['extension'].append(
                {
                    'url': 'http://cosri.org/fhir/last_fill',
                    'valueDate': last_fill,
                }
            )


        prescriber_fname = xml_element.xpath('.//Prescriber/Name/FirstName/text()')[0]
        prescriber_lname = xml_element.xpath('.//Prescriber/Name/LastName/text()')[0]

        # use contained resource, or save for other resource relationships?
        prescriber = {
            "display": " ".join((prescriber_fname, prescriber_lname))
        }

        med_order = cls(med_cc, dispense_request=dispense_request, prescriber=prescriber, date_written=date_written, date_ended=None)
        return med_order
    def __str__(self):
        return str(self.as_fhir())

    def as_fhir(self):
        fhir_json = {
            'resourceType': 'MedicationOrder',
            'dateWritten': self.date_written,
            'dateEnded': self.date_ended,
            'medicationCodeableConcept': self.medication,
            'dispenseRequest': self.dispense_request,
            'prescriber': self.prescriber,
        }
        filtered_fhir_json = {k:v for k, v in fhir_json.items() if v}
        return filtered_fhir_json
