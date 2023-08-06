# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlAlgIngressProtectionCode(KeuzelijstField):
    """De IP-codering als een aanduiding voor de mate van beveiliging van de constructie van elektrische of elektronische apparatuur tegen eigen schade door gebruik in 'vijandige omgevingen' en tegen eventueel gevaar voor de gebruiker volgens IEC 60529."""
    naam = 'KlAlgIngressProtectionCode'
    label = 'Ingress Protection Codering'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlAlgIngressProtectionCode'
    definition = "De IP-codering als een aanduiding voor de mate van beveiliging van de constructie van elektrische of elektronische apparatuur tegen eigen schade door gebruik in 'vijandige omgevingen' en tegen eventueel gevaar voor de gebruiker volgens IEC 60529."
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlAlgIngressProtectionCode'
    options = {
        'i-p-44': KeuzelijstWaarde(invulwaarde='i-p-44',
                                   label='IP44',
                                   definitie='Bescherming tegen spitse voorwerpen en plensdicht.',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAlgIngressProtectionCode/i-p-44'),
        'i-p-65': KeuzelijstWaarde(invulwaarde='i-p-65',
                                   label='IP65',
                                   definitie='Stofvrij en sproeidicht.',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAlgIngressProtectionCode/i-p-65'),
        'ip54': KeuzelijstWaarde(invulwaarde='ip54',
                                 label='IP54',
                                 definitie='Spatwaterdicht en stofvrij.',
                                 objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAlgIngressProtectionCode/ip54')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlAlgIngressProtectionCode.get_dummy_data()

