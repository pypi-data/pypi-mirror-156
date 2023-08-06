# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlDrukknopMerk(KeuzelijstField):
    """Keuzelijst met merknamen voor Drukknop."""
    naam = 'KlDrukknopMerk'
    label = 'Drukknop merk'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlDrukknopMerk'
    definition = 'Keuzelijst met merknamen voor Drukknop.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlDrukknopMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlDrukknopMerk.get_dummy_data()

