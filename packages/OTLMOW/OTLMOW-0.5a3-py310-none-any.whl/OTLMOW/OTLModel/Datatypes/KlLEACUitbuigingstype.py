# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLEACUitbuigingstype(KeuzelijstField):
    """De mogelijke uitbuigingstypes."""
    naam = 'KlLEACUitbuigingstype'
    label = 'Uitbuigingstype'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLEACUitbuigingstype'
    definition = 'De mogelijke uitbuigingstypes.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLEACUitbuigingstype'
    options = {
        'type-1': KeuzelijstWaarde(invulwaarde='type-1',
                                   label='type 1',
                                   definitie='Uitbuiging op wegen tot 90 km/h, straal R = 10 meter',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEACUitbuigingstype/type-1'),
        'type-2': KeuzelijstWaarde(invulwaarde='type-2',
                                   label='type 2',
                                   definitie='Uitbuiging op wegen vanaf 90 km/h, L = 25 meter',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEACUitbuigingstype/type-2')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLEACUitbuigingstype.get_dummy_data()

