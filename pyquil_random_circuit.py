#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly
#Some functions taken from https://github.com/rigetti/grove/blob/master/grove/qft/fourier.py

import click
import time
import random
import csv
import os.path
import math

from typing import List

from pyquil import get_qc, Program
from pyquil.gates import SWAP, H, X, Y, Z, T, CNOT, CZ, MEASURE

# Implementation of the Quantum Fourier Transform
def _core_random_circuit(reg: List[int], depth: int) -> Program:
    """
    Generates the core program to perform the random universal circuit benchmark
    
    :param qubits: A list of qubit indexes.
    :param depth: Benchmark circuit depth
    :return: A Quil program to perform the random universal circuit benchmark
    """
    single_bit_gates = H, X, Y, Z, T
    two_bit_gates = SWAP, CNOT, CZ
    circ = []

    for i in range(depth):
        # Single bit gates
        for j in range(len(reg)):
            gate = random.choice(single_bit_gates)
            circ.append(gate(reg[j]))

        # Two bit gates
        bit_set = [reg]  
        while len(bit_set) > 1:
            b1 = random.choice(bit_set)
            bit_set.remove(b1)
            b2 = random.choice(bit_set)
            bit_set.remove(b2)
            gate = random.choice(two_bit_gates)
            circ.append(gate(reg[b1], reg[b2]))

    return circ

def random_circuit(qubits: List[int], depth: int) -> Program:
    """
    Generate a program to perform the random universal circuit benchmark on a set of qubits.
    :param qubits: A list of qubit indexes.
    :param depth: Benchmark circuit depth
    :return: A Quil program to perform the random universal circuit benchmark
    """
    p = Program().inst(_core_random_circuit(qubits, depth))
    return p

def bench(num_qubits, depth):
    circ = random_circuit(range(num_qubits), depth)
    sim_backend = get_qc(str(num_qubits) + 'q-qvm')
    start = time.time()
    sim_backend.run_and_measure(circ, trials=1)
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

    functions = bench,
    writer = create_csv(out)

    for n in range(low, high):
        for d in range(depth):
            # Progress counter
            progress = (((n - low) * depth) + d) / ((high - low) * depth)
            print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

            # Run the benchmarks
            for i in range(samples):
                func = random.choice(functions)
                t = func(n+1, d+1)
                write_csv(writer, {'name': 'pyquil_random', 'num_qubits': n+1, 'depth': d+1, 'time': t})

if __name__ == '__main__':
    benchmark()
