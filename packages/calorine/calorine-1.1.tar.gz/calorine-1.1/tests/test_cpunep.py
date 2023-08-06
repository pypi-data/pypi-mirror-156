import pytest
import contextlib
import numpy as np
from ase import Atoms
from calorine.nepy import CPUNEP
from calorine import GPUNEP

vacuum_cell = ([100, 0, 0], [0, 100, 0], [0, 0, 100])
PbTe = Atoms('TePb', positions=[(0, 0, 0), (0, 0.0, 1.1)],
             cell=vacuum_cell)
C = Atoms('C', positions=[(0, 0, 0)],
          cell=vacuum_cell)
CO = Atoms('CO', positions=[(0, 0, 0), (0, 0.0, 1.1)],
           cell=vacuum_cell)
CC = Atoms('CC', positions=[(0, 0, 0), (0, 0.0, 1.1)],
           cell=vacuum_cell)
CON = Atoms('CON', positions=[(0, 0, 0), (0, 0.0, 1.1), (0, 0.0, 2.2)],
            cell=vacuum_cell)


# --- get_potential_forces_and_virials ---
def test_get_potential_and_forces_NEP3():
    """NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)
    PbTe.calc = calc
    energy = PbTe.get_potential_energy()
    forces = PbTe.get_forces()

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP3_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_and_forces_set_atoms_constructor():
    """Set atoms directly when creating the calculator"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    CPUNEP(nep3, atoms=PbTe)
    energy = PbTe.get_potential_energy()
    forces = PbTe.get_forces()

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP3_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_and_forces_set_atoms_calculate():
    """Set atoms directly when calling calculate on the calculator"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)
    calc.calculate(atoms=PbTe)
    results = calc.results
    energy, energies, forces = results['energy'], results['energies'], results['forces']

    assert energy.shape == ()
    assert energies.shape == (2,)  # Per atom (makes no physical sense)
    assert forces.shape == (2, 3)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP3_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_NEP3_debug(tmpdir):
    """Compares result with debug flag enabled."""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3, debug=True)
    p = tmpdir.join('nep_out.tmp')
    with open(p, 'w') as f:
        with contextlib.redirect_stdout(f):
            with contextlib.redirect_stderr(f):
                PbTe.calc = calc
                PbTe.get_potential_energy()
                PbTe.get_forces()
    with open(p, 'r') as f:
        lines = p.readlines()
        print(lines)
        assert lines[0] == 'Use the NEP3 potential with 2 atom type(s).\n'
        assert len(lines) == 16


def test_get_potential_and_forces_dummy_NEP2():
    """Dummy NEP2 model supplied. Compares results to output from `nep_cpu` for another system"""
    nep2 = 'tests/nep_models/CO_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    CO.calc = calc
    energy = CO.get_potential_energy()
    forces = CO.get_forces()

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/CO_2atom_NEP2_dummy_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_and_forces_several_different_species():
    """Check that forces are correct for a CON system.
    Note that these forces should be exactly zero for this system
    since the NEP2 dummy potential treats all atom species as identical atm."""
    nep2 = 'tests/nep_models/CON_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    CON.calc = calc
    energy = CON.get_potential_energy()
    forces = CON.get_forces()

    assert energy.shape == ()
    assert forces.shape == (3, 3)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/CON_3atom_NEP2_dummy_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(forces, np.zeros((3, 3)), atol=1e-12, rtol=0)


def test_get_potential_and_forces_dummy_NEP2_independent_of_species():
    """Dummy NEP2 energies and forces should be independent of atom species"""
    nep2 = 'tests/nep_models/PbTe_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    PbTe.calc = calc
    PbTe_energy = PbTe.get_potential_energy()
    PbTe_forces = PbTe.get_forces()

    nep2 = 'tests/nep_models/CO_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    CO.calc = calc
    CO_energy = CO.get_potential_energy()
    CO_forces = CO.get_forces()

    expected_forces_CO = np.loadtxt(
        'tests/expected_descriptors/CO_2atom_NEP2_dummy_force.out')

    assert np.allclose(PbTe_energy, CO_energy, atol=1e-12, rtol=0)
    assert np.allclose(PbTe_forces, CO_forces, atol=1e-12, rtol=0)
    assert np.allclose(CO_forces, expected_forces_CO, atol=1e-12, rtol=0)


def test_get_potential_and_forces_update_positions():
    """Update the positions and make sure that the energies and forces are also updated"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()

    # Move atoms slightly
    copy.set_positions([[0, 0, 0], [0, 0, 2.2]])
    energy_after = copy.get_potential_energy()
    forces_after = copy.get_forces()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    assert np.isclose(diff_energy, 1.80751674, atol=1e-8, rtol=0)
    assert np.allclose(diff_force, [[0, 0, 4.65672972], [0, 0, -4.65672972]], atol=1e-8, rtol=0)


