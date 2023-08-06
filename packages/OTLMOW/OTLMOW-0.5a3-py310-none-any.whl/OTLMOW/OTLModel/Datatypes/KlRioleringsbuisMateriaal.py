# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlRioleringsbuisMateriaal(KeuzelijstField):
    """Materialen van de rioleringbuis."""
    naam = 'KlRioleringsbuisMateriaal'
    label = 'Rioleringsbuis materiaal'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlRioleringsbuisMateriaal'
    definition = 'Materialen van de rioleringbuis.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlRioleringsbuisMateriaal'
    options = {
        'PP-buizen': KeuzelijstWaarde(invulwaarde='PP-buizen',
                                      label='PP-buizen',
                                      definitie='PP-buizen',
                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/PP-buizen'),
        'PVC-U-composietleidingen': KeuzelijstWaarde(invulwaarde='PVC-U-composietleidingen',
                                                     label='PVC-U-composietleidingen',
                                                     definitie='PVC-U-composietleidingen',
                                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/PVC-U-composietleidingen'),
        'PVC-buizen': KeuzelijstWaarde(invulwaarde='PVC-buizen',
                                       label='PVC-buizen',
                                       definitie='PVC-buizen',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/PVC-buizen'),
        'afvoerbuizen-van-polyethyleen': KeuzelijstWaarde(invulwaarde='afvoerbuizen-van-polyethyleen',
                                                          label='afvoerbuizen van polyethyleen',
                                                          definitie='buizen vervaardigd uit polyethyleen',
                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/afvoerbuizen-van-polyethyleen'),
        'betonbuizen-met-plaatstalen-kern': KeuzelijstWaarde(invulwaarde='betonbuizen-met-plaatstalen-kern',
                                                             label='betonbuizen met plaatstalen kern',
                                                             definitie='Betonbuizen met plaatstalen kern',
                                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/betonbuizen-met-plaatstalen-kern'),
        'buizen-van-gevuld-en-glasvezelversterkt-polyesterhars-(UP-GF)': KeuzelijstWaarde(invulwaarde='buizen-van-gevuld-en-glasvezelversterkt-polyesterhars-(UP-GF)',
                                                                                          label='buizen van gevuld en glasvezelversterkt polyesterhars (UP-GF)',
                                                                                          definitie='Buizen van gevuld en glasvezelversterkt polyesterhars (UP-GF)',
                                                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/buizen-van-gevuld-en-glasvezelversterkt-polyesterhars-(UP-GF)'),
        'buizen-van-hoogwaardig-beton': KeuzelijstWaarde(invulwaarde='buizen-van-hoogwaardig-beton',
                                                         label='buizen van hoogwaardig beton',
                                                         definitie='Buizen van hoogwaardig beton',
                                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/buizen-van-hoogwaardig-beton'),
        'buizen-van-nodulair-gietijzer-zonder-inwendige-druk': KeuzelijstWaarde(invulwaarde='buizen-van-nodulair-gietijzer-zonder-inwendige-druk',
                                                                                label='buizen van nodulair gietijzer zonder inwendige druk',
                                                                                definitie='Buizen van nodulair gietijzer zonder inwendige druk',
                                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/buizen-van-nodulair-gietijzer-zonder-inwendige-druk'),
        'buizen-van-poreus-beton-volgens-3-24.6': KeuzelijstWaarde(invulwaarde='buizen-van-poreus-beton-volgens-3-24.6',
                                                                   label='buizen van poreus beton volgens 3-24.6',
                                                                   definitie='Buizen van poreus beton volgens 3-24.6',
                                                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/buizen-van-poreus-beton-volgens-3-24.6'),
        'doorpersbuizen-van-beton-met-plaatstalen-kern-en-dubbel-voegsysteem': KeuzelijstWaarde(invulwaarde='doorpersbuizen-van-beton-met-plaatstalen-kern-en-dubbel-voegsysteem',
                                                                                                label='doorpersbuizen van beton met plaatstalen kern en dubbel voegsysteem',
                                                                                                definitie='Doorpersbuizen van beton met plaatstalen kern en dubbel voegsysteem',
                                                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/doorpersbuizen-van-beton-met-plaatstalen-kern-en-dubbel-voegsysteem'),
        'doorpersbuizen-van-gevuld-en-glasvezelversterkt-polyesterhars': KeuzelijstWaarde(invulwaarde='doorpersbuizen-van-gevuld-en-glasvezelversterkt-polyesterhars',
                                                                                          label='doorpersbuizen van gevuld en glasvezelversterkt polyesterhars',
                                                                                          definitie='Doorpersbuizen van gevuld en glasvezelversterkt polyesterhars',
                                                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/doorpersbuizen-van-gevuld-en-glasvezelversterkt-polyesterhars'),
        'doorpersbuizen-van-gewapend-beton-voorzien-van-een-harde-PVC-bekleding': KeuzelijstWaarde(invulwaarde='doorpersbuizen-van-gewapend-beton-voorzien-van-een-harde-PVC-bekleding',
                                                                                                   label='doorpersbuizen van gewapend beton voorzien van een harde PVC-bekleding',
                                                                                                   definitie='Doorpersbuizen van polymeerbeton',
                                                                                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/doorpersbuizen-van-gewapend-beton-voorzien-van-een-harde-PVC-bekleding'),
        'doorpersbuizen-van-gewapend-beton.-sterktereeks-135': KeuzelijstWaarde(invulwaarde='doorpersbuizen-van-gewapend-beton.-sterktereeks-135',
                                                                                label='doorpersbuizen van gewapend beton. sterktereeks 135',
                                                                                definitie='Doorpersbuizen van gewapend beton, sterktereeks 135',
                                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/doorpersbuizen-van-gewapend-beton.-sterktereeks-135'),
        'doorpersbuizen-van-gres': KeuzelijstWaarde(invulwaarde='doorpersbuizen-van-gres',
                                                    label='doorpersbuizen van gres',
                                                    definitie='Doorpersbuizen van gres',
                                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/doorpersbuizen-van-gres'),
        'gewapend-betonbuizen': KeuzelijstWaarde(invulwaarde='gewapend-betonbuizen',
                                                 label='gewapend-betonbuizen',
                                                 definitie='Gewapend-betonbuizen',
                                                 objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/gewapend-betonbuizen'),
        'gresbuizen': KeuzelijstWaarde(invulwaarde='gresbuizen',
                                       label='gresbuizen',
                                       definitie='gresbuis is een (riool)buis gemaakt van vette klei en chamotte met een gladde en zeer harde afwerking.',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/gresbuizen'),
        'met-staalvezels-versterkte-betonbuizen': KeuzelijstWaarde(invulwaarde='met-staalvezels-versterkte-betonbuizen',
                                                                   label='met staalvezels versterkte betonbuizen',
                                                                   definitie='Met staalvezels versterkte betonbuizen',
                                                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/met-staalvezels-versterkte-betonbuizen'),
        'ongewapende-betonbuizen': KeuzelijstWaarde(invulwaarde='ongewapende-betonbuizen',
                                                    label='ongewapende betonbuizen',
                                                    definitie='Ongewapende betonbuizen',
                                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/ongewapende-betonbuizen'),
        'voorgespannen-gewapende-betonbuizen': KeuzelijstWaarde(invulwaarde='voorgespannen-gewapende-betonbuizen',
                                                                label='voorgespannen gewapende betonbuizen',
                                                                definitie='Voorgespannen gewapende betonbuizen',
                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/voorgespannen-gewapende-betonbuizen'),
        'wandversterkte-HDPE-buizen': KeuzelijstWaarde(invulwaarde='wandversterkte-HDPE-buizen',
                                                       label='wandversterkte HDPE-buizen',
                                                       definitie='Wandversterkte HDPE-buizen',
                                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlRioleringsbuisMateriaal/wandversterkte-HDPE-buizen')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlRioleringsbuisMateriaal.get_dummy_data()

