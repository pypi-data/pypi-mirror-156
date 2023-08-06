# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from abc import abstractmethod
from OTLMOW.OTLModel.Classes.ImplementatieElement.AIMObject import AIMObject
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument


# Generated with OTLClassCreator. To modify: extend, do not edit
class LijnvormigElement(AIMObject):
    """Abstracte voor de gemeenschappelijke eigenschappen en relaties van lijnvormige elementen."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#LijnvormigElement'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()

        self._technischeFiche = OTLAttribuut(field=DtcDocument,
                                             naam='technischeFiche',
                                             label='technische fiche',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#LijnvormigElement.technischeFiche',
                                             kardinaliteit_max='*',
                                             definition='De technische fiche van het lijnvormig element.',
                                             owner=self)

    @property
    def technischeFiche(self):
        """De technische fiche van het lijnvormig element."""
        return self._technischeFiche.get_waarde()

    @technischeFiche.setter
    def technischeFiche(self, value):
        self._technischeFiche.set_waarde(value, owner=self)
