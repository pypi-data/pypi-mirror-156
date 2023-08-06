# coding=utf-8
from OTLMOW.OTLModel.Classes.Abstracten.DNB import DNB


# Generated with OTLClassCreator. To modify: extend, do not edit
class DNBHoogspanning(DNB):
    """Aansluiting op het hoogspanningsnet van de distributienetbeheerder."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#DNBHoogspanning'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()
