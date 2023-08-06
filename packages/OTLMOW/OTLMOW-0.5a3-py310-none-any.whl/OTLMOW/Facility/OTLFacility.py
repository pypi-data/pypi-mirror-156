import json
import logging
import os
from os.path import abspath

from OTLMOW.Facility.FileExporter import FileExporter
from OTLMOW.Facility.FileImporter import FileImporter
from OTLMOW.Facility.RelatieCreator import RelatieCreator
from OTLMOW.Facility.RequesterFactory import RequesterFactory
from OTLMOW.GeometrieArtefact.GeometrieArtefactCollector import GeometrieArtefactCollector
from OTLMOW.GeometrieArtefact.GeometrieInMemoryCreator import GeometrieInMemoryCreator
from OTLMOW.ModelGenerator.BaseClasses.RelatieValidator import RelatieValidator
from OTLMOW.ModelGenerator.OSLOCollector import OSLOCollector
from OTLMOW.ModelGenerator.OSLOInMemoryCreator import OSLOInMemoryCreator
from OTLMOW.ModelGenerator.OTLModelCreator import OTLModelCreator
from OTLMOW.ModelGenerator.SQLDbReader import SQLDbReader
from OTLMOW.OEFModel.ModelGrabber import ModelGrabber
from OTLMOW.OEFModel.OEFModelCreator import OEFModelCreator
from OTLMOW.OTLModel.GeldigeRelatieLijst import GeldigeRelatieLijst
from OTLMOW.PostenMapping.PostenCollector import PostenCollector
from OTLMOW.PostenMapping.PostenCreator import PostenCreator
from OTLMOW.PostenMapping.PostenInMemoryCreator import PostenInMemoryCreator


