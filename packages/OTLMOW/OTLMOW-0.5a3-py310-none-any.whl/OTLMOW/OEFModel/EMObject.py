from OTLMOW.GeometrieArtefact.PuntGeometrie import PuntGeometrie
from OTLMOW.OEFModel.DtcBeheerder import DtcBeheerder
from OTLMOW.OEFModel.DtcToezichtGroep import DtcToezichtGroep
from OTLMOW.OEFModel.DtcToezichter import DtcToezichter
from OTLMOW.OEFModel.EMAttribuut import EMAttribuut
from OTLMOW.OTLModel.Classes.ImplementatieElement.NaampadObject import NaampadObject
from OTLMOW.OTLModel.Datatypes.StringField import StringField


class EMObject(NaampadObject, PuntGeometrie):
    def __init__(self):
        NaampadObject.__init__(self)
        PuntGeometrie.__init__(self)

        self._omschrijving = EMAttribuut(field=StringField,
                                         naam='locatie omschrijving',
                                         label='locatie omschrijving',
                                         objectUri='https://loc.data.wegenenverkeer.be/ns/attribuut#EMObject.Locatie.omschrijving',
                                         definitie='Definitie nog toe te voegen voor eigenschap locatie omschrijving aanwezig')

        self._toezichtgroep = EMAttribuut(field=DtcToezichtGroep,
                                          naam='toezichtgroep',
                                          label='toezichtgroep',
                                          objectUri='https://tz.data.wegenenverkeer.be/ns/implementatieelement#Toezicht.toezichtgroep',
                                          definitie='De toezichtgroep van een asset.')

        self._toezichter = EMAttribuut(field=DtcToezichter,
                                       naam='toezichter',
                                       label='toezichter',
                                       objectUri='https://tz.data.wegenenverkeer.be/ns/implementatieelement#Toezicht.toezichter',
                                       definitie='De toezichter van een asset.')

        self._schadebeheerder = EMAttribuut(field=DtcBeheerder,
                                            naam='schadebeheerder',
                                            label='schadebeheerder',
                                            objectUri='https://tz.data.wegenenverkeer.be/ns/implementatieelement#Schadebeheerder.schadebeheerder',
                                            definitie='De schadebeheerder  van een asset.')

    @property
    def schadebeheerder(self):
        """De schadebeheerder van een asset."""
        return self._schadebeheerder.waarde

    @schadebeheerder.setter
    def schadebeheerder(self, value):
        self._schadebeheerder.set_waarde(value, owner=self)

    @property
    def toezichter(self):
        """De toezichter van een asset."""
        return self._toezichter.waarde

    @toezichter.setter
    def toezichter(self, value):
        self._toezichter.set_waarde(value, owner=self)

    @property
    def toezichtgroep(self):
        """De toezichtgroep van een asset."""
        return self._toezichtgroep.waarde

    @toezichtgroep.setter
    def toezichtgroep(self, value):
        self._toezichtgroep.set_waarde(value, owner=self)

    @property
    def omschrijving(self):
        """Definitie nog toe te voegen voor eigenschap locatie omschrijving aanwezig"""
        return self._omschrijving.waarde

    @omschrijving.setter
    def omschrijving(self, value):
        self._omschrijving.set_waarde(value, owner=self)
