# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlGPUModelnaam(KeuzelijstField):
    """De modelnaam van de GPU."""
    naam = 'KlGPUModelnaam'
    label = 'GPU modelnaam'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlGPUModelnaam'
    definition = 'De modelnaam van de GPU.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlGPUModelnaam'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlGPUModelnaam.get_dummy_data()