def test_get_potential_and_forces_update_cell():
    """Update the cell and make sure that the energies and forces are still the same"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()

    # Change box
    copy.set_cell([[20, 0, 0], [0, 20, 0], [0, 0, 20]], scale_atoms=True)

    energy_after = copy.get_potential_energy()
    forces_after = copy.get_forces()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    assert np.isclose(diff_energy, 0.72005750, atol=1e-8, rtol=0)
    assert np.allclose(diff_force, [[0, 0, 6.58735098], [0, 0, -6.58735098]], atol=1e-8, rtol=0)


def test_get_potential_and_forces_update_numbers():
    """Update the atom numbers (species) and make sure that the
    energies and forces are also updated
    """
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()

    # Change atomic numbers
    copy.set_atomic_numbers([82, 82])  # Pb_2

    energy_after = copy.get_potential_energy()
    forces_after = copy.get_forces()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    assert np.isclose(diff_energy, 1.86577361, atol=1e-8, rtol=0)
    assert np.allclose(diff_force, [[0, 0, 1.07038059], [0, 0, -1.07038059]], atol=1e-8, rtol=0)


def test_reset_calculator_on_atoms_change():
    """Reset the calculator when changing the system.
    """
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()

    # Copy system
    atoms_copy = copy.copy()
    original_cell = copy.cell.copy()
    atoms_copy.calc = calc

    assert calc.results == {}
    assert calc.nepy is None

    # Scale cell
    atoms_copy.set_cell(1.1*original_cell, scale_atoms=True)
    energy_after = atoms_copy.get_potential_energy()
    forces_after = atoms_copy.get_forces()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    assert np.isclose(diff_energy, 0.28572432, atol=1e-8, rtol=0)
    assert np.allclose(diff_force, [[0, 0, 0.27278336], [0, 0, -0.27278336]], atol=1e-8, rtol=0)


def test_get_potential_and_forces_no_cell():
    """Should raise error if no cell is supplied"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)
    atoms = Atoms('C', positions=[(0, 0, 0)])
    atoms.calc = calc
    with pytest.raises(ValueError)as e:
        atoms.get_potential_energy()
    assert 'Atoms must have a defined cell.' in str(e)


def test_get_potential_and_forces_no_potential():
    """Tries to get potentials and forces without specifying potential"""
    with pytest.raises(FileNotFoundError)as e:
        CPUNEP('nep.txt')
    assert 'nep.txt does not exist.' in str(e)


def test_get_potential_and_forces_no_atoms():
    """Tries to get potential and forces without specifying atoms"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    calc = CPUNEP(nep3)
    with pytest.raises(ValueError)as e:
        calc.calculate()
    assert 'Atoms must be defined to get energies and forces.' in str(e)


def test_CPU_GPU_equivalent():
    """Assert that the CPU and GPU implementation are equivalent
    """
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    # CPU
    PbTe.calc = CPUNEP(nep3)
    cpu_energy = PbTe.get_potential_energy()
    cpu_forces = PbTe.get_forces()
    # GPU
    PbTe.calc = GPUNEP(nep3)
    gpu_energy = PbTe.get_potential_energy()
    gpu_forces = PbTe.get_forces()
    assert np.isclose(cpu_energy, gpu_energy, atol=1e-6)
    assert np.allclose(cpu_forces, gpu_forces, atol=1e-6)
