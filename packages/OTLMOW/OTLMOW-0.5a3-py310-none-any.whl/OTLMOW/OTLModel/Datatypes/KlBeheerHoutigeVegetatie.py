# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlBeheerHoutigeVegetatie(KeuzelijstField):
    """De verschillende beheersopties voor houtige vegetatie."""
    naam = 'KlBeheerHoutigeVegetatie'
    label = 'Beheer houtige vegetatie'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/levenscyclus#KlBeheerHoutigeVegetatie'
    definition = 'De verschillende beheersopties voor houtige vegetatie.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlBeheerHoutigeVegetatie'
    options = {
        'afpalingswerken': KeuzelijstWaarde(invulwaarde='afpalingswerken',
                                            label='afpalingswerken',
                                            definitie='Het afpalen van bepaalde oppervlaktes met vegetatie.',
                                            objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/afpalingswerken'),
        'begieten': KeuzelijstWaarde(invulwaarde='begieten',
                                     label='begieten',
                                     definitie='Periodisch begieten van vegetatie. ',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/begieten'),
        'bestrijding': KeuzelijstWaarde(invulwaarde='bestrijding',
                                        label='bestrijding',
                                        definitie='Bestrijding van ongewenste onkruiden.',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bestrijding'),
        'bodemafdekking-boomplaat': KeuzelijstWaarde(invulwaarde='bodemafdekking-boomplaat',
                                                     label='bodemafdekking - boomplaat',
                                                     definitie='De bodem wordt afgedekt met een boomplaat.',
                                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bodemafdekking-boomplaat'),
        'bodemafdekking-boomschors': KeuzelijstWaarde(invulwaarde='bodemafdekking-boomschors',
                                                      label='bodemafdekking - boomschors',
                                                      definitie='De bodem wordt afgedekt met boomschors.',
                                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bodemafdekking-boomschors'),
        'bodemafdekking-doek-in-jute-pla-folie': KeuzelijstWaarde(invulwaarde='bodemafdekking-doek-in-jute-pla-folie',
                                                                  label='bodemafdekking - doek in jute & PLA folie',
                                                                  definitie='De bodem wordt afgedekt met een doek in jute en PLA-folie.',
                                                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bodemafdekking-doek-in-jute-pla-folie'),
        'bodemafdekking-groencompost': KeuzelijstWaarde(invulwaarde='bodemafdekking-groencompost',
                                                        label='bodemafdekking - groencompost',
                                                        definitie='De bodem wordt afgedekt met groencompost.',
                                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bodemafdekking-groencompost'),
        'bodemafdekking-houtsnippers': KeuzelijstWaarde(invulwaarde='bodemafdekking-houtsnippers',
                                                        label='bodemafdekking - houtsnippers',
                                                        definitie='De bodem wordt afgedekt met houtsnippers.',
                                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bodemafdekking-houtsnippers'),
        'bodemafdekking-pla-doek': KeuzelijstWaarde(invulwaarde='bodemafdekking-pla-doek',
                                                    label='bodemafdekking - PLA doek',
                                                    definitie='De bodem wordt afgedekt met een PLA-doek.',
                                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/bodemafdekking-pla-doek'),
        'dunnen': KeuzelijstWaarde(invulwaarde='dunnen',
                                   label='dunnen',
                                   definitie='Het gelijkgronds afzagen van bomen ter bevordering van de groei van omstaande bomen of struiken.',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/dunnen'),
        'gedeeltelijk-ontstronken': KeuzelijstWaarde(invulwaarde='gedeeltelijk-ontstronken',
                                                     label='gedeeltelijk ontstronken',
                                                     definitie='Gedeeltelijk ontstronken van bomen. ',
                                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/gedeeltelijk-ontstronken'),
        'hakhoutbeheer': KeuzelijstWaarde(invulwaarde='hakhoutbeheer',
                                          label='hakhoutbeheer',
                                          definitie='Er wordt hakhoutbeheer uitgevoerd.',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/hakhoutbeheer'),
        'hakken': KeuzelijstWaarde(invulwaarde='hakken',
                                   label='hakken',
                                   definitie='Hakken van de grond tussen houtige vegetaties.',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/hakken'),
        'maaien': KeuzelijstWaarde(invulwaarde='maaien',
                                   label='maaien',
                                   definitie='Het maaien van de grazige vegetatie tussen de houtige vegetatie.',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/maaien'),
        'niets-doen': KeuzelijstWaarde(invulwaarde='niets-doen',
                                       label='niets doen',
                                       definitie='Er wordt geen beheer uitgevoerd.',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/niets-doen'),
        'ontstronken': KeuzelijstWaarde(invulwaarde='ontstronken',
                                        label='ontstronken',
                                        definitie='Ontstronken van bomen. ',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/ontstronken'),
        'rooien': KeuzelijstWaarde(invulwaarde='rooien',
                                   label='rooien',
                                   definitie='Wegnemen van vegetatie dmv rooien. ',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/rooien'),
        'scheren': KeuzelijstWaarde(invulwaarde='scheren',
                                    label='scheren',
                                    definitie='Het vlakvormig gelijkmatig kort afsnijden van takken van hagen, heesters en houtkanten.',
                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/scheren'),
        'snoeien': KeuzelijstWaarde(invulwaarde='snoeien',
                                    label='snoeien',
                                    definitie='Het inkorten of wegnemen van takken met snoeischaar of zaag.',
                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/snoeien'),
        'spitten': KeuzelijstWaarde(invulwaarde='spitten',
                                    label='spitten',
                                    definitie='Spitten van de grond tussen houtige vegetaties.',
                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/spitten'),
        'wieden': KeuzelijstWaarde(invulwaarde='wieden',
                                   label='wieden',
                                   definitie='Het wieden van de grond tussen houtige vegetaties. Dit is het verwijderen van onkruid.',
                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlBeheerHoutigeVegetatie/wieden')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlBeheerHoutigeVegetatie.get_dummy_data()

