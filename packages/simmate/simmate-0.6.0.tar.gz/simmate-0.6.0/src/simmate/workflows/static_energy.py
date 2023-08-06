# -*- coding: utf-8 -*-

"""
Workflows for calculating the energy of material
"""

# TODO: when I add more calculators, I can do something like this...
# if "simmate.calculators.vasp" in installed_apps:
from simmate.calculators.vasp.workflows.static_energy import (
    mit_workflow,
    quality04_workflow,
    matproj_workflow,
    neb_endpoint_workflow,
)
