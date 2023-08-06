# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlVentilatorRichting(KeuzelijstField):
    """Keuzelijst die aangeeft of de luchtstroom in één richting of beide richtingen kan plaatsvinden."""
    naam = 'KlVentilatorRichting'
    label = 'Ventilator richting'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlVentilatorRichting'
    definition = 'Keuzelijst die aangeeft of de luchtstroom in één richting of beide richtingen kan plaatsvinden.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlVentilatorRichting'
    options = {
        'bidirectioneel': KeuzelijstWaarde(invulwaarde='bidirectioneel',
                                           label='bidirectioneel',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlVentilatorRichting/bidirectioneel'),
        'unidirectioneel': KeuzelijstWaarde(invulwaarde='unidirectioneel',
                                            label='unidirectioneel',
                                            objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlVentilatorRichting/unidirectioneel')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlVentilatorRichting.get_dummy_data()

