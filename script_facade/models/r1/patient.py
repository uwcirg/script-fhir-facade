

class Patient(object):

    def __init__(self):
        self.given_name = None
        self.family_name = None


    @classmethod
    def from_xml(cls, xml_element):
        patient = cls()
        patient_fhir = {}

        given_name = xml_element.xpath(
            './/*[local-name()="Name"]/*[local-name()="FirstName"]/text()',
        )
        if given_name:
            patient.given_name = given_name

        return patient


    def __str__(self):
        return str(self.as_fhir())

    def as_fhir(self):
        name = {}
        if self.given_name:
            name['given'] = self.given_name
        if self.family_name:
            name['family'] = self.family_name

        fhir_json = {
            'resourceType': 'Patient',
            'name': name,
        }
        filtered_fhir_json = {k:v for k, v in fhir_json.items() if v}
        return filtered_fhir_json
