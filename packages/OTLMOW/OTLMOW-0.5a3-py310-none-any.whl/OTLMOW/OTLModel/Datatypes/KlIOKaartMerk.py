# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlIOKaartMerk(KeuzelijstField):
    """Lijst van mogelijke merken voor IO-kaarten."""
    naam = 'KlIOKaartMerk'
    label = 'IO-kaart merken'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlIOKaartMerk'
    definition = 'Lijst van mogelijke merken voor IO-kaarten.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlIOKaartMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlIOKaartMerk.get_dummy_data()

