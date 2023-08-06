# from qb_core.rats_pkg.cook import _cook_persistence
#
#
# def add_cook(cook):
#     _cook_persistence.save_cook(cook)
#
#
# def remove_cook(cook):
#     _cook_persistence.remove_cook(cook)


# from qb_core.rats_pkg.cook.cook_persistence_core import CookPersistenceCore
#
# _cook_persistence = CookPersistenceCore()
from qb_core.common.plugin.peristence import PersistencePluginManager

_cook_persistence = None


def initialize():
    global _cook_persistence
    _cook_persistence = PersistencePluginManager.get_persistence_implementation(
        "cook_persistence_interface")


def add_cook(cook):
    _cook_persistence.save_cook(cook)


def remove_cook(cook):
    _cook_persistence.remove_cook(cook)
