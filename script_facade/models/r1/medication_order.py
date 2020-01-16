from lxml import etree as ET


class MedicationOrder(object):

    def __init__(self, med, date_written=None, date_ended=None):
        # todo: support medicationReference and medicationCodeableConcept
        self.medication = med

        self.date_written = date_written
        self.date_ended = None


    @classmethod
    def from_xml(cls, xml_element):

        drug_description = xml_element.xpath('.//*[local-name()="DrugDescription"]')[0].text

        drug_coded = xml_element.xpath('.//*[local-name()="DrugCoded"]')[0]
        product_code = drug_coded.xpath('.//*[local-name()="ProductCode"]')[0].text
        product_code_qualifier = drug_coded.xpath('.//*[local-name()="ProductCodeQualifier"]')[0].text
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

        med_order = cls(med_cc, date_written=date_written, date_ended=None)
        return med_order
    def __str__(self):
        return str(self.as_fhir())

    def as_fhir(self):
        fhir_json = {
            'dateWritten': self.date_written,
            'dateEnded': self.date_ended,
            'medicationCodeableConcept': self.medication,
        }
        filtered_fhir_json = {k:v for k, v in fhir_json.items() if v}
        return filtered_fhir_json


def parse_rx_history_response(xml_string):
    # LXML infers encoding from XML metadata
    root = ET.fromstring(xml_string.encode('utf-8'))

    # todo: use SCRIPT XML namespace correctly
    meds_elements = root.xpath('//*[local-name()="MedicationDispensed"]')

    meds = []
    for med_element in meds_elements:
        meds.append(MedicationOrder.from_xml(med_element))

    return meds
