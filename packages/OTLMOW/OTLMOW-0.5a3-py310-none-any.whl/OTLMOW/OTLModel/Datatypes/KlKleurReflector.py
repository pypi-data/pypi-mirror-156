# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlKleurReflector(KeuzelijstField):
    """Kleuropties voor de reflector."""
    naam = 'KlKleurReflector'
    label = 'Kleur reflector'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlKleurReflector'
    definition = 'Kleuropties voor de reflector.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlKleurReflector'
    options = {
        'amber': KeuzelijstWaarde(invulwaarde='amber',
                                  label='amber',
                                  definitie='amber',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlKleurReflector/amber'),
        'blauw': KeuzelijstWaarde(invulwaarde='blauw',
                                  label='blauw',
                                  definitie='blauw',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlKleurReflector/blauw'),
        'groen': KeuzelijstWaarde(invulwaarde='groen',
                                  label='groen',
                                  definitie='groen',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlKleurReflector/groen'),
        'rood': KeuzelijstWaarde(invulwaarde='rood',
                                 label='rood',
                                 definitie='rood',
                                 objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlKleurReflector/rood'),
        'wit': KeuzelijstWaarde(invulwaarde='wit',
                                label='wit',
                                definitie='wit',
                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlKleurReflector/wit')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlKleurReflector.get_dummy_data()

