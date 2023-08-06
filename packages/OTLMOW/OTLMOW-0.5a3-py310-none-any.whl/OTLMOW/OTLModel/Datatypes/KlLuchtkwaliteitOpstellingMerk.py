# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLuchtkwaliteitOpstellingMerk(KeuzelijstField):
    """Het merk van een onderdeel uit een luchtkwaliteitsinstallatie."""
    naam = 'KlLuchtkwaliteitOpstellingMerk'
    label = 'Luchtkwaliteitsopstelling merk'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#KlLuchtkwaliteitOpstellingMerk'
    definition = 'Het merk van een onderdeel uit een luchtkwaliteitsinstallatie.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLuchtkwaliteitOpstellingMerk'
    options = {
        'sick': KeuzelijstWaarde(invulwaarde='sick',
                                 label='sick',
                                 objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLuchtkwaliteitOpstellingMerk/sick')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLuchtkwaliteitOpstellingMerk.get_dummy_data()

