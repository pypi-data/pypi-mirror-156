# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLEGCGeluidskarakteristiek(KeuzelijstField):
    """De geluidskarakteristieken van de geluidswerende constructie."""
    naam = 'KlLEGCGeluidskarakteristiek'
    label = 'Geluidskarakteristiek'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLEGCGeluidskarakteristiek'
    definition = 'De geluidskarakteristieken van de geluidswerende constructie.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLEGCGeluidskarakteristiek'
    options = {
        'absorberend': KeuzelijstWaarde(invulwaarde='absorberend',
                                        label='absorberend',
                                        definitie='De geluidsgolven worden gedeeltelijk niet weerkaatst door de geluidswerende constructie.',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEGCGeluidskarakteristiek/absorberend'),
        'bi-absorberend': KeuzelijstWaarde(invulwaarde='bi-absorberend',
                                           label='bi-absorberend',
                                           definitie='De geluidsgolven worden gedeeltelijk niet weerkaatst door de geluidswerende constructie (langs beide zijden).',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEGCGeluidskarakteristiek/bi-absorberend'),
        'reflecterend': KeuzelijstWaarde(invulwaarde='reflecterend',
                                         label='reflecterend',
                                         definitie='reflecterend',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEGCGeluidskarakteristiek/reflecterend')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLEGCGeluidskarakteristiek.get_dummy_data()

