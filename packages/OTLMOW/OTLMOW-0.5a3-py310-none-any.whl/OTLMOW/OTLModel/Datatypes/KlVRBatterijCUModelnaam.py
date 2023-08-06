# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlVRBatterijCUModelnaam(KeuzelijstField):
    """Keuzelijst met modelnamen voor VRBatterijCU."""
    naam = 'KlVRBatterijCUModelnaam'
    label = 'Batterij CU modelnaam'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlVRBatterijCUModelnaam'
    definition = 'Keuzelijst met modelnamen voor VRBatterijCU.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlVRBatterijCUModelnaam'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlVRBatterijCUModelnaam.get_dummy_data()

