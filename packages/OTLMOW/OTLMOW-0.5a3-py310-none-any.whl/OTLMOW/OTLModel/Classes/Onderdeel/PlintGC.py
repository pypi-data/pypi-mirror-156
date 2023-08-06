# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Abstracten.BetonnenConstructieElement import BetonnenConstructieElement
from OTLMOW.OTLModel.Classes.Abstracten.ConstructieElement import ConstructieElement
from OTLMOW.OTLModel.Classes.Abstracten.ConstructieElementenGC import ConstructieElementenGC
from OTLMOW.OTLModel.Datatypes.DtcAfmetingBxlxhInM import DtcAfmetingBxlxhInM
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument
from OTLMOW.OTLModel.Datatypes.KlPlaatsingswijzePlint import KlPlaatsingswijzePlint
from OTLMOW.GeometrieArtefact.LijnGeometrie import LijnGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class PlintGC(BetonnenConstructieElement, ConstructieElement, ConstructieElementenGC, LijnGeometrie):
    """Een plint is een betonnen balk/plaat die de akoestische dichtheid verzekert tussen de schermelementen van de geluidswerende constructie en de bodem."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#PlintGC'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        BetonnenConstructieElement.__init__(self)
        ConstructieElement.__init__(self)
        ConstructieElementenGC.__init__(self)
        LijnGeometrie.__init__(self)

        self._afmetingen = OTLAttribuut(field=DtcAfmetingBxlxhInM,
                                        naam='afmetingen',
                                        label='afmetingen',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#PlintGC.afmetingen',
                                        definition='Met dit complex datatype worden de afmetingen van de plint weergegeven. Indien de plint afwijkt van een rechthoekige vorm wordt deze informatie in de technische fiche opgeslagen.',
                                        owner=self)

        self._plaatsingswijze = OTLAttribuut(field=KlPlaatsingswijzePlint,
                                             naam='plaatsingswijze',
                                             label='plaatsingswijze',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#PlintGC.plaatsingswijze',
                                             definition='De manier waarop de plint geplaatst is ten opzichte van de profielen.',
                                             owner=self)

        self._technischeFiche = OTLAttribuut(field=DtcDocument,
                                             naam='technischeFiche',
                                             label='technische fiche',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#PlintGC.technischeFiche',
                                             definition='Document met verdere specificaties van de plint die niet opgevangen worden met de aanwezige attributen.',
                                             owner=self)

    @property
    def afmetingen(self):
        """Met dit complex datatype worden de afmetingen van de plint weergegeven. Indien de plint afwijkt van een rechthoekige vorm wordt deze informatie in de technische fiche opgeslagen."""
        return self._afmetingen.get_waarde()

    @afmetingen.setter
    def afmetingen(self, value):
        self._afmetingen.set_waarde(value, owner=self)

    @property
    def plaatsingswijze(self):
        """De manier waarop de plint geplaatst is ten opzichte van de profielen."""
        return self._plaatsingswijze.get_waarde()

    @plaatsingswijze.setter
    def plaatsingswijze(self, value):
        self._plaatsingswijze.set_waarde(value, owner=self)

    @property
    def technischeFiche(self):
        """Document met verdere specificaties van de plint die niet opgevangen worden met de aanwezige attributen."""
        return self._technischeFiche.get_waarde()

    @technischeFiche.setter
    def technischeFiche(self, value):
        self._technischeFiche.set_waarde(value, owner=self)
