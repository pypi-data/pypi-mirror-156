.. index::
   single: Function reference; Calculators

ASE calculators
===============

:program:`Calorine` provides two ASE calculators for NEP calculations,
one that uses the GPU implementation and one that uses the CPU implementation
of NEP. The former is better tested but is likely to be slow if many
calculations are to performed, since it relies on reading and writing
files. 

GPU calculator
--------------

.. currentmodule:: calorine.gpunep_calculator

.. autoclass:: GPUNEP
   :members: run_custom_md, set_atoms, set_directory, single_point_parameters, command

CPU calculator
--------------

.. currentmodule:: calorine.nepy.cpunep_calculator

.. autoclass:: CPUNEP
   :members: set_atoms