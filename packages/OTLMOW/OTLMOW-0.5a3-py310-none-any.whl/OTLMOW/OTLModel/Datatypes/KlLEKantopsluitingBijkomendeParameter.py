# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLEKantopsluitingBijkomendeParameter(KeuzelijstField):
    """Gedetailleerder typeren van de kantopsluiting."""
    naam = 'KlLEKantopsluitingBijkomendeParameter'
    label = 'Kantopsluiting bijkomende parameter'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLEKantopsluitingBijkomendeParameter'
    definition = 'Gedetailleerder typeren van de kantopsluiting.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLEKantopsluitingBijkomendeParameter'
    options = {
        'eindschikking-voor-schampkant': KeuzelijstWaarde(invulwaarde='eindschikking-voor-schampkant',
                                                          label='eindschikking voor schampkant',
                                                          definitie='eindschikking voor schampkant',
                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/eindschikking-voor-schampkant'),
        'gebogen-kantstrook-of-watergreppel-straal-groter-5m': KeuzelijstWaarde(invulwaarde='gebogen-kantstrook-of-watergreppel-straal-groter-5m',
                                                                                label='gebogen kantstrook of watergreppel straal groter 5m',
                                                                                definitie='gebogen kantstrook of watergreppel, met straal groter dan 5m',
                                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-kantstrook-of-watergreppel-straal-groter-5m'),
        'gebogen-kantstrook-of-watergreppel-straal-kleiner-of-gelijk-5m': KeuzelijstWaarde(invulwaarde='gebogen-kantstrook-of-watergreppel-straal-kleiner-of-gelijk-5m',
                                                                                           label='gebogen kantstrook of watergreppel straal kleiner of gelijk 5m',
                                                                                           definitie='gebogen kantstrook of watergreppel, met straal kleiner of gelijk 5m',
                                                                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-kantstrook-of-watergreppel-straal-kleiner-of-gelijk-5m'),
        'gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m': KeuzelijstWaarde(invulwaarde='gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m',
                                                                                               label='gebogen trottoirband of Trottoirband-watergreppel straal groter 5m',
                                                                                               definitie='Gebogen trottoirband of trottoirband-watergreppel, met straal groter dan 5 m.',
                                                                                               objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m'),
        'gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m-reflectoren-schuin': KeuzelijstWaarde(invulwaarde='gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m-reflectoren-schuin',
                                                                                                                  label='gebogen trottoirband of Trottoirband-watergreppel straal groter 5m reflectoren schuin',
                                                                                                                  definitie='Gebogen trottoirband of trottoirband-watergreppel, met straal groter dan 5 m met schuin geplaatste reflectoren.',
                                                                                                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m-reflectoren-schuin'),
        'gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m-reflectoren-verticaal': KeuzelijstWaarde(invulwaarde='gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m-reflectoren-verticaal',
                                                                                                                     label='gebogen trottoirband of Trottoirband-watergreppel straal groter 5m reflectoren verticaal',
                                                                                                                     definitie='Gebogen trottoirband of trottoirband-watergreppel, met straal groter dan 5 m met verticaal geplaatste reflectoren.',
                                                                                                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-trottoirband-of-Trottoirband-watergreppel-straal-groter-5m-reflectoren-verticaal'),
        'gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m': KeuzelijstWaarde(invulwaarde='gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m',
                                                                                                          label='gebogen trottoirband of Trottoirband-watergreppel straal kleiner of gelijk 5m',
                                                                                                          definitie='gebogen trottoirband of trottoirband-watergreppel, met straal kleiner of gelijk aan 5m',
                                                                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m'),
        'gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m-reflectoren-schuin': KeuzelijstWaarde(invulwaarde='gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m-reflectoren-schuin',
                                                                                                                             label='gebogen trottoirband of Trottoirband-watergreppel straal kleiner of gelijk 5m reflectoren schuin',
                                                                                                                             definitie='Gebogen trottoirband of trottoirband-watergreppel, met straal kleiner of gelijk aan 5m en schuin geplaatste reflectoren.',
                                                                                                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m-reflectoren-schuin'),
        'gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m-reflectoren-verticaal': KeuzelijstWaarde(invulwaarde='gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m-reflectoren-verticaal',
                                                                                                                                label='gebogen trottoirband of Trottoirband-watergreppel straal kleiner of gelijk 5m reflectoren verticaal',
                                                                                                                                definitie='Gebogen trottoirband of trottoirband-watergreppel, met straal kleiner of gelijk aan 5m met verticaal geplaatste reflectoren.',
                                                                                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/gebogen-trottoirband-of-Trottoirband-watergreppel-straal-kleiner-of-gelijk-5m-reflectoren-verticaal'),
        'hoekstukken.-hoek-90°-of-270°': KeuzelijstWaarde(invulwaarde='hoekstukken.-hoek-90°-of-270°',
                                                          label='hoekstukken. hoek 90° of 270°',
                                                          definitie='hoekstukken waarbij de hoek gelijk is aan 90° of 270°',
                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/hoekstukken.-hoek-90°-of-270°'),
        'hoekstukken.-hoek-verschillend-90°-of-270°': KeuzelijstWaarde(invulwaarde='hoekstukken.-hoek-verschillend-90°-of-270°',
                                                                       label='hoekstukken. hoek verschillend 90° of 270°',
                                                                       definitie='Hoekstukken, hoek verschillend van 90° of 270°',
                                                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/hoekstukken.-hoek-verschillend-90°-of-270°'),
        'overgangstrottoirbanden': KeuzelijstWaarde(invulwaarde='overgangstrottoirbanden',
                                                    label='overgangstrottoirbanden',
                                                    definitie='Overgangstrottoirbanden',
                                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/overgangstrottoirbanden'),
        'rechte-kantstrook-of-watergreppel': KeuzelijstWaarde(invulwaarde='rechte-kantstrook-of-watergreppel',
                                                              label='rechte kantstrook of watergreppel',
                                                              definitie='Rechte kantstrook of watergreppel.',
                                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/rechte-kantstrook-of-watergreppel'),
        'rechte-schampkant': KeuzelijstWaarde(invulwaarde='rechte-schampkant',
                                              label='rechte schampkant',
                                              definitie='rechte schampkant',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/rechte-schampkant'),
        'rechte-trottoirband-of-Trottoirband-watergreppel-reflectoren-schuin': KeuzelijstWaarde(invulwaarde='rechte-trottoirband-of-Trottoirband-watergreppel-reflectoren-schuin',
                                                                                                label='rechte trottoirband of Trottoirband-watergreppel reflectoren schuin',
                                                                                                definitie='Rechte trottoirband of trottoirband-watergreppel met schuin geplaatste reflectoren.',
                                                                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/rechte-trottoirband-of-Trottoirband-watergreppel-reflectoren-schuin'),
        'rechte-trottoirband-of-trottoirband-watergreppel': KeuzelijstWaarde(invulwaarde='rechte-trottoirband-of-trottoirband-watergreppel',
                                                                             label='rechte trottoirband of trottoirband-watergreppel',
                                                                             definitie='Rechte trottoirband of trottoirband-watergreppel.',
                                                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/rechte-trottoirband-of-trottoirband-watergreppel'),
        'rechte-trottoirband-of-trottoirbandwater-greppel-reflectoren-verticaal': KeuzelijstWaarde(invulwaarde='rechte-trottoirband-of-trottoirbandwater-greppel-reflectoren-verticaal',
                                                                                                   label='rechte trottoirband of trottoirbandwater-greppel reflectoren verticaal',
                                                                                                   definitie='Rechte trottoirband of trottoirband-watergreppel met verticaal geplaatste reflectoren.',
                                                                                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/rechte-trottoirband-of-trottoirbandwater-greppel-reflectoren-verticaal'),
        'supplement-voor-in-verstek-zagen': KeuzelijstWaarde(invulwaarde='supplement-voor-in-verstek-zagen',
                                                             label='supplement voor in verstek zagen',
                                                             definitie='supplement voor in verstek zagen',
                                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/supplement-voor-in-verstek-zagen'),
        'trottoirbanden-voor-minder-validen': KeuzelijstWaarde(invulwaarde='trottoirbanden-voor-minder-validen',
                                                               label='trottoirbanden voor minder-validen',
                                                               definitie='trottoirbanden voor minder-validen',
                                                               objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLEKantopsluitingBijkomendeParameter/trottoirbanden-voor-minder-validen')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLEKantopsluitingBijkomendeParameter.get_dummy_data()

