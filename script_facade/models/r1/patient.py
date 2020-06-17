

class Patient(object):

    def __init__(self):
        self.given_name = None
        self.family_name = None
        self.gender = None
        self.birthdate = None
        self.address = None

    @classmethod
    def from_xml(cls, patient_xml, ns=None):
        """Build a Patient from a SCRIPT Patient xml element object

        :param patient_xml: Patient xml element object

        """
        patient = cls()
        patient_fhir = {}

        # todo: use XML namespaces
        given_name = patient_xml.xpath('./script:Name/script:FirstName/text()', namespaces=ns)[0]
        if given_name:
            patient.given_name = given_name

        family_name = patient_xml.xpath('./script:Name/script:LastName/text()', namespaces=ns)[0]
        if family_name:
            patient.family_name = family_name


        gender = patient_xml.xpath('./script:Gender/text()', namespaces=ns)[0]
        if gender:
            gender_map = {'m': 'male', 'f': 'female'}
            patient.gender = gender_map[gender[0].lower()]

        birthdate = patient_xml.xpath('./script:DateOfBirth/script:Date/text()', namespaces=ns)[0]
        if birthdate:
            patient.birthdate = birthdate

        address_line = patient_xml.xpath('./script:Address/script:AddressLine1/text()', namespaces=ns)
        address_city = patient_xml.xpath('./script:Address/script:City/text()', namespaces=ns)
        address_state = patient_xml.xpath('./script:Address/script:State/text()', namespaces=ns)
        address_postal_code = patient_xml.xpath('./script:Address/script:ZipCode/text()', namespaces=ns)

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
