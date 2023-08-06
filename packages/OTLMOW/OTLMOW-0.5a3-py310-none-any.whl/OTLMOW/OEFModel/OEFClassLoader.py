﻿class OEFClassLoader:
    @staticmethod
    def dynamic_create_instance_from_name(class_name):
        try:
            py_mod = __import__(name=f'OTLMOW.OEFModel.Classes.{class_name}', fromlist=f'Classes.{class_name}')
        except ModuleNotFoundError as exc:
            return None
        class_ = getattr(py_mod, class_name)
        instance = class_()

        return instance

    def dynamic_create_instance_from_uri(self, class_uri):
        class_name = class_uri.split('#')[-1]
        return self.dynamic_create_instance_from_name(class_name)
