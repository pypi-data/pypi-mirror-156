# coding=utf-8
from OTLMOW.OTLModel.Classes.Abstracten.BegroeidVoorkomen import BegroeidVoorkomen
from OTLMOW.GeometrieArtefact.VlakGeometrie import VlakGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class InvasieveExoten(BegroeidVoorkomen, VlakGeometrie):
    """Invasieve exoten zijn planten die door menselijk handelen buiten hun natuurlijk verspreidingsgebied ('exoot') gebracht zijn en die in staat zijn zich op een natuurlijke wijze, al dan niet massaal, te verspreiden en hierbij schade (biodiversiteit, economisch, volksgezondheid) kunnen aanrichten ('invasief')."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#InvasieveExoten'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        BegroeidVoorkomen.__init__(self)
        VlakGeometrie.__init__(self)
