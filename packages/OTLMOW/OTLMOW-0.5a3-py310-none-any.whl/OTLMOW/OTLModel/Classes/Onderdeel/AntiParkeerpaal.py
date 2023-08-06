# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Abstracten.Straatmeubilair import Straatmeubilair
from OTLMOW.OTLModel.Datatypes.AntiParkeerpaalType import AntiParkeerpaalType
from OTLMOW.OTLModel.Datatypes.KlAntiparkeerpaalMateriaal import KlAntiparkeerpaalMateriaal
from OTLMOW.OTLModel.Datatypes.KlPlaatsingswijze import KlPlaatsingswijze
from OTLMOW.GeometrieArtefact.PuntGeometrie import PuntGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class AntiParkeerpaal(Straatmeubilair, PuntGeometrie):
    """Een paal met als doel het parkeren te verhinderen."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AntiParkeerpaal'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        Straatmeubilair.__init__(self)
        PuntGeometrie.__init__(self)

        self._materiaal = OTLAttribuut(field=KlAntiparkeerpaalMateriaal,
                                       naam='materiaal',
                                       label='materiaal',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AntiParkeerpaal.materiaal',
                                       definition='Het materiaal van de Amsterdammer.',
                                       owner=self)

        self._plaatsingswijze = OTLAttribuut(field=KlPlaatsingswijze,
                                             naam='plaatsingswijze',
                                             label='plaatsingswijze',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AntiParkeerpaal.plaatsingswijze',
                                             definition='Aanduiding of de anti-parkeerpaal eenvoudig wegneembaar is.',
                                             owner=self)

        self._type = OTLAttribuut(field=AntiParkeerpaalType,
                                  naam='type',
                                  label='type',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AntiParkeerpaal.type',
                                  definition='Vorm van de anti-parkeerpaal.',
                                  owner=self)

    @property
    def materiaal(self):
        """Het materiaal van de Amsterdammer."""
        return self._materiaal.get_waarde()

    @materiaal.setter
    def materiaal(self, value):
        self._materiaal.set_waarde(value, owner=self)

    @property
    def plaatsingswijze(self):
        """Aanduiding of de anti-parkeerpaal eenvoudig wegneembaar is."""
        return self._plaatsingswijze.get_waarde()

    @plaatsingswijze.setter
    def plaatsingswijze(self, value):
        self._plaatsingswijze.set_waarde(value, owner=self)

    @property
    def type(self):
        """Vorm van de anti-parkeerpaal."""
        return self._type.get_waarde()

    @type.setter
    def type(self, value):
        self._type.set_waarde(value, owner=self)
