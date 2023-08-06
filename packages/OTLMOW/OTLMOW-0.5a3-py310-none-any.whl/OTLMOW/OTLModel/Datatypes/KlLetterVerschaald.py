# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlLetterVerschaald(KeuzelijstField):
    """De mogelijke letters voor een verschaalde lettermarkering."""
    naam = 'KlLetterVerschaald'
    label = 'Letter verschaald'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlLetterVerschaald'
    definition = 'De mogelijke letters voor een verschaalde lettermarkering.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlLetterVerschaald'
    options = {
        'A': KeuzelijstWaarde(invulwaarde='A',
                              label='A',
                              definitie='Letter A.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/A'),
        'B': KeuzelijstWaarde(invulwaarde='B',
                              label='B',
                              definitie='Letter B.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/B'),
        'C': KeuzelijstWaarde(invulwaarde='C',
                              label='C',
                              definitie='Letter C.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/C'),
        'D': KeuzelijstWaarde(invulwaarde='D',
                              label='D',
                              definitie='Letter D.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/D'),
        'E': KeuzelijstWaarde(invulwaarde='E',
                              label='E',
                              definitie='Letter E.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/E'),
        'F': KeuzelijstWaarde(invulwaarde='F',
                              label='F',
                              definitie='Letter F.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/F'),
        'G': KeuzelijstWaarde(invulwaarde='G',
                              label='G',
                              definitie='Letter G.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/G'),
        'H': KeuzelijstWaarde(invulwaarde='H',
                              label='H',
                              definitie='Letter H.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/H'),
        'I': KeuzelijstWaarde(invulwaarde='I',
                              label='I',
                              definitie='Letter I.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/I'),
        'J': KeuzelijstWaarde(invulwaarde='J',
                              label='J',
                              definitie='Letter J.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/J'),
        'K': KeuzelijstWaarde(invulwaarde='K',
                              label='K',
                              definitie='Letter K.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/K'),
        'L': KeuzelijstWaarde(invulwaarde='L',
                              label='L',
                              definitie='Letter L.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/L'),
        'M': KeuzelijstWaarde(invulwaarde='M',
                              label='M',
                              definitie='Letter M.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/M'),
        'N': KeuzelijstWaarde(invulwaarde='N',
                              label='N',
                              definitie='Letter N.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/N'),
        'O': KeuzelijstWaarde(invulwaarde='O',
                              label='O',
                              definitie='Letter O.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/O'),
        'P': KeuzelijstWaarde(invulwaarde='P',
                              label='P',
                              definitie='Letter P.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/P'),
        'Q': KeuzelijstWaarde(invulwaarde='Q',
                              label='Q',
                              definitie='Letter Q.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/Q'),
        'R': KeuzelijstWaarde(invulwaarde='R',
                              label='R',
                              definitie='Letter R.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/R'),
        'S': KeuzelijstWaarde(invulwaarde='S',
                              label='S',
                              definitie='Letter S.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/S'),
        'T': KeuzelijstWaarde(invulwaarde='T',
                              label='T',
                              definitie='Letter T.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/T'),
        'U': KeuzelijstWaarde(invulwaarde='U',
                              label='U',
                              definitie='Letter U.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/U'),
        'V': KeuzelijstWaarde(invulwaarde='V',
                              label='V',
                              definitie='Letter V.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/V'),
        'W': KeuzelijstWaarde(invulwaarde='W',
                              label='W',
                              definitie='Letter W.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/W'),
        'X': KeuzelijstWaarde(invulwaarde='X',
                              label='X',
                              definitie='Letter X.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/X'),
        'Y': KeuzelijstWaarde(invulwaarde='Y',
                              label='Y',
                              definitie='Letter Y.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/Y'),
        'Z': KeuzelijstWaarde(invulwaarde='Z',
                              label='Z',
                              definitie='Letter Z.',
                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlLetterVerschaald/Z')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlLetterVerschaald.get_dummy_data()

