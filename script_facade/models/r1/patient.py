

class Patient(object):

    def __init__(self):
        self.given_name = None
        self.family_name = None
        self.gender = None
        self.birthdate = None
        self.address = None

    @classmethod
    def from_xml(cls, patient_xml):
        """Build a Patient from a SCRIPT Patient xml element object

        :param patient_xml: Patient xml element object

        """
        patient = cls()
        patient_fhir = {}

        # todo: use XML namespaces
        given_name = patient_xml.xpath(
            './/*[local-name()="Name"]/*[local-name()="FirstName"]/text()',
        )
        if given_name:
            patient.given_name = given_name[0]

        family_name = patient_xml.xpath(
            './/*[local-name()="Name"]/*[local-name()="LastName"]/text()',
        )
        if family_name:
            patient.family_name = family_name[0]

        gender = patient_xml.xpath(
            './/*[local-name()="Gender"]/text()',
        )
        if gender:
            gender_map = {'m': 'male', 'f': 'female'}
            patient.gender = gender_map[gender[0].lower()]

        birthdate = patient_xml.xpath(
            './/*[local-name()="DateOfBirth"]/*[local-name()="Date"]/text()',
        )
        if birthdate:
            patient.birthdate = birthdate[0]

        address_line = patient_xml.xpath(
            './/*[local-name()="Address"]/*[local-name()="AddressLine1"]/text()',
        )
        address_city = patient_xml.xpath(
            './/*[local-name()="Address"]/*[local-name()="City"]/text()',
        )
        address_state = patient_xml.xpath(
            './/*[local-name()="Address"]/*[local-name()="State"]/text()',
        )
        address_postal_code = patient_xml.xpath(
            './/*[local-name()="Address"]/*[local-name()="ZipCode"]/text()',
        )
        address = {
            'line': address_line,
            'city': address_city,
            'state': address_state,
            'postalCode': address_postal_code,
        }
        address = {k:v[0] for k, v in address.items() if v}
        patient.address = address

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
            'gender': self.gender,
            'birthDate': self.birthdate,
            'address': self.address,
        }
        filtered_fhir_json = {k:v for k, v in fhir_json.items() if v}
        return filtered_fhir_json
