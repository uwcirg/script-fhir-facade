from lxml import etree as ET


class MedicationOrder(object):

    def __init__(self, med):
        # todo: support medicationReference and medicationCodeableConcept
        self.medication = med

        self.date_written = None
        self.date_ended = None


    @classmethod
    def from_xml(cls, xml_element):

        drug_description = xml_element.xpath('.//*[local-name()="DrugDescription"]')[0].text

        med_cc = {
            'text': drug_description,
        }

        med_order = cls(med_cc)
        return med_order
    def __str__(self):
        return str(self.as_fhir())

    def as_fhir(self):
        fhir_json = {
            'dateWritten': self.date_written,
            'dateEnded': self.date_ended,
            'medicationCodeableConcept': {
                'coding': [{
                    'system': '',
                    'code': '',
                    'display': self.medication['text'],
                }],
                'text': self.medication['text'],
            }
        }
        return fhir_json


def parse_rx_history_response(xml_string):
    # LXML infers encoding from XML metadata
    root = ET.fromstring(xml_string.encode('utf-8'))

    # todo: use SCRIPT XML namespace correctly
    meds_elements = root.xpath('//*[local-name()="MedicationDispensed"]')

    meds = []
    for med_element in meds_elements:
        meds.append(MedicationOrder.from_xml(med_element))

    return meds
