# -*- coding: utf-8 -*-
"""
Submodule of calorine containing `nep_cpu` interface.
"""

from .nep import get_descriptors, get_potential_forces_and_virials
from .cpunep_calculator import CPUNEP

__all__ = ['CPUNEP',
           'get_descriptors',
           'get_potential_forces_and_virials']
