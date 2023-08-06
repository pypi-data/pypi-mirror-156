#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2022 Hao Zhang<zh970205@mail.ustc.edu.cn>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import inspect
import signal
from copyreg import _slotnames
import numpy as np
import TAT
from .abstract_state import AbstractState
from .common_toolkit import (allreduce_buffer, SignalHandler, seed_differ, mpi_comm, mpi_size, mpi_rank, show, showln,
                             write_to_file, get_imported_function)
from .sampling_tools.tensor_element import tensor_element
from .multiple_product_ansatz import *


class MultipleProductState(AbstractState):
    """
    The multiple product state, which is product of several subansatz.
    """

    __slots__ = ["ansatzes"]

    def __setstate__(self, state):
        # before data_version mechanism, state is (None, state)
        if isinstance(state, tuple):
            state = state[1]
        # before data_version mechanism, there is no data_version field
        if "data_version" not in state:
            state["data_version"] = 0
        # version 0 to version 1
        if state["data_version"] == 0:
            state["data_version"] = 1
        # version 1 to version 2
        if state["data_version"] == 1:
            state["data_version"] = 2
        # setstate
        for key, value in state.items():
            setattr(self, key, value)

    def __getstate__(self):
        # getstate
        state = {key: getattr(self, key) for key in _slotnames(self.__class__)}
        return state

    def __init__(self, abstract):
        """
        Create multiple product state from a given abstract state.

        Parameters
        ----------
        abstract : AbstractState
            The abstract state used to create multiple product state.
        """
        super()._init_by_copy(abstract)
        self.ansatzes = {}

    def add_ansatz(self, ansatz, name=None):
        """
        Add an ansatz.

        Parameters
        ----------
        ansatz : Ansatz
            The ansatz to be made.
        name : str, optional
            The name of the new ansatz.
        """
        if name is None:
            name = str(len(self.ansatzes))
        self.ansatzes[name] = ansatz

    def weight_and_delta(self, configurations, calculate_delta):
        """
        Calculate weight and delta of all ansatz.

        Parameters
        ----------
        configurations : list[list[list[dict[int, EdgePoint]]]]
            The given configurations to calculate weight and delta.
        calculate_delta : set[str]
            The iterator of name of ansatz to calculate delta.

        Returns
        -------
        tuple[list[complex | float], list[dict[str, ansatz]]]
            The weight and the delta ansatz.
        """
        number = len(configurations)
        weight = [1. for _ in range(number)]
        delta = [{} for _ in range(number)]
        for name, ansatz in self.ansatzes.items():
            sub_weight, sub_delta = ansatz.weight_and_delta(configurations, name in calculate_delta)
            for i in range(number):
                weight[i] *= sub_weight[i]
            if sub_delta is not None:
                for i in range(number):
                    delta[i][name] = sub_delta[i] / sub_weight[i]
        for i in range(number):
            this_weight = weight[i]
            this_delta = delta[i]
            for name in this_delta:
                this_delta[name] *= this_weight
        return weight, delta

    def apply_gradient(self, gradient, step_size, relative):
        """
        Apply the gradient to the state.

        Parameters
        ----------
        gradient : dict[str, Delta]
            The gradient calculated by observer object.
        step_size : float
            The gradient step size.
        relative : bool
            Use relative step size or not.
        """
        for name in gradient:
            self.ansatzes[name].apply_gradient(gradient[name], step_size, relative)


