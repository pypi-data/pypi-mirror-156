# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlRackModelnaam(KeuzelijstField):
    """Modelnamen voor racks."""
    naam = 'KlRackModelnaam'
    label = 'Rack modelnaam'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlRackModelnaam'
    definition = 'Modelnamen voor racks.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlRackModelnaam'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlRackModelnaam.get_dummy_data()

