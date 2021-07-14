# https://www.hl7.org/fhir/terminologies-systems.html
drug_code_system_map = {
    # todo: interpolate dashes as necessary for NDC
    'ND': 'http://hl7.org/fhir/sid/ndc'
}

SCRIPT_NAMESPACE = {'script': 'http://www.ncpdp.org/schema/SCRIPT'}


def medication_request_factory(script_version, source_identifier):
    """Factory method to return versioned MedicationRequest instance"""
    if script_version == '106':
        return MedicationRequest106(source_identifier, xml_namespaces=SCRIPT_NAMESPACE)
    elif script_version == '20170701':
        return MedicationRequest20170701(source_identifier)
    else:
        raise ValueError(f"unsupported script_version: f{script_version}")


class MedicationRequest(object):
    """Base class for MedicationRequest version implementations"""

    # XPath query templates
    written_data_query = './/{self.ns_prefix}WrittenDate/{self.ns_prefix}Date/text()'
    drug_description_query = './/{self.ns_prefix}DrugDescription/text()'
    drug_coded_query = './/{self.ns_prefix}DrugCoded'
    quantity_dispensed_query = './/{self.ns_prefix}Quantity/{self.ns_prefix}Value/text()'
    expected_supply_duration_query = './/{self.ns_prefix}DaysSupply/text()'
    last_fill_query = './/{self.ns_prefix}LastFillDate/{self.ns_prefix}Date/text()'

    prescriber_fname_query = './/{self.ns_prefix}Name/{self.ns_prefix}FirstName/text()'
    prescriber_lname_query = './/{self.ns_prefix}Name/{self.ns_prefix}LastName/text()'

    def __init__(self, source_identifier, xml_namespaces=None):
        # required attribute
        # https://hl7.org/fhir/R4/medicationrequest-definitions.html#MedicationRequest.medication_x_
        self.medication = None

        self.authored_on = None
        self.dispense_request = None
        self.requester = None
        self.source_identifier = source_identifier

        self.xml_namespaces = xml_namespaces
        self.ns_prefix = next(iter(xml_namespaces.keys())) + ":" if xml_namespaces else ""

    def authored_on_from_xml(self, med_dispensed):
        authored_on = med_dispensed.xpath(
            _path=self.written_data_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]
        self.authored_on = authored_on
        return authored_on

    def med_cc_from_xml(self, med_dispensed):
        drug_description = med_dispensed.xpath(
            _path=self.drug_description_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        drug_coded = med_dispensed.xpath(
            _path=self.drug_coded_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        product_code = drug_coded.xpath(
            _path=self.product_code_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        product_code_qualifier = drug_coded.xpath(
            _path=self.product_code_qualifier_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        # attempt code system lookup
        product_code_qualifier = drug_code_system_map.get(product_code_qualifier, product_code_qualifier)

        # element no longer present in OHP PDMP response
        #strength = drug_coded.xpath('.//*[local-name()="Strength"]')[0].text

        med_cc = {
            'coding': [{
                'system': product_code_qualifier,
                'code': product_code,
                'display': drug_description,
            }],
            'text': drug_description,
        }
        self.medication = med_cc
        return med_cc

    def requester_from_xml(self, med_dispensed):
        prescriber = med_dispensed.xpath(
            _path=self.prescriber_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        prescriber_fname = prescriber.xpath(
            _path=self.prescriber_fname_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        prescriber_lname = prescriber.xpath(
            _path=self.prescriber_lname_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]

        # use contained resource, or save for other resource relationships?
        requester = {"display": " ".join((prescriber_fname, prescriber_lname))}
        self.requester = requester
        return requester

    def dispense_request_from_xml(self, med_dispensed):
        dispense_request = {}

        quantity_dispensed = med_dispensed.xpath(
            _path=self.quantity_dispensed_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]
        if quantity_dispensed:
            dispense_request.setdefault(
                'quantity',
                {'value': float(quantity_dispensed)},
            )

        expected_supply_duration = med_dispensed.xpath(
            _path=self.expected_supply_duration_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]
        if expected_supply_duration:
            dispense_request.setdefault(
                'expectedSupplyDuration',
                {
                    'value': float(expected_supply_duration),
                    'unit': 'days',
                    'system': 'http://unitsofmeasure.org',
                    'code': 'd',
                },
            )

        # todo: move these extensions to a separate MedicationDispense resource
        pharmacy_name = med_dispensed.xpath(
            _path=self.pharmacy_name_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]
        if pharmacy_name:
            dispense_request.setdefault('extension', [])
            dispense_request['extension'].append(
                {
                    'url': 'http://cosri.org/fhir/pharmacy_name',
                    'valueString': pharmacy_name,
                }
            )

        last_fill = med_dispensed.xpath(
            _path=self.last_fill_query.format(self=self),
            namespaces=self.xml_namespaces
        )[0]
        if last_fill:
            dispense_request.setdefault('extension', [])
            dispense_request['extension'].append(
                {
                    'url': 'http://cosri.org/fhir/last_fill',
                    'valueDate': last_fill,
                }
            )
        self.dispense_request = dispense_request
        return dispense_request

    def __str__(self):
        return str(self.as_fhir())

    def as_fhir(self):
        fhir_json = {
            'resourceType': 'MedicationRequest',
            'identifier': [{'system': self.source_identifier}],
            'authoredOn': self.authored_on,
            'medicationCodeableConcept': self.medication,
            'dispenseRequest': self.dispense_request,
            'requester': self.requester,
        }
        # filter out unset attributes
        filtered_fhir_json = {k:v for k, v in fhir_json.items() if v}
        return filtered_fhir_json

    def from_xml(self, med_dispensed):
        self.med_cc_from_xml(med_dispensed)
        self.requester_from_xml(med_dispensed)
        self.dispense_request_from_xml(med_dispensed)
        self.authored_on_from_xml(med_dispensed)
        return self


class MedicationRequest106(MedicationRequest):
    """Derivation for version 106 MedicationRequest parsing """

    # Define unique XPath query templates for version 106
    product_code_query = './/{self.ns_prefix}ProductCode/text()'
    product_code_qualifier_query = './/{self.ns_prefix}ProductCodeQualifier/text()'
    prescriber_query = './/{self.ns_prefix}Prescriber'
    pharmacy_name_query = './/{self.ns_prefix}Pharmacy/{self.ns_prefix}StoreName/text()'


class MedicationRequest20170701(MedicationRequest):
    """Derivation for version 20170701 MedicationRequest parsing """

    # Define unique XPath query templates for version 20170701
    product_code_query = './/ProductCode/Code/text()'
    product_code_qualifier_query = './/ProductCode/Qualifier/text()'
    prescriber_query = './/Prescriber/NonVeterinarian'
    pharmacy_name_query = './/Pharmacy/BusinessName/text()'
