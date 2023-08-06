# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Abstracten.Behuizing import Behuizing
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument
from OTLMOW.GeometrieArtefact.VlakGeometrie import VlakGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class Lokaal(Behuizing, VlakGeometrie):
    """Een ruimte binnen een gebouw."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Lokaal'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        Behuizing.__init__(self)
        VlakGeometrie.__init__(self)

        self._grondplan = OTLAttribuut(field=DtcDocument,
                                       naam='grondplan',
                                       label='grondplan',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Lokaal.grondplan',
                                       definition='Plattegrond van het lokaal met aanduidingen van de verschillende aanwezige elementen zoals kasten met kastnummers, toegangscontrole en meer.',
                                       owner=self)

    @property
    def grondplan(self):
        """Plattegrond van het lokaal met aanduidingen van de verschillende aanwezige elementen zoals kasten met kastnummers, toegangscontrole en meer."""
        return self._grondplan.get_waarde()

    @grondplan.setter
    def grondplan(self, value):
        self._grondplan.set_waarde(value, owner=self)
