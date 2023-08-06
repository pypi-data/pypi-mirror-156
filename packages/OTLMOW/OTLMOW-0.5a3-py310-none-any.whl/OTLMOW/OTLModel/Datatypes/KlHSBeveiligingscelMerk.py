# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlHSBeveiligingscelMerk(KeuzelijstField):
    """Het merk van de HS-beveiligingscel."""
    naam = 'KlHSBeveiligingscelMerk'
    label = 'HS-beveiligingscel merk'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlHSBeveiligingscelMerk'
    definition = 'Het merk van de HS-beveiligingscel.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlHSBeveiligingscelMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlHSBeveiligingscelMerk.get_dummy_data()

