# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlKlimatisatieMerk(KeuzelijstField):
    """Merknamen voor klimatisatiesystemen."""
    naam = 'KlKlimatisatieMerk'
    label = 'Klimatisatie merk'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlKlimatisatieMerk'
    definition = 'Merknamen voor klimatisatiesystemen.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlKlimatisatieMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlKlimatisatieMerk.get_dummy_data()

