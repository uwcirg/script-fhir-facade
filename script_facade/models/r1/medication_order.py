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

        drug_description = xml_element.xpath('.//*[local-name()="DrugDescription"]')[0].text

        drug_coded = xml_element.xpath('.//*[local-name()="DrugCoded"]')[0]
        product_code = drug_coded.xpath('.//*[local-name()="ProductCode"]')[0].text
        product_code_qualifier = drug_coded.xpath('.//*[local-name()="ProductCodeQualifier"]')[0].text

        # attempt code system lookup
        product_code_qualifier = drug_code_system_map.get(product_code_qualifier, product_code_qualifier)

        #strength = drug_coded.xpath('.//*[local-name()="Strength"]')[0].text

        date_written = xml_element.xpath('.//*[local-name()="WrittenDate"]//*[local-name()="Date"]')[0].text


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

        quantity_dispensed = xml_element.xpath('.//*[local-name()="Quantity"]//*[local-name()="Value"]')[0].text
        dispense_request = None
        if quantity_dispensed:
            dispense_request = {
                'quantity': {
                    'value': int(quantity_dispensed)
                }
            }


        prescriber_fname = xml_element.xpath('.//*[local-name()="Prescriber"]//*[local-name()="Name"]//*[local-name()="FirstName"]')[0].text
        prescriber_lname = xml_element.xpath('.//*[local-name()="Prescriber"]//*[local-name()="Name"]//*[local-name()="LastName"]')[0].text

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
