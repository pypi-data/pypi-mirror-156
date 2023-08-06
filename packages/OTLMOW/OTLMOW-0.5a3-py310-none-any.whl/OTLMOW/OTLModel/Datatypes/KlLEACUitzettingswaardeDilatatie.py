# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLEACUitzettingswaardeDilatatie(KeuzelijstField):
    """De grootst mogelijke uitzetting die mogelijk is voor een bepaalde dilatatieoplossing."""
    naam = 'KlLEACUitzettingswaardeDilatatie'
    label = 'Uitzetttingswaarde dilatatie'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLEACUitzettingswaardeDilatatie'
    definition = 'De grootst mogelijke uitzetting die mogelijk is voor een bepaalde dilatatieoplossing.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLEACUitzettingswaardeDilatatie'
    options = {
        '10-cm': KeuzelijstWaarde(invulwaarde='10-cm',
                                  label='10 cm',
                                  definitie='De uitzettingswaarde is 10 cm.',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEACUitzettingswaardeDilatatie/10-cm'),
        '20-cm': KeuzelijstWaarde(invulwaarde='20-cm',
                                  label='20 cm',
                                  definitie='De uitzettingswaarde is 20 cm.',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEACUitzettingswaardeDilatatie/20-cm'),
        '90-cm': KeuzelijstWaarde(invulwaarde='90-cm',
                                  label='90 cm',
                                  definitie='De uitzettingswaarde is 90 cm.',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEACUitzettingswaardeDilatatie/90-cm')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLEACUitzettingswaardeDilatatie.get_dummy_data()

