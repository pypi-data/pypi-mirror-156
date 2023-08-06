# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlTelecomkabelTypeSpecificatie(KeuzelijstField):
    """Lijst met mogelijke specificaties van het type van de telecomkabel volgens een vaste lijst om bv. de brandklasse mee te geven."""
    naam = 'KlTelecomkabelTypeSpecificatie'
    label = 'Telecomkabel type specificatie'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlTelecomkabelTypeSpecificatie'
    definition = 'Lijst met mogelijke specificaties van het type van de telecomkabel volgens een vaste lijst om bv. de brandklasse mee te geven.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlTelecomkabelTypeSpecificatie'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlTelecomkabelTypeSpecificatie.get_dummy_data()

