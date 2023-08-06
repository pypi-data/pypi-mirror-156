from datetime import datetime

from OTLMOW.Facility.FileFormats.EMInfraImporter import EMInfraImporter
from OTLMOW.Facility.OTLFacility import OTLFacility
from OTLMOW.Facility.RequesterFactory import RequesterFactory
from OTLMOW.Facility.Visualiser import Visualiser
from OTLMOW.OTLModel.Classes.Onderdeel.Bevestiging import Bevestiging
from OTLMOW.OTLModel.Classes.Onderdeel.Flitsgroep import Flitsgroep
from OTLMOW.OTLModel.Classes.Onderdeel.Flitspaalbehuizing import Flitspaalbehuizing
from OTLMOW.OTLModel.Classes.Onderdeel.HoortBij import HoortBij
from OTLMOW.OTLModel.Classes.Onderdeel.Laagspanningsbord import Laagspanningsbord
from OTLMOW.OTLModel.Classes.Onderdeel.Stroomkring import Stroomkring
from OTLMOW.OTLModel.Classes.Onderdeel.Voedt import Voedt
from OTLMOW.OTLModel.Classes.Onderdeel.Wegkantkast import Wegkantkast

if __name__ == '__main__':
    otl_facility = OTLFacility(logfile=r'C:\temp\pythonLogging\python_log.txt',
                               settings_path="C:\\resources\\settings_OTLMOW.json",
                               enable_relation_features=True)

    # add EM-Infra assets through API
    input_uuids = ['6fec1fbf-9037-4daa-976d-4ccd54e2d554', '1c6dbec3-62e6-4e30-8fe1-19ba58a73151',
                   'e88f3270-91ed-4fa8-a605-0969805790d4', 'adbd8726-d026-4c5d-80e1-5343a2fa4d34',
                   '60b2dcaa-69f1-4fac-9062-9c1381eecd2e', '85ab7233-4d69-4702-841e-aace94b42410',
                   'f63bfc00-2951-401e-8dbb-6667a479e0ea']

    requester = RequesterFactory.create_requester(settings=otl_facility.settings, auth_type='JWT', env='prd')
    importer = EMInfraImporter(requester=requester)

    # fetch assets, based on a list of uuids
    assets = importer.import_assets_from_webservice_by_uuids(input_uuids)

    # for each asset, find all relations
    relatie_list = []
    for asset in assets:
        relaties = importer.import_assetrelaties_from_webservice_by_assetuuid(asset.assetId.identificator[0:36])
        relatie_list.extend(relaties)

    assets.extend(relatie_list)

    # use the generated datamodel to create instances of OTL classes
    flitspaalbehuizing1 = Flitspaalbehuizing()
    flitspaalbehuizing1.naam = '360C6.1'
    flitspaalbehuizing1.toestand = 'in-gebruik'
    flitspaalbehuizing1.assetId.identificator = '360C6.1'
    flitspaalbehuizing1.geometry = 'POINT Z (171277.9 173790.9 0)'

    flitsgroep = Flitsgroep()
    flitsgroep.naam = '360C6'
    flitsgroep.assetId.identificator = '360C6'
    flitsgroep.toestand = 'in-gebruik'
    flitsgroep.isRoodLicht = True
    flitsgroep.externeReferentie.externReferentienummer = 'https://bmidata.drive-it.be/sites/sites/321'
    flitsgroep.externeReferentie.externePartij = 'Belgisch Meet Instituut'

    hoortbijrelatie_beh_1 = otl_facility.relatie_creator.create_relation(bron=flitspaalbehuizing1, doel=flitsgroep, relatie=HoortBij)

    # TODO: copy paste flitspaalbehuizing1 + hoortbij

    # voorbeeld SNC 'R23X3.8/421C6/1'
    flitspaalbehuizing3 = Flitspaalbehuizing()
    flitspaalbehuizing3.naam = '421C6.1'
    flitspaalbehuizing3.toestand = 'in-gebruik'
    flitspaalbehuizing3.assetId.identificator = '421C6.1'
    flitspaalbehuizing3.geometry = 'POINT Z (173600.1 173138.6 0)'

    hoortbijrelatie_beh_3_legacy = otl_facility.relatie_creator.create_relation(bron=flitspaalbehuizing3,
                                                                                doel=next(a for a in assets if
                                                                                          a.assetId.identificator[
                                                                                          0:36] == '1c6dbec3-62e6-4e30-8fe1-19ba58a73151'),
                                                                                relatie=HoortBij)

    flitsgroep2 = Flitsgroep()
    flitsgroep2.naam = '421C6'
    flitsgroep2.assetId.identificator = '421C6'
    flitsgroep2.toestand = 'in-gebruik'
    flitsgroep2.isRoodLicht = False

    hoortbijrelatie_flitsgroep2_legacy = otl_facility.relatie_creator.create_relation(bron=flitsgroep2,
                                                                                      doel=next(a for a in assets if
                                                                                                a.assetId.identificator[
                                                                                                0:36] == '6fec1fbf-9037-4daa-976d-4ccd54e2d554'),
                                                                                      relatie=HoortBij)

    hoortbijrelatie_beh_3 = otl_facility.relatie_creator.create_relation(bron=flitspaalbehuizing3, doel=flitsgroep2,
                                                                         relatie=HoortBij)

    str = Stroomkring()
    str.assetId.identificator = '421C6-str'

    hoortbijrelatie_str_legacy = otl_facility.relatie_creator.create_relation(bron=str,
                                                                              doel=next(a for a in assets if
                                                                                        a.assetId.identificator[
                                                                                        0:36] == 'adbd8726-d026-4c5d-80e1-5343a2fa4d34'),
                                                                              relatie=HoortBij)

    voedingsrelatie_str_fp = otl_facility.relatie_creator.create_relation(bron=str, doel=flitspaalbehuizing3, relatie=Voedt)

    lsb = Laagspanningsbord()
    lsb.assetId.identificator = '421C6-lsb'

    hoortbijrelatie_lsb_legacy = otl_facility.relatie_creator.create_relation(bron=lsb,
                                                                              doel=next(a for a in assets if
                                                                                        a.assetId.identificator[
                                                                                        0:36] == 'adbd8726-d026-4c5d-80e1-5343a2fa4d34'),
                                                                              relatie=HoortBij)

    bevestigingsrelatie_str_lsb = otl_facility.relatie_creator.create_relation(bron=lsb, doel=str, relatie=Bevestiging)

    bevestigingsrelatie_meter_lsb = otl_facility.relatie_creator.create_relation(bron=lsb,
                                                                                 doel=next(a for a in assets if
                                                                                           a.assetId.identificator[
                                                                                           0:36] == '85ab7233-4d69-4702-841e-aace94b42410'),
                                                                                 relatie=Bevestiging)

    kast = Wegkantkast()
    kast.naam = 'R23N3.85.K'
    kast.assetId.identificator = 'R23N3.85.K'
    kast.mplan = []

    bevestigingsrelatie_aansluiting_kast = otl_facility.relatie_creator.create_relation(bron=kast,
                                                                                        doel=next(a for a in assets if
                                                                                                  a.assetId.identificator[
                                                                                                  0:36] == 'f63bfc00-2951-401e-8dbb-6667a479e0ea'),
                                                                                        relatie=Bevestiging)

    bevestigingsrelatie_kast_lsb = otl_facility.relatie_creator.create_relation(bron=kast, doel=lsb, relatie=Bevestiging)

    hoortbijrelatie_kast_legacy = otl_facility.relatie_creator.create_relation(bron=kast,
                                                                               doel=next(a for a in assets if
                                                                                         a.assetId.identificator[
                                                                                         0:36] == 'e88f3270-91ed-4fa8-a605-0969805790d4'),
                                                                               relatie=HoortBij)

    voedingsrelatie_str_meter = otl_facility.relatie_creator.create_relation(doel=str,
                                                                             bron=next(a for a in assets if
                                                                                       a.assetId.identificator[
                                                                                       0:36] == '85ab7233-4d69-4702-841e-aace94b42410'),
                                                                             relatie=Voedt)

    lijst_otl_objecten = [flitspaalbehuizing1, flitsgroep, hoortbijrelatie_beh_1, flitspaalbehuizing3, flitsgroep2,
                          hoortbijrelatie_beh_3, str, voedingsrelatie_str_fp, lsb, bevestigingsrelatie_str_lsb, kast,
                          bevestigingsrelatie_kast_lsb, hoortbijrelatie_beh_3_legacy, hoortbijrelatie_flitsgroep2_legacy,
                          hoortbijrelatie_str_legacy, hoortbijrelatie_lsb_legacy, hoortbijrelatie_kast_legacy,
                          voedingsrelatie_str_meter, bevestigingsrelatie_aansluiting_kast, bevestigingsrelatie_meter_lsb]

    # export as json file
    filepath = f'Output/{datetime.now().strftime("%Y%m%d%H%M%S")}_export_RLC_SNC.json'
    otl_facility.create_file_from_assets(list_of_objects=lijst_otl_objecten, filepath=filepath)

    lijst_otl_objecten.extend(assets)

    Visualiser().show(lijst_otl_objecten)
