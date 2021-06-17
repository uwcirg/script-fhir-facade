# https://www.hl7.org/fhir/terminologies-systems.html
drug_code_system_map = {
    # todo: interpolate dashes as necessary for NDC
    'ND': 'http://hl7.org/fhir/sid/ndc'
}

class MedicationRequest(object):
    def __init__(self):
        # required attribute
        # https://hl7.org/fhir/R4/medicationrequest-definitions.html#MedicationRequest.medication_x_
        self.medication = None

        self.authored_on = None
        self.dispense_request = None
        self.requester = None
        self.source_identifier = None

    @classmethod
    def from_xml(cls, med_dispensed, source_identifier, script_version):
        """Build a MedicationRequest from a MedicationDispensed xml element object

        :param med_dispensed: MedicationDispensed xml element object

        """

        if script_version == "106":
            med_request = cls.from_106_xml(med_dispensed, source_identifier)
        elif script_version == "20170701":
            med_request = cls.from_20170701_xml(med_dispensed, source_identifier)
        else:
            # TODO raise exception
            pass

        return med_request

    @classmethod
    def from_20170701_xml(cls, med_dispensed, source_identifier):
        med_request = cls()

        return med_request


    @classmethod
    def from_106_xml(cls, med_dispensed, source_identifier):
        med_order = cls()
        med_order.source_identifier = source_identifier

        # todo: separate finding/extract into separate steps
        drug_description = med_dispensed.xpath('.//DrugDescription/text()')[0]


        drug_coded = med_dispensed.xpath('.//DrugCoded')[0]
        product_code = drug_coded.xpath('.//ProductCode/text()')[0]
        product_code_qualifier = drug_coded.xpath('.//ProductCodeQualifier/text()')[0]


        # attempt code system lookup
        product_code_qualifier = drug_code_system_map.get(product_code_qualifier, product_code_qualifier)

        # element no longer present in OHP PDMP response
        #strength = drug_coded.xpath('.//*[local-name()="Strength"]')[0].text


        med_order.authored_on = med_dispensed.xpath('.//WrittenDate/Date/text()')[0]
        med_cc = {
            'coding': [{
                'system': product_code_qualifier,
                'code': product_code,
                'display': drug_description,
            }],
            'text': drug_description,
        }

        med_order.medication = med_cc

        prescriber_fname = med_dispensed.xpath('.//Prescriber/Name/FirstName/text()')[0]
        prescriber_lname = med_dispensed.xpath('.//Prescriber/Name/LastName/text()')[0]
        # use contained resource, or save for other resource relationships?
        requester = {
            "display": " ".join((prescriber_fname, prescriber_lname))
        }
        med_order.requester = requester

        dispense_request = {}
        quantity_dispensed = med_dispensed.xpath('.//Quantity/Value/text()')[0]
        if quantity_dispensed:
            dispense_request.setdefault(
                'quantity',
                {'value': float(quantity_dispensed)},
            )
        expected_supply_duration = med_dispensed.xpath('.//DaysSupply/text()')[0]
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
        med_order.dispense_request = dispense_request

        # todo: move these extensions to a separate MedicationDispense resource
        pharmacy_name = med_dispensed.xpath('.//Pharmacy/StoreName/text()')[0]
        if pharmacy_name:
            dispense_request.setdefault('extension', [])
            dispense_request['extension'].append(
                {
                    'url': 'http://cosri.org/fhir/pharmacy_name',
                    'valueString': pharmacy_name,
                }
            )

        last_fill = med_dispensed.xpath('.//LastFillDate/Date/text()')[0]
        if last_fill:
            dispense_request.setdefault('extension', [])
            dispense_request['extension'].append(
                {
                    'url': 'http://cosri.org/fhir/last_fill',
                    'valueDate': last_fill,
                }
            )
        return med_order

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
