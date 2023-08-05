"""
use this module to initialize the whole app

Note setuptools is not picking this up
probably because this module is directly off of src
"""
import qb_core.oproc_pkg.oproc
import qb_core.rats_pkg.rats
import qb_core.ocra_pkg.ocra


def initialize_app():
    qb_core.rats_pkg.rats.initialize_module()
    qb_core.oproc_pkg.oproc.initialize_module()
    qb_core.ocra_pkg.ocra.initialize_module()
