# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.ImplementatieElement.NaampadObject import NaampadObject
from OTLMOW.OTLModel.Datatypes.KlPadNetwerkprotectie import KlPadNetwerkprotectie
from OTLMOW.GeometrieArtefact.GeenGeometrie import GeenGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class Pad(NaampadObject, GeenGeometrie):
    """Een aaneengesloten reeks van links die samen een verbinding realiseren over het netwerk, gebruik makende van eenzelfde technologie (vb SDH, OTN…)."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Pad'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        NaampadObject.__init__(self)
        GeenGeometrie.__init__(self)

        self._netwerkprotectie = OTLAttribuut(field=KlPadNetwerkprotectie,
                                              naam='netwerkprotectie',
                                              label='netwerkprotectie',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Pad.netwerkprotectie',
                                              kardinaliteit_max='*',
                                              definition='Referentie van het pad dat redundantie levert aan dit pad.',
                                              owner=self)

    @property
    def netwerkprotectie(self):
        """Referentie van het pad dat redundantie levert aan dit pad."""
        return self._netwerkprotectie.get_waarde()

    @netwerkprotectie.setter
    def netwerkprotectie(self, value):
        self._netwerkprotectie.set_waarde(value, owner=self)
