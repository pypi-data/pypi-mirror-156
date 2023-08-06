# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlHandbedieningType(KeuzelijstField):
    """Types van handbediening voor toestellen bevestigd aan een kast."""
    naam = 'KlHandbedieningType'
    label = 'Handbediening type'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlHandbedieningType'
    definition = 'Types van handbediening voor toestellen bevestigd aan een kast.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlHandbedieningType'
    options = {
        'drukknop': KeuzelijstWaarde(invulwaarde='drukknop',
                                     label='drukknop',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlHandbedieningType/drukknop'),
        'schakelaar': KeuzelijstWaarde(invulwaarde='schakelaar',
                                       label='schakelaar',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlHandbedieningType/schakelaar'),
        'sleutelcontact': KeuzelijstWaarde(invulwaarde='sleutelcontact',
                                           label='sleutelcontact',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlHandbedieningType/sleutelcontact')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlHandbedieningType.get_dummy_data()