class Sampling:
    """
    Metropois sampling object for multiple product state.
    """

    __slots__ = ["_owner", "configuration", "_hopping_hamiltonians", "_restrict_subspace", "ws"]

    def __init__(self, owner, configuration, hopping_hamiltonians, restrict_subspace):
        """
        Create sampling object.

        Parameters
        ----------
        owner : MultipleProductState
            The owner of this sampling object
        configuration : list[list[dict[int, EdgePoint]]]
            The initial configuration.
        hopping_hamiltonian : None | dict[tuple[tuple[int, int, int], ...], Tensor]
            The hamiltonian used in hopping, using the state hamiltonian if this is None.
        restrict_subspace
            A function return bool to restrict sampling subspace.
        """
        self._owner = owner
        self.configuration = [[{orbit: configuration[l1][l2][orbit]
                                for orbit in owner.physics_edges[l1, l2]}
                               for l2 in range(owner.L2)]
                              for l1 in range(owner.L1)]
        [self.ws], _ = self._owner.weight_and_delta([self.configuration], set())
        if hopping_hamiltonians is not None:
            self._hopping_hamiltonians = hopping_hamiltonians
        else:
            self._hopping_hamiltonians = self._owner._hamiltonians
        self._hopping_hamiltonians = list(self._hopping_hamiltonians.items())
        self._restrict_subspace = restrict_subspace

    def __call__(self):
        """
        Get the next configuration.
        """
        owner = self._owner
        hamiltonian_number = len(self._hopping_hamiltonians)
        positions, hamiltonian = self._hopping_hamiltonians[TAT.random.uniform_int(0, hamiltonian_number - 1)()]
        body = hamiltonian.rank // 2
        current_configuration = tuple(self.configuration[l1][l2][orbit] for [l1, l2, orbit] in positions)
        element_pool = tensor_element(hamiltonian)
        if current_configuration not in element_pool:
            return
        possible_hopping = element_pool[current_configuration]
        if len(possible_hopping) == 0:
            return
        hopping_number = len(possible_hopping)
        current_configuration_s, _ = list(possible_hopping.items())[TAT.random.uniform_int(0, hopping_number - 1)()]
        hopping_number_s = len(element_pool[current_configuration_s])
        if self._restrict_subspace is not None:
            replacement = {positions[i]: current_configurations_s[i] for i in range(body)}
            if not self._restrict_subspace(self.configuration, replacement):
                return
        configuration_s = [[{orbit: self.configuration[l1][l2][orbit]
                             for orbit in owner.physics_edges[l1, l2]}
                            for l2 in range(owner.L2)]
                           for l1 in range(owner.L1)]
        for i, [l1, l2, orbit] in enumerate(positions):
            configuration_s[l1][l2][orbit] = current_configuration_s[i]
        [wss], _ = self._owner.weight_and_delta([configuration_s], set())
        p = (np.linalg.norm(wss)**2) / (np.linalg.norm(self.ws)**2) * hopping_number / hopping_number_s
        if TAT.random.uniform_real(0, 1)() < p:
            self.configuration = configuration_s
            self.ws = wss


