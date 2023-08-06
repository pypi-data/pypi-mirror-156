# from qb_core.rats_pkg.cook import _cook_persistence
#
#
# def add_cook(cook):
#     _cook_persistence.save_cook(cook)
#
#
# def remove_cook(cook):
#     _cook_persistence.remove_cook(cook)


from qb_core.rats_pkg.cook.cook_persistence_core import CookPersistenceCore

_cook_persistence = CookPersistenceCore()


def add_cook(cook):
    _cook_persistence.save_cook(cook)


def remove_cook(cook):
    _cook_persistence.remove_cook(cook)