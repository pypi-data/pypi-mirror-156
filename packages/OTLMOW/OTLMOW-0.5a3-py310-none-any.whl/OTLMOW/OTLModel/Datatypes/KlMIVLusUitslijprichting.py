# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlMIVLusUitslijprichting(KeuzelijstField):
    """De uitlopers van de lus gaan naar links of naar rechts  bekeken ten opzichte van de rijrichting."""
    naam = 'KlMIVLusUitslijprichting'
    label = 'MIV-lus uitslijprichting'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlMIVLusUitslijprichting'
    definition = 'De uitlopers van de lus gaan naar links of naar rechts  bekeken ten opzichte van de rijrichting.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlMIVLusUitslijprichting'
    options = {
        'links': KeuzelijstWaarde(invulwaarde='links',
                                  label='links',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlMIVLusUitslijprichting/links'),
        'rechts': KeuzelijstWaarde(invulwaarde='rechts',
                                   label='rechts',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlMIVLusUitslijprichting/rechts')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlMIVLusUitslijprichting.get_dummy_data()