class OTLFacility:
    def __init__(self,
                 settings_path: str = '',
                 logging_level: int = logging.WARNING, logfile: str = 'logs.txt',
                 enable_relation_features: bool = False):
        """Main utility class for creating a model, importing and exporting assets from files and enabling validation features

        :param settings_path: specifies the location of the settings file this library loads. Defaults to the example that is supplied with the library ('OTLMOW/Facility/settings_sample.json')
        :type settings_path: str
        :param logging_level: specifies the level of logging that is used for actions with this class
        :type logging_level: int
        :param logfile: specifies the path to the logfile.
        :type logfile: str
        :param enable_relation_features: specifies whether to enable the relation features such as validation
        :type enable_relation_features: bool
        """
        self.settings: dict = {}
        self._load_settings(settings_path)

        if logging_level != 0 and logfile != '':
            logging.basicConfig(filename=logfile,
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging_level)

        self.oef_model_creator: None | OEFModelCreator = None
        self.posten_collector = None
        self.posten_creator = None
        self.relatie_validator: None | RelatieValidator = None
        self.relatie_creator: None | RelatieCreator = None

        if enable_relation_features:
            self._init_relatie_validation()

    def create_otl_datamodel(self, directory: str = '',
                             otl_sqlite_file_location: str = '',
                             geo_artefact_sqlite_file_location: str = '') -> None:
        """Creates a datamodel given an OTL SQLite database in the specified directory. This will also use a Geometry Artefact if specified

        :param directory: directory where the model classes will be created, including the OTLModel directory. If not specified, this will create a model in a directory OTLModel in the same directory as the script that runs this method
        :type: str
        :param otl_sqlite_file_location: path to the OTL SQLite file
        :type: str
        :param geo_artefact_sqlite_file_location: path to the Geometry Artefact SQLite file. Defaults to an empty string as this file is not mandatory to create a model
        :type: str

        :return: Nothing is returned, instead the datamodel files are created in the specified directory
        :rtype: None
        """
        model_creator = self._init_otl_model_creator(otl_sqlite_file_location, geo_artefact_sqlite_file_location)
        self._create_otl_datamodel(model_creator, directory)

    def create_oef_datamodel(self, oef_file_location: str = '', ins_ond_file_location: str = '',
                             auth_type: str = 'JWT', env: str = 'prd') -> None:
        # TODO
        """Creates a datamodel given an OTL SQLite database in the specified directory. This will also use a Geometry Artefact if specified

        :param oef_file_location: path to the OEF SQLite file
        :type: str
        :param ins_ond_file_location: path to the OTL SQLite file
        :type: str
        :param geo_artefact_sqlite_file_location: path to the Geometry Artefact SQLite file. Defaults to an empty string as this file is not mandatory to create a model
        :type: str

        :return: Nothing is returned, instead the datamodel files are created in the specified directory
        :rtype: None
        """
        oef_model_creator = self._init_oef_model_creator(oef_file_location=oef_file_location,
                                                         ins_ond_file_location=ins_ond_file_location,
                                                         auth_type=auth_type, env=env)
        oef_model_creator.create_full_model()

    def create_posten_model(self, postenmaping_file_location) -> None:
        """Creates a posten model given a SQLite database.

        :param postenmaping_file_location: path to the SQLite file of the postenmapping
        :type: str

        :return: Nothing is returned, instead the datamodel files are created
        :rtype: None
        """
        collector = self._init_postenmapping_collector(postenmaping_file_location)
        collector.collect()
        creator = PostenCreator(collector)
        creator.create_all_mappings()

    def create_assets_from_file(self, filepath: str, **kwargs) -> list:
        """Creates asset objects in memory from a file. Supports csv and json files.

        :param filepath: Path to the file that is to be imported
        :type: str

        Supported arguments for csv:

        delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'

        Supported arguments for json:

        ignore_failed_objects (bool): If True, suppresses the errors resulting from the creation of one object,
        to allow the collection of all non-erroneous objects. Defaults to False

        :return: Returns a list with asset objects
        :rtype: list
        """
        file_importer = FileImporter(settings=self.settings)
        return file_importer.create_assets_from_file(filepath=filepath, **kwargs)

    def create_file_from_assets(self, filepath: str, list_of_objects: list, **kwargs) -> None:
        """Creates a file from asset objects in memory. Supports csv and json files.

        :param filepath: Path to the file that is to be created
        :type: str

        Supported arguments for csv:

        delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'
        split_per_type (bool): If True, creates a file per type instead of one file for all objects

        :return: Returns a list with asset objects
        :rtype: list
        """
        file_exporter = FileExporter(settings=self.settings)
        return file_exporter.create_file_from_assets(filepath=filepath, list_of_objects=list_of_objects, **kwargs)

    def _init_relatie_validation(self, relation_list: [GeldigeRelatieLijst] = None):
        if relation_list is None:
            relation_list = GeldigeRelatieLijst().lijst
        self.relatie_validator = RelatieValidator(relation_list)
        self.relatie_validator.enableValidateRelatieOnRelatieInteractor()
        self.relatie_creator = RelatieCreator(self.relatie_validator)

    @staticmethod
    def _init_otl_model_creator(otl_file_location: str = '', geoA_file_location: str = '') -> OTLModelCreator:
        sql_reader = SQLDbReader(otl_file_location)
        oslo_creator = OSLOInMemoryCreator(sql_reader)
        collector = OSLOCollector(oslo_creator)
        geo_artefact_collector = None
        if geoA_file_location != '':
            sql_reader_GA = SQLDbReader(geoA_file_location)
            geo_memory_creator = GeometrieInMemoryCreator(sql_reader_GA)
            geo_artefact_collector = GeometrieArtefactCollector(geo_memory_creator)
        return OTLModelCreator(collector, geo_artefact_collector)

    @staticmethod
    def _create_otl_datamodel(model_creator: OTLModelCreator, directory: str = ''):
        model_creator.oslo_collector.collect()
        if model_creator.geo_artefact_collector is not None:
            model_creator.geo_artefact_collector.collect()
        if directory == '':
            base_dir = os.path.dirname(os.path.realpath(__file__))
            directory = abspath(f'{base_dir}/../')
        model_creator.create_full_model(directory=directory)

    def _init_postenmapping_collector(self, postenmaping_file_location: str = '') -> PostenCollector:
        sql_reader = SQLDbReader(postenmaping_file_location)
        oslo_creator = PostenInMemoryCreator(sql_reader)
        return PostenCollector(oslo_creator)

    def _init_oef_model_creator(self, oef_file_location: str, ins_ond_file_location: str, auth_type: str, env: str):
        requester = RequesterFactory.create_requester(settings=self.settings, auth_type=auth_type, env=env)
        model_grabber = ModelGrabber(requester)
        model_grabber.grab_models_as_json(oef_file_location, ins_ond_file_location)
        classes = model_grabber.decode_json_and_get_classes(oef_file_location)
        attributen = model_grabber.decode_json_and_get_attributen(oef_file_location)
        ins_ond_classes = model_grabber.decode_json_and_get_classes(ins_ond_file_location)
        self._extend_classes_with_ond_ins(classes, ins_ond_classes)
        ins_ond_attributen = model_grabber.decode_json_and_get_attributen(ins_ond_file_location)
        attributen.extend(ins_ond_attributen)
        return OEFModelCreator(classes=classes, attributen=attributen)

    @staticmethod
    def _extend_classes_with_ond_ins(classes, ins_ond_classes):
        for cls in classes:
            ins_ond_cls = next((c for c in ins_ond_classes if c["uri"] == cls["uri"]), None)
            if ins_ond_cls is None:
                continue
            cls["attributen"].extend(ins_ond_cls["attributen"])

    def _load_settings(self, settings_path):
        if settings_path == '':
            base_dir = os.path.dirname(os.path.realpath(__file__))
            settings_path = abspath(f'{base_dir}\\settings_sample.json')

        if not os.path.isfile(settings_path):
            raise FileNotFoundError(settings_path + " is not a valid path. File does not exist.")

        try:
            with open(settings_path) as settings_file:
                self.settings = json.load(settings_file)
        except OSError:
            raise ImportError(f'Could not open the settings file at {settings_file}')
