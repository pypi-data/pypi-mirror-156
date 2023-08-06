# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Abstracten.Proef import Proef
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument
from OTLMOW.GeometrieArtefact.PuntGeometrie import PuntGeometrie
from OTLMOW.GeometrieArtefact.LijnGeometrie import LijnGeometrie
from OTLMOW.GeometrieArtefact.VlakGeometrie import VlakGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefGaafheid(Proef, PuntGeometrie, LijnGeometrie, VlakGeometrie):
    """Controle van het lijnvormig element op de ongeschondenheid, volledigheid en zuiverheid."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefGaafheid'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        Proef.__init__(self)
        LijnGeometrie.__init__(self)
        PuntGeometrie.__init__(self)
        VlakGeometrie.__init__(self)

        self._gaafheid = OTLAttribuut(field=DtcDocument,
                                      naam='gaafheid',
                                      label='gaafheid',
                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefGaafheid.gaafheid',
                                      definition='De resultaten van de controle.',
                                      owner=self)

    @property
    def gaafheid(self):
        """De resultaten van de controle."""
        return self._gaafheid.get_waarde()

    @gaafheid.setter
    def gaafheid(self, value):
        self._gaafheid.set_waarde(value, owner=self)
