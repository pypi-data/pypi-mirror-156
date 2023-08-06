# coding=utf-8
from abc import abstractmethod
from OTLMOW.GeometrieArtefact.PuntGeometrie import PuntGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class BevestigingGC(PuntGeometrie):
    """Abstracte om de bevestigingsrelatie naar de profielen en schermelementen van geluidswerende constructies te faciliteren."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#BevestigingGC'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()

        pass
