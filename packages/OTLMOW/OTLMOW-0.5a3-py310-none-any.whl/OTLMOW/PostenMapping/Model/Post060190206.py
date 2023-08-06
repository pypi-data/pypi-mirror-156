# coding=utf-8
from OTLMOW.PostenMapping.StandaardPost import StandaardPost
from OTLMOW.PostenMapping.StandaardPostMapping import StandaardPostMapping


# Generated with PostenCreator. To modify: extend, do not edit
class Post060190206(StandaardPost):
    def __init__(self):
        super().__init__(
            nummer='0601.90206',
            beschrijving='Aanbrengen van een isolatievoeg tussen een bestaande constructie en de betonverharding volgens 6-1.3.3.3.F',
            meetstaateenheid='M',
            mappings=[StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdekvoeg',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdekvoeg.type',
                dotnotation='type',
                defaultWaarde='isolatievoeg-tussen-bestaande-constructie-en-betonverharding',
                range='',
                usagenote='',
                isMeetstaatAttr=0,
                isAltijdInTeVullen=0,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0601.90206')
                , StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdekvoeg',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdekvoeg.lengte',
                dotnotation='lengte',
                defaultWaarde='',
                range='',
                usagenote='m^^cdt:ucumunit',
                isMeetstaatAttr=1,
                isAltijdInTeVullen=1,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0601.90206')])
