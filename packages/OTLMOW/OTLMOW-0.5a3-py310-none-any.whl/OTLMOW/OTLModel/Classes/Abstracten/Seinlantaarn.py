# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from abc import abstractmethod
from OTLMOW.OTLModel.Classes.ImplementatieElement.AIMNaamObject import AIMNaamObject
from OTLMOW.OTLModel.Datatypes.BooleanField import BooleanField
from OTLMOW.OTLModel.Datatypes.KlLantaarnVormgeving import KlLantaarnVormgeving
from OTLMOW.OTLModel.Datatypes.KlSeinlantaarnDiameter import KlSeinlantaarnDiameter
from OTLMOW.OTLModel.Datatypes.KlSeinlantaarnMerk import KlSeinlantaarnMerk
from OTLMOW.OTLModel.Datatypes.KlSeinlantaarnModelnaam import KlSeinlantaarnModelnaam
from OTLMOW.GeometrieArtefact.PuntGeometrie import PuntGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class Seinlantaarn(AIMNaamObject, PuntGeometrie):
    """Abstracte voor het geheel van één of meerdere verkeerslichten die boven elkaar worden opgesteld en worden bevestigd op een steun,teneinde de beweging van een weggebruiker die een bepaald traject volgt,te verhinderen of toe te laten."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        AIMNaamObject.__init__(self)
        PuntGeometrie.__init__(self)

        self._diameter = OTLAttribuut(field=KlSeinlantaarnDiameter,
                                      naam='diameter',
                                      label='diameter',
                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn.diameter',
                                      definition='Diameter (in mm) van de lens van de verkeerslichten waaruit de lantaarn is samengesteld.',
                                      owner=self)

        self._heeftContrastscherm = OTLAttribuut(field=BooleanField,
                                                 naam='heeftContrastscherm',
                                                 label='heeft contrastscherm aanwezig',
                                                 objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn.heeftContrastscherm',
                                                 definition='Aanduiding of er een contrastscherm aanwezig is op de lantaarn.',
                                                 owner=self)

        self._merk = OTLAttribuut(field=KlSeinlantaarnMerk,
                                  naam='merk',
                                  label='merk',
                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn.merk',
                                  definition='Het merk van een de seinlantaarn.',
                                  owner=self)

        self._modelnaam = OTLAttribuut(field=KlSeinlantaarnModelnaam,
                                       naam='modelnaam',
                                       label='modelnaam',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn.modelnaam',
                                       definition='De modelnaam/product range van de seinlantaarn.',
                                       owner=self)

        self._vormgeving = OTLAttribuut(field=KlLantaarnVormgeving,
                                        naam='vormgeving',
                                        label='vormgeving',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn.vormgeving',
                                        definition='Type vormgeving van de seinlantaarn.',
                                        owner=self)

    @property
    def diameter(self):
        """Diameter (in mm) van de lens van de verkeerslichten waaruit de lantaarn is samengesteld."""
        return self._diameter.get_waarde()

    @diameter.setter
    def diameter(self, value):
        self._diameter.set_waarde(value, owner=self)

    @property
    def heeftContrastscherm(self):
        """Aanduiding of er een contrastscherm aanwezig is op de lantaarn."""
        return self._heeftContrastscherm.get_waarde()

    @heeftContrastscherm.setter
    def heeftContrastscherm(self, value):
        self._heeftContrastscherm.set_waarde(value, owner=self)

    @property
    def merk(self):
        """Het merk van een de seinlantaarn."""
        return self._merk.get_waarde()

    @merk.setter
    def merk(self, value):
        self._merk.set_waarde(value, owner=self)

    @property
    def modelnaam(self):
        """De modelnaam/product range van de seinlantaarn."""
        return self._modelnaam.get_waarde()

    @modelnaam.setter
    def modelnaam(self, value):
        self._modelnaam.set_waarde(value, owner=self)

    @property
    def vormgeving(self):
        """Type vormgeving van de seinlantaarn."""
        return self._vormgeving.get_waarde()

    @vormgeving.setter
    def vormgeving(self, value):
        self._vormgeving.set_waarde(value, owner=self)
