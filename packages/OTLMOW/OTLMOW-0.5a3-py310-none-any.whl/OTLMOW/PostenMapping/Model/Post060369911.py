# coding=utf-8
from OTLMOW.PostenMapping.StandaardPost import StandaardPost
from OTLMOW.PostenMapping.StandaardPostMapping import StandaardPostMapping


# Generated with PostenCreator. To modify: extend, do not edit
class Post060369911(StandaardPost):
    def __init__(self):
        super().__init__(
            nummer='0603.69911',
            beschrijving='Aanbrengen van uitzettingsvoeg volgens 6-3.7.3.8',
            meetstaateenheid='M',
            mappings=[StandaardPostMapping(
                typeURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdekvoeg',
                attribuutURI='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdekvoeg.type',
                dotnotation='type',
                defaultWaarde='uitzettingsvoeg',
                range='',
                usagenote='',
                isMeetstaatAttr=0,
                isAltijdInTeVullen=0,
                isBasisMapping=1,
                mappingStatus='gemapt 2.0',
                mappingOpmerking='',
                standaardpostnummer='0603.69911')
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
                standaardpostnummer='0603.69911')])