class Observer:

    __slots__ = [
        "_owner", "_enable_gradient", "_observer", "_restrict_subspace", "_start", "_count", "_result",
        "_result_square", "_total_energy", "_total_energy_square", "_Delta", "_EDelta"
    ]

    def __init__(self, owner):
        """
        Create observer object for the given multiple product state.

        Parameters
        ----------
        owner : MultipleProductState
            The owner of this obsever object.
        """
        self._owner = owner

        self._enable_gradient = set()
        self._observer = {}
        self._restrict_subspace = None

        self._start = False

        self._count = None
        self._result = None
        self._result_square = None
        self._total_energy = None
        self._total_energy_square = None
        self._Delta = None
        self._EDelta = None

    def restrict_subspace(self, restrict_subspace):
        """
        Set restrict subspace for observers.

        Parameters
        ----------
        restrict_subspace
            A function return bool to restrict measure subspace.
        """
        if self._start:
            raise RuntimeError("Cannot set restrict subspace after sampling start")
        self._restrict_subspace = restrict_subspace

    def __enter__(self):
        """
        Enter sampling loop, flush all cached data in the observer object.
        """
        self._start = True
        self._count = 0
        self._result = {
            name: {positions: 0.0 for positions, observer in observers.items()
                  } for name, observers in self._observer.items()
        }
        self._result_square = {
            name: {positions: 0.0 for positions, observer in observers.items()
                  } for name, observers in self._observer.items()
        }
        self._total_energy = 0.0
        self._total_energy_square = 0.0
        self._Delta = {name: None for name in self._enable_gradient}
        self._EDelta = {name: None for name in self._enable_gradient}

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit sampling loop, reduce observed values, used when running with multiple processes.
        """
        if exc_type is not None:
            return False
        buffer = []
        for name, observers in self._observer.items():
            for positions in observers:
                buffer.append(self._result[name][positions])
                buffer.append(self._result_square[name][positions])
        buffer.append(self._total_energy)
        buffer.append(self._total_energy_square)
        buffer.append(self._count)

        buffer = np.array(buffer)
        allreduce_buffer(buffer)
        buffer = buffer.tolist()

        self._count = buffer.pop()
        self._total_energy_square = buffer.pop()
        self._total_energy = buffer.pop()
        for name, observer in reversed(self._observer.items()):
            for positions in reversed(observers):
                self._result_square[name][positions] = buffer.pop()
                self._result[name][positions] = buffer.pop()

        for name in sorted(self._enable_gradient):
            self._owner.ansatzes[name].allreduce_delta(self._Delta[name])
            self._owner.ansatzes[name].allreduce_delta(self._EDelta[name])

    def _expect_and_deviation(self, total, total_square):
        """
        Get the expect value and deviation.

        Parameters
        ----------
        total : float
            The summation of observed value.
        total_square : float
            The summation of observed value square.

        Returns
        -------
        tuple[float, float]
            The expect value and deviation.
        """
        if total == total_square == 0.0:
            return 0.0, 0.0

        N = self._count

        Eb = total / N
        E2b = total_square / N

        EV = E2b - Eb * Eb

        expect = Eb
        variance = EV / N

        if variance < 0.0:
            deviation = 0.0
        else:
            deviation = variance**0.5

        return expect, deviation

    @property
    def result(self):
        """
        Get the observer result.

        Returns
        -------
        dict[str, dict[tuple[tuple[int, int, int], ...], tuple[float, float]]]
            The observer result of each observer set name and each site positions list.
        """
        return {
            name: {
                positions: self._expect_and_deviation(self._result[name][positions],
                                                      self._result_square[name][positions])
                for positions, _ in data.items()
            } for name, data in self._observer.items()
        }

    @property
    def total_energy(self):
        """
        Get the observed energy.

        Returns
        -------
        tuple[float, float]
            The total energy.
        """
        return self._expect_and_deviation(self._total_energy, self._total_energy_square)

    @property
    def energy(self):
        """
        Get the observed energy per site.

        Returns
        -------
        tuple[float, float]
            The energy per site.
        """
        expect, deviation = self.total_energy
        site_number = self._owner.site_number
        return expect / site_number, deviation / site_number

    @property
    def gradient(self):
        """
        Get the energy gradient for every subansatz.

        Returns
        -------
        dict[str, Delta]
            The gradient for every subansatz.
        """
        energy, _ = self.total_energy
        return {
            name: 2 * self._EDelta[name] / self._count - 2 * energy * self._Delta[name] / self._count
            for name in self._enable_gradient
        }

    def enable_gradient(self, ansatz_name=None):
        """
        Enable observing gradient for specified ansatz.

        Parameters
        ----------
        ansatz_name : str | list[str] | None
            The ansatzes of which the gradient should be calculated.
        """
        if self._start:
            raise RuntimeError("Cannot enable gradient after sampling start")
        if "energy" not in self._observer:
            self.add_energy()
        if ansatz_name is None:
            ansatz_name = self._owner.ansatzes.keys()
        if isinstance(ansatz_name, str):
            ansatz_name = [ansatz_name]
        for name in ansatz_name:
            self._enable_gradient.add(name)

    def add_observer(self, name, observer):
        """
        Add an observer set into this observer object, cannot add observer once observer started.

        Parameters
        ----------
        name : str
            This observer set name.
        observers : dict[tuple[tuple[int, int, int], ...], Tensor]
            The observer map.
        """
        if self._start:
            raise RuntimeError("Canot add observer after sampling start")
        self._observer[name] = observer

    def add_energy(self):
        """
        Add energy as an observer.
        """
        self.add_observer("energy", self._owner._hamiltonians)

    def __call__(self, configuration):
        """
        Collect observer value from current configuration.

        Parameters
        ----------
        configuration : list[list[dict[int, EdgePoint]]]
            The current configuration.
        """
        owner = self._owner
        self._count += 1
        [ws], [delta] = owner.weight_and_delta([configuration], self._enable_gradient)
        # find wss
        configuration_list = []
        configuration_map = {}
        for name, observers in self._observer.items():
            configuration_map[name] = {}
            for positions, observer in observers.items():
                configuration_map[name][positions] = {}
                body = observer.rank // 2
                current_configuration = tuple(configuration[l1][l2][orbit] for l1, l2, orbit in positions)
                element_pool = tensor_element(observer)
                if current_configuration not in element_pool:
                    continue
                for other_configuration, observer_shrinked in element_pool[current_configuration].items():
                    if self._restrict_subspace is not None:
                        replacement = {positions[i]: other_configuration[i] for i in range(body)}
                        if not self._restrict_subspace(configuration, replacement):
                            continue
                    new_configuration = [[{
                        orbit: configuration[l1][l2][orbit] for orbit in owner.physics_edges[l1, l2]
                    } for l2 in range(owner.L2)] for l1 in range(owner.L1)]
                    for i, [l1, l2, orbit] in enumerate(positions):
                        new_configuration[l1][l2][orbit] = other_configuration[i]
                    configuration_map[name][positions][other_configuration] = (len(configuration_list),
                                                                               observer_shrinked.storage[0])
                    configuration_list.append(new_configuration)
        wss_list, _ = owner.weight_and_delta(configuration_list, set())
        # measure
        for name, configuration_map_name in configuration_map.items():
            if name == "energy":
                Es = 0.0
            for positions, configuration_map_name_positions in configuration_map_name.items():
                total_value = 0
                for _, [index, hamiltonian_term] in configuration_map_name_positions.items():
                    wss = wss_list[index]
                    value = (wss / ws) * hamiltonian_term
                    total_value += complex(value)
                to_save = total_value.real
                self._result[name][positions] += to_save
                self._result_square[name][positions] += to_save * to_save
                if name == "energy":
                    Es += total_value
            if name == "energy":
                to_save = Es.real
                self._total_energy += to_save
                self._total_energy_square += to_save * to_save
                if self._owner.Tensor.is_real:
                    Es = Es.real
                else:
                    Es = Es.conjugate()
                for ansatz_name in self._enable_gradient:
                    this_delta = delta[ansatz_name] / ws
                    if self._Delta[ansatz_name] is None:
                        self._Delta[ansatz_name] = this_delta
                    else:
                        self._Delta[ansatz_name] += this_delta
                    if self._EDelta[ansatz_name] is None:
                        self._EDelta[ansatz_name] = Es * this_delta
                    else:
                        self._EDelta[ansatz_name] += Es * this_delta


def gradient(
        state: MultipleProductState,
        sampling_total_step,
        grad_total_step,
        grad_step_size,
        *,
        # About sampling
        sampling_configurations=[],
        sweep_hopping_hamiltonians=None,
        restrict_subspace=None,
        # About gradient
        enable_gradient_ansatz=None,
        use_fix_relative_step_size=False,
        # About log and save state
        log_file=None,
        save_state_interval=None,
        save_state_file=None,
        # About Measurement
        measurement=None):

    # Restrict subspace
    if restrict_subspace is not None:
        origin_restrict = get_imported_function(restrict_subspace, "restrict")
        if len(inspect.signature(origin_restrict).parameters) == 1:

            def restrict(configuration, replacement=None):
                if replacement is None:
                    return origin_restrict(configuration)
                else:
                    configuration = configuration.copy()
                    for [l1, l2, orbit], new_site_config in replacement.items():
                        configuration[l1, l2, orbit] = new_site_config
                    return origin_restrict(configuration)
        else:
            restrict = origin_restrict
    else:
        restrict = None

    # Create observer
    observer = Observer(state)
    observer.restrict_subspace(restrict)
    observer.add_energy()
    if grad_step_size != 0:
        if enable_gradient_ansatz is not None:
            observer.enable_gradient(enable_gradient_ansatz.split(","))
        else:
            observer.enable_gradient()
    if measurement:
        measurement_names = measurement.split(",")
        for measurement_name in measurement_names:
            observer.add_observer(measurement_name, get_imported_function(measurement_name, "measurement")(state))

    # Gradient descent
    with SignalHandler(signal.SIGINT) as sigint_handler:
        for grad_step in range(grad_total_step):
            with observer, seed_differ:
                # Create sampling object
                if sweep_hopping_hamiltonians is not None:
                    hopping_hamiltonians = get_imported_function(sweep_hopping_hamiltonians,
                                                                 "hopping_hamiltonians")(state)
                else:
                    hopping_hamiltonians = None
                if len(sampling_configurations) < mpi_size:
                    choose = TAT.random.uniform_int(0, len(sampling_configurations) - 1)()
                else:
                    choose = mpi_rank
                sampling = Sampling(state,
                                    configuration=sampling_configurations[choose],
                                    hopping_hamiltonians=hopping_hamiltonians,
                                    restrict_subspace=restrict)
                # Sampling
                for sampling_step in range(sampling_total_step):
                    if sampling_step % mpi_size == mpi_rank:
                        observer(sampling.configuration)
                        for _ in range(state.site_number):
                            sampling()
                        show(f"sampling {sampling_step}/{sampling_total_step}, energy={observer.energy}")
                # Save configurations
                gathered_configurations = mpi_comm.allgather(sampling.configuration)
                sampling_configurations.clear()
                sampling_configurations += gathered_configurations
            showln(f"gradient {grad_step}/{grad_total_step}, energy={observer.energy}")
            # Measure log
            if measurement and mpi_rank == 0:
                for measurement_name in measurement_names:
                    measurement_result = observer.result[measurement_name]
                    get_imported_function(measurement_name, "save_result")(state, measurement_result, grad_step)
            # Energy log
            if log_file and mpi_rank == 0:
                with open(log_file, "a", encoding="utf-8") as file:
                    print(observer.energy, file=file)
            # Update state
            state.apply_gradient(observer.gradient, grad_step_size, relative=use_fix_relative_step_size)
            # Save state
            if save_state_interval and (grad_step + 1) % save_state_interval == 0 and save_state_file:
                write_to_file(state, save_state_file)

            if sigint_handler():
                break
