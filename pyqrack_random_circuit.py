#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from collections import Counter

from qiskit import QuantumCircuit
from qiskit import execute, Aer
from qiskit.providers.aer import QasmSimulator

from pyqrack import QrackSimulator, Pauli

def dicts_almost_equal(dict1, dict2, delta=None, places=None, default_value=0):
    """Test if two dictionaries with numeric values are almost equal.

    Fail if the two dictionaries are unequal as determined by
    comparing that the difference between values with the same key are
    not greater than delta (default 1e-8), or that difference rounded
    to the given number of decimal places is not zero. If a key in one
    dictionary is not in the other the default_value keyword argument
    will be used for the missing value (default 0). If the two objects
    compare equal then they will automatically compare almost equal.

    Args:
        dict1 (dict): a dictionary.
        dict2 (dict): a dictionary.
        delta (number): threshold for comparison (defaults to 1e-8).
        places (int): number of decimal places for comparison.
        default_value (number): default value for missing keys.

    Raises:
        TypeError: if the arguments are not valid (both `delta` and
            `places` are specified).

    Returns:
        String: Empty string if dictionaries are almost equal. A description
            of their difference if they are deemed not almost equal.
    """

    def valid_comparison(value):
        """compare value to delta, within places accuracy"""
        if places is not None:
            return round(value, places) == 0
        else:
            return value < delta

    # Check arguments.
    if dict1 == dict2:
        return ""
    if places is not None:
        if delta is not None:
            raise TypeError("specify delta or places not both")
        msg_suffix = " within %s places" % places
    else:
        delta = delta or 1e-8
        msg_suffix = " within %s delta" % delta

    # Compare all keys in both dicts, populating error_msg.
    error_msg = ""
    for key in set(dict1.keys()) | set(dict2.keys()):
        val1 = dict1.get(key, default_value)
        val2 = dict2.get(key, default_value)
        if not valid_comparison(abs(val1 - val2)):
            error_msg += f"({safe_repr(key)}: {safe_repr(val1)} != {safe_repr(val2)}), "

    if error_msg:
        return error_msg[:-2] + msg_suffix
    else:
        return ""

def cx(circ, q1, q2):
    circ.mcx([q1], q2)

def cz(circ, q1, q2):
    circ.mcz([q1], q2)

def swap(circ, q1, q2):
    circ.swap(q1, q2)

def toffoli(circ, q1, q2, q3):
    circ.mcx([q1, q2], q3)

sim_backend = QasmSimulator(shots=1000, method='automatic')

# Implementation of random universal circuit
def bench(sim, depth):
    num_qubits = sim.num_qubits()
    qis = QuantumCircuit(num_qubits, num_qubits)
    sim.reset_all()
    single_bit_gates = sim.h, sim.x, sim.y, sim.z, sim.t
    multi_bit_gates = swap, cx, cz, toffoli
    qis_single_bit_gates = qis.h, qis.x, qis.y, qis.z, qis.t
    qis_multi_bit_gates = qis.swap, qis.cx, qis.cz, qis.ccx

    start = time.time()

    for i in range(depth):
        # Single bit gates
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            qisgate = qis_single_bit_gates[single_bit_gates.index(gate)]
            gate(j)
            qisgate(j)

        # Multi bit gates
        bit_set = [range(num_qubits)]    
        while len(bit_set) > 1:
            b1 = random.choice(bit_set)
            bit_set.remove(b1)
            b2 = random.choice(bit_set)
            bit_set.remove(b2)
            gate = random.choice(multi_bit_gates)
            while len(bit_set) == 0 and gate == toffoli:
                gate = random.choice(multi_bit_gates)
            qisgate = qis_multi_bit_gates[qis_multi_bit_gates.index(gate)]
            if gate == toffoli:
                b3 = random.choice(bit_set)
                bit_set.remove(b3)
                gate(sim, b1, b2, b3)
                qisgate(b1, b2, b3)
            else:
                gate(sim, b1, b2)
                qisgate(b1, b2)

    for j in range(num_qubits):
        qis.measure(j, j)

    qubits = [i for i in range(num_qubits)]
    measure_results = sim.measure_shots(qubits, 1000)
    qrack_result_list = []
    for sample in measure_results:
        qrack_result_list.append(hex(int(bin(sample)[2:], 2)))
    qrack_result = dict(Counter(qrack_result_list))

    job = execute(qis, sim_backend, timeout=600, shots=1000)
    qiskit_result = job.result().results[0].to_dict()['data']['counts']

    if "" != dicts_almost_equal(qrack_result, qiskit_result, delta=100):
        raise Exception("Not within tolerance")

    return time.time() - start

# Reporting
def create_csv(filename):
    file_exists = os.path.isfile(filename)
    csvfile = open(filename, 'a')

    headers = ['name', 'num_qubits', 'depth', 'time']
    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

    if not file_exists:
        writer.writeheader()  # file doesn't exist yet, write a header

    return writer

def write_csv(writer, data):
    writer.writerow(data)



@click.command()
@click.option('--samples', default=100, help='Number of samples to take for each qubit.')
@click.option('--qubits', default=28, help='How many qubits you want to test for')
@click.option('--depth', default=20, help='How large a circuit depth you want to test for')
@click.option('--out', default='benchmark_data.csv', help='Where to store the CSV output of each test')
@click.option('--single', default=False, help='Only run the benchmark for a single amount of qubits, and print an analysis')
def benchmark(samples, qubits, depth, out, single):
    if single:
        low = qubits - 1
    else:
        low = 3
    high = qubits

    writer = create_csv(out)

    for n in range(low, high):
        sim = QrackSimulator(n + 1)

        for d in range(depth):
            # Progress counter
            progress = (((n - low) * depth) + d) / ((high - low) * depth)
            print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

            # Run the benchmarks
            for i in range(samples):
                t = bench(sim, d+1)
                write_csv(writer, {'name': 'pyqrack_random', 'num_qubits': n+1, 'depth': d+1, 'time': t})

        # Call old simulator width destructor BEFORE initializing new width
        del sim

if __name__ == '__main__':
    benchmark()
