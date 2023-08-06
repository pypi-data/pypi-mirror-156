# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLEGCSchermtype(KeuzelijstField):
    """De mogelijke schermtypes (vlak, niet-vlak)."""
    naam = 'KlLEGCSchermtype'
    label = 'Schermtype'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLEGCSchermtype'
    definition = 'De mogelijke schermtypes (vlak, niet-vlak).'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLEGCSchermtype'
    options = {
        'niet-vlak': KeuzelijstWaarde(invulwaarde='niet-vlak',
                                      label='niet-vlak',
                                      definitie='De niet-vlakke schermen zijn de schermen die niet kunnen getest worden volgens de normen NBN EN 1793-1 NBN EN 1793-2.',
                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEGCSchermtype/niet-vlak'),
        'vlak': KeuzelijstWaarde(invulwaarde='vlak',
                                 label='vlak',
                                 definitie='De vlakke schermen zijn de schermen die kunnen getest worden volgens de normen NBN EN 1793-1 NBN EN 1793-2.',
                                 objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEGCSchermtype/vlak')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLEGCSchermtype.get_dummy_data()

