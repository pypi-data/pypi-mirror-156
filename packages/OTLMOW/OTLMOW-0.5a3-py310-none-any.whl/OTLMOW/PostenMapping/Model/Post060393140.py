# coding=utf-8
from OTLMOW.PostenMapping.StandaardPost import StandaardPost
from OTLMOW.PostenMapping.StandaardPostMapping import StandaardPostMapping


# Generated with PostenCreator. To modify: extend, do not edit
class Post060393140(StandaardPost):
    def __init__(self):
        super().__init__(
            nummer='0603.93140',
            beschrijving='Verharding van gras-kunststofplaten opgevuld met steenslag 2/6,3 volgens 6-3.10, nominale dikte 40 mm',
            meetstaateenheid='M2',
            mappings=[StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#VerhardingGrasKunststofplaat',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#VerhardingGrasKunststofplaat.vulling',
                dotnotation='vulling',
                defaultWaarde='steenslag-2-6.3',
                range='',
                usagenote='',
                isMeetstaatAttr=0,
                isAltijdInTeVullen=0,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0603.93140')
                , StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#VerhardingGrasKunststofplaat',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Laag.laagRol',
                dotnotation='laagRol',
                defaultWaarde='verharding',
                range='',
                usagenote='',
                isMeetstaatAttr=0,
                isAltijdInTeVullen=0,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0603.93140')
                , StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#VerhardingGrasKunststofplaat',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#LaagDikte.dikte',
                dotnotation='dikte',
                defaultWaarde='4',
                range='',
                usagenote='cm^^cdt:ucumunit',
                isMeetstaatAttr=0,
                isAltijdInTeVullen=0,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0603.93140')
                , StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#VerhardingGrasKunststofplaat',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Laag.oppervlakte',
                dotnotation='oppervlakte',
                defaultWaarde='',
                range='',
                usagenote='m2^^cdt:ucumunit',
                isMeetstaatAttr=1,
                isAltijdInTeVullen=1,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0603.93140')])
