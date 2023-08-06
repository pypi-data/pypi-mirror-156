# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Abstracten.BevestigingGC import BevestigingGC
from OTLMOW.OTLModel.Classes.ImplementatieElement.AIMNaamObject import AIMNaamObject
from OTLMOW.OTLModel.Datatypes.BooleanField import BooleanField
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument
from OTLMOW.OTLModel.Datatypes.KlBevestigingsbeugelType import KlBevestigingsbeugelType


# Generated with OTLClassCreator. To modify: extend, do not edit
class Bevestigingsbeugel(BevestigingGC, AIMNaamObject):
    """Verbindingsstuk waarmee een object kan vastgemaakt worden aan een steun of oppervlak."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestigingsbeugel'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        AIMNaamObject.__init__(self)
        BevestigingGC.__init__(self)

        self._berekeningsnota = OTLAttribuut(field=DtcDocument,
                                             naam='berekeningsnota',
                                             label='berekeningsnota',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestigingsbeugel.berekeningsnota',
                                             usagenote='Bestanden van het type xlsx of pdf.',
                                             kardinaliteit_max='*',
                                             definition='Document met de berekeningsnota van de bevestigingsbeugel.',
                                             owner=self)

        self._constructieEnMontageplan = OTLAttribuut(field=DtcDocument,
                                                      naam='constructieEnMontageplan',
                                                      label='constructie en montageplan',
                                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestigingsbeugel.constructieEnMontageplan',
                                                      usagenote='Bestanden van het type dwg of pdf.',
                                                      kardinaliteit_max='*',
                                                      definition='Document met het constructie- en montageplan van de bevestigingsbeugel.',
                                                      owner=self)

        self._isVerzegeld = OTLAttribuut(field=BooleanField,
                                         naam='isVerzegeld',
                                         label='is verzegeld',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestigingsbeugel.isVerzegeld',
                                         definition='Geeft aan of de bevestigingsbeugel verzegeld is tegen het ongemerkt losmaken ervan.',
                                         owner=self)

        self._type = OTLAttribuut(field=KlBevestigingsbeugelType,
                                  naam='type',
                                  label='type',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestigingsbeugel.type',
                                  definition='Het type van de bevestigingsbeugel.',
                                  owner=self)

    @property
    def berekeningsnota(self):
        """Document met de berekeningsnota van de bevestigingsbeugel."""
        return self._berekeningsnota.get_waarde()

    @berekeningsnota.setter
    def berekeningsnota(self, value):
        self._berekeningsnota.set_waarde(value, owner=self)

    @property
    def constructieEnMontageplan(self):
        """Document met het constructie- en montageplan van de bevestigingsbeugel."""
        return self._constructieEnMontageplan.get_waarde()

    @constructieEnMontageplan.setter
    def constructieEnMontageplan(self, value):
        self._constructieEnMontageplan.set_waarde(value, owner=self)

    @property
    def isVerzegeld(self):
        """Geeft aan of de bevestigingsbeugel verzegeld is tegen het ongemerkt losmaken ervan."""
        return self._isVerzegeld.get_waarde()

    @isVerzegeld.setter
    def isVerzegeld(self, value):
        self._isVerzegeld.set_waarde(value, owner=self)

    @property
    def type(self):
        """Het type van de bevestigingsbeugel."""
        return self._type.get_waarde()

    @type.setter
    def type(self, value):
        self._type.set_waarde(value, owner=self)
