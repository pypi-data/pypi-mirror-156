import importlib


class PersistencePluginManager:
    persistence_obj = None

    @classmethod
    def initialize(cls, persistence_key):
        if persistence_key == "core":
            module = importlib.import_module("qb_core.rats_pkg.cook.cook_persistence_core")
            cls.persistence_obj = module.get_implementation()
        else:
            module = importlib.import_module("qb_core.rats_pkg.cook.cook_persistence_core")
            cls.persistence_obj = module.get_implementation()

    @classmethod
    def get_persistence_implementation(cls):
        return cls.persistence_obj



