# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlVrComKaartTypeOpslaggeheugen(KeuzelijstField):
    """Keuzelijst met verschillende types geheugen van een VRCommunicatiekaart."""
    naam = 'KlVrComKaartTypeOpslaggeheugen'
    label = 'VR-communicatiekaart type opslaggeheugen'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlVrComKaartTypeOpslaggeheugen'
    definition = 'Keuzelijst met verschillende types geheugen van een VRCommunicatiekaart.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlVrComKaartTypeOpslaggeheugen'
    options = {
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlVrComKaartTypeOpslaggeheugen.get_dummy_data()

