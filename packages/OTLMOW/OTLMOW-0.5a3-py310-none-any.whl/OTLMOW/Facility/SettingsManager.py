import json

from OTLMOW.Facility.DotnotationHelper import DotnotationHelper
from OTLMOW.Facility.Singleton import Singleton


class SettingsManager(metaclass=Singleton):
    def __init__(self, settings_path: str = ''):
        self.settings: dict = {}
        if settings_path != '':
            self.load_settings_from_file(settings_path)

    def load_settings_from_file(self, settings_path):
        with open(settings_path) as settings_file:
            self.settings = json.load(settings_file)
        if self.settings is not None:
            self.load_settings_in_app()

    def load_settings_in_app(self):
        if 'file_formats' in self.settings:
            otlmow_format = next((f for f in self.settings['file_formats'] if f['name'] == 'OTLMOW'), None)
            if otlmow_format is not None and 'dotnotation' in otlmow_format:
                if 'separator' in otlmow_format['dotnotation']:
                    DotnotationHelper.separator = otlmow_format['dotnotation']['separator']
                if 'cardinality separator' in otlmow_format['dotnotation']:
                    DotnotationHelper.cardinality_separator = otlmow_format['dotnotation']['cardinality separator']
                if 'cardinality indicator' in otlmow_format['dotnotation']:
                    DotnotationHelper.cardinality_indicator = otlmow_format['dotnotation']['cardinality indicator']
                if 'waarde_shortcut_applicable' in otlmow_format['dotnotation']:
                    DotnotationHelper.waarde_shortcut_applicable = otlmow_format['dotnotation']['waarde_shortcut_applicable']
