# coding=utf-8
import random
from OTLMOW.OTLModel.Datatypes.KeuzelijstField import KeuzelijstField
from OTLMOW.OTLModel.Datatypes.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlWegbebakeningType(KeuzelijstField):
    """De vormen van wegbebakening."""
    naam = 'KlWegbebakeningType'
    label = 'Wegbebakening type'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#KlWegbebakeningType'
    definition = 'De vormen van wegbebakening.'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlWegbebakeningType'
    options = {
        'type-1-(new-jersey-reclip)': KeuzelijstWaarde(invulwaarde='type-1-(new-jersey-reclip)',
                                                       label='type 1 (new jersey reclip)',
                                                       definitie='type 1 (new jersey reclip)',
                                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlWegbebakeningType/type-1-(new-jersey-reclip)'),
        'type-2-(new-jersey)': KeuzelijstWaarde(invulwaarde='type-2-(new-jersey)',
                                                label='type 2 (new jersey)',
                                                definitie='type 2 (new jersey)',
                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlWegbebakeningType/type-2-(new-jersey)'),
        'type-3-(referentiepaal)': KeuzelijstWaarde(invulwaarde='type-3-(referentiepaal)',
                                                    label='type 3 (referentiepaal)',
                                                    definitie='type 3 (referentiepaal)',
                                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlWegbebakeningType/type-3-(referentiepaal)'),
        'type-A-(vangrail-reclip)': KeuzelijstWaarde(invulwaarde='type-A-(vangrail-reclip)',
                                                     label='type A (vangrail reclip)',
                                                     definitie='type A (vangrail reclip)',
                                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlWegbebakeningType/type-A-(vangrail-reclip)'),
        'type-B-(vangrail)': KeuzelijstWaarde(invulwaarde='type-B-(vangrail)',
                                              label='type B (vangrail)',
                                              definitie='type B (vangrail)',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlWegbebakeningType/type-B-(vangrail)'),
        'type-C-(vangrail-trapezium)': KeuzelijstWaarde(invulwaarde='type-C-(vangrail-trapezium)',
                                                        label='type C (vangrail trapezium)',
                                                        definitie='Type C (vangrail trapezium)',
                                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlWegbebakeningType/type-C-(vangrail-trapezium)')
    }

    @classmethod
    def get_dummy_data(cls):
        return random.choice(list(cls.options.keys()))

    @staticmethod
    def create_dummy_data():
        return KlWegbebakeningType.get_dummy_data()

