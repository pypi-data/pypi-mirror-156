import logging
import os
import re

from OTLMOW.ModelGenerator.StringHelper import wrap_in_quotes


class OEFClassCreator:
    def __init__(self, attributen: [dict]):
        logging.info("Created an instance of OEFClassCreator")
        self.attributen = attributen

    def create_block_to_write_from_class(self, oef_class: dict):
        if not isinstance(oef_class, dict):
            raise ValueError(f"Input is not a oef_class dict")

        if oef_class['uri'] == '' or not (
                oef_class['uri'].startswith('https://lgc.data.wegenenverkeer.be/ns/installatie#')):
            raise ValueError(f"oef_class[uri] is invalid. Value = '{oef_class['uri']}'")

        if oef_class['naam'] == '':
            raise ValueError(f"oef_class[naam] is invalid. Value = '{oef_class['naam']}'")

        if oef_class['naam'] == 'AID':
            pass

        return self._create_block_to_write_from_class(oef_class)

    def _create_block_to_write_from_class(self, oef_class: dict):
        attributen = self.find_attributes_by_class(oef_class)

        datablock = ['# coding=utf-8', 'from OTLMOW.OEFModel.EMObject import EMObject']

        if len(attributen) > 0:
            datablock.append('from OTLMOW.OEFModel.EMAttribuut import EMAttribuut')

        list_of_fields = self.get_fields_to_import_from_list_of_attributes(attributen)
        for type_field in list_of_fields:
            datablock.append(f'from OTLMOW.OTLModel.Datatypes.{type_field} import {type_field}')

        datablock.append('')
        datablock.append('')
        datablock.append(f'# Generated with {self.__class__.__name__}. To modify: extend, do not edit')

        datablock.append(f'class {oef_class["naam"]}(EMObject):')
        datablock.append(f'    """{oef_class["definitie"]}"""')
        datablock.append('')
        datablock.append(f"    typeURI = '{oef_class['uri']}'")
        datablock.append(f"    label = '{oef_class['label']}'")
        datablock.append('')
        datablock.append('    def __init__(self):')
        datablock.append('        super().__init__()')
        datablock.append('')

        self.add_attributen_to_datablock(attributen, datablock)

        return datablock

    def find_attributes_by_class(self, oef_class):
        attributenlijst = list(map(lambda a: a['attribuut'], oef_class['attributen']))
        attributenlijst = list(
            filter(lambda a: not a.startswith('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#'),
                   attributenlijst))
        return list(filter(lambda x: x['uri'] in attributenlijst, self.attributen))

    def get_field_from_datatype(self, datatype: str) -> str:
        substitute_lijst = {
            'http://www.w3.org/2001/XMLSchema#decimal': 'FloatOrDecimalField',
            'http://www.w3.org/2001/XMLSchema#boolean': 'BooleanField',
            'http://www.w3.org/2001/XMLSchema#string': 'StringField',
            'http://www.w3.org/2001/XMLSchema#integer': 'IntegerField',
            'http://www.w3.org/2001/XMLSchema#date': 'DateField',
            'http://www.w3.org/2001/XMLSchema#dateTime': 'DateTimeField'
        }
        return substitute_lijst.get(datatype)

    def get_fields_to_import_from_list_of_attributes(self, attributen):
        field_lijst = list(set(map(lambda a: a['dataType'], attributen)))
        unsorted = list(sorted(map(self.get_field_from_datatype, field_lijst)))
        return unsorted

    @staticmethod
    def getWhiteSpaceEquivalent(string):
        return ''.join(' ' * len(string))

    def add_attributen_to_datablock(self, attributen, datablock):
        prop_datablock = []
        for attribuut in sorted(attributen, key=lambda a: a['naam']):
            verkorte_uri = attribuut["uri"].replace('https://lgc.data.wegenenverkeer.be/ns/attribuut#', ''). \
                replace('https://ond.data.wegenenverkeer.be/ns/attribuut#', ''). \
                replace('https://ins.data.wegenenverkeer.be/ns/attribuut#', '')
            verkorte_uri = verkorte_uri.split('.')[1]

            if re.search("^\d", verkorte_uri) is not None:
                continue

            whitespace = self.getWhiteSpaceEquivalent(f'        self._{verkorte_uri} = EMAttribuut(')
            fieldName = self.get_field_from_datatype(attribuut['dataType'])

            datablock.append(f'        self._{verkorte_uri} = EMAttribuut(field={fieldName},')
            datablock.append(f'{whitespace}naam={wrap_in_quotes(attribuut["naam"])},')
            datablock.append(f'{whitespace}label={wrap_in_quotes(attribuut["label"])},')
            datablock.append(f'{whitespace}objectUri={wrap_in_quotes(attribuut["uri"])},')
            if attribuut["kardinaliteit"] != '1..1':
                datablock.append(f'{whitespace}kardinaliteit={wrap_in_quotes(attribuut["kardinaliteit"])},')
            definitie_zonder_quotes = attribuut["definitie"].replace("\'", "\\\'").replace("\n", ' ')
            datablock.append(f'{whitespace}definitie={wrap_in_quotes(definitie_zonder_quotes)},')
            datablock.append(f'{whitespace}owner=self)')

            datablock.append('')

            prop_datablock.append(f'    @property'),
            prop_datablock.append(f'    def {verkorte_uri}(self):'),

            prop_datablock.append(f'        """{definitie_zonder_quotes}"""'),
            prop_datablock.append(f'        return self._{verkorte_uri}.waarde'),
            prop_datablock.append(f''),
            prop_datablock.append(f'    @{verkorte_uri}.setter'),
            prop_datablock.append(f'    def {verkorte_uri}(self, value):'),
            prop_datablock.append(f'        self._{verkorte_uri}.set_waarde(value, owner=self)'),
            prop_datablock.append(f'')

        for prop_line in prop_datablock:
            datablock.append(prop_line)

        return datablock

    @staticmethod
    def writeToFile(cls, dataToWrite: list[str], relativePath=''):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        path = f"{base_dir}/../OEFModel/Classes/{cls['naam']}.py"

        with open(path, "w", encoding='utf-8') as file:
            for line in dataToWrite:
                file.write(line + "\n")
