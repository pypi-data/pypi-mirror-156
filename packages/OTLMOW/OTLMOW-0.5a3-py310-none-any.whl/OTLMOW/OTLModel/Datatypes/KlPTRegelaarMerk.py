# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlPTRegelaarMerk(KeuzelijstField):
    """Keuzelijst met merknamen voor PTRegelaar."""
    naam = 'KlPTRegelaarMerk'
    label = 'PT regelaar merk'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlPTRegelaarMerk'
    definition = 'Keuzelijst met merknamen voor PTRegelaar.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlPTRegelaarMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlPTRegelaarMerk.get_dummy_data()

