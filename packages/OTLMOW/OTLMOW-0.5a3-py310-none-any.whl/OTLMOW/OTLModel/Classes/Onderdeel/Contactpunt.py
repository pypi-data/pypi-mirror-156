# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.ImplementatieElement.AIMObject import AIMObject
from OTLMOW.OTLModel.Datatypes.KlContactpuntType import KlContactpuntType
from OTLMOW.GeometrieArtefact.PuntGeometrie import PuntGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class Contactpunt(AIMObject, PuntGeometrie):
    """Techniek voor het meten van een aan- of afwezigheid van contact tussen de onderdelen waaraan deze bevestigd is. """

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Contactpunt'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        AIMObject.__init__(self)
        PuntGeometrie.__init__(self)

        self._type = OTLAttribuut(field=KlContactpuntType,
                                  naam='type',
                                  label='type contactpunt',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Contactpunt.type',
                                  definition='Typering van de gebruikte techniek op basis waarvan de aan- of afwezigheid van een contact vastgesteld wordt.',
                                  owner=self)

    @property
    def type(self):
        """Typering van de gebruikte techniek op basis waarvan de aan- of afwezigheid van een contact vastgesteld wordt."""
        return self._type.get_waarde()

    @type.setter
    def type(self, value):
        self._type.set_waarde(value, owner=self)
