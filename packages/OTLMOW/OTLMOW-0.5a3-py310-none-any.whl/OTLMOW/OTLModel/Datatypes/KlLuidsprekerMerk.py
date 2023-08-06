# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLuidsprekerMerk(KeuzelijstField):
    """Het merk van de luidspreker."""
    naam = 'KlLuidsprekerMerk'
    label = 'Luidspreker merk'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLuidsprekerMerk'
    definition = 'Het merk van de luidspreker.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLuidsprekerMerk'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLuidsprekerMerk.get_dummy_data()

