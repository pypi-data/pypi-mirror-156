# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlDynBordOpMaatMerk(KeuzelijstField):
    """Keuzelijst met de gangbare merken van dynamische borden op maat. De merken verwijzen doorgaans naar de fabrikant of leverancier."""
    naam = 'KlDynBordOpMaatMerk'
    label = 'Keuzelijst merknamen voor dynamische borden op maat'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlDynBordOpMaatMerk'
    definition = 'Keuzelijst met de gangbare merken van dynamische borden op maat. De merken verwijzen doorgaans naar de fabrikant of leverancier.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlDynBordOpMaatMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlDynBordOpMaatMerk.get_dummy_data()

