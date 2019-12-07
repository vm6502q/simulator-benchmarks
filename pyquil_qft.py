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
from pyquil.gates import SWAP, H, CPHASE, MEASURE

# Implementation of the Quantum Fourier Transform
def _core_qft(qubits: List[int], coeff: int) -> Program:
    """
    Generates the core program to perform the quantum Fourier transform
    
    :param qubits: A list of qubit indexes.
    :param coeff: A modifier for the angle used in rotations (-1 for inverse QFT, 1 for QFT)
    :return: A Quil program to compute the core (inverse) QFT of the qubits.
    """
    
    q = qubits[0]
    qs = qubits[1:]
    if 1 == len(qubits):
        return [H(q)]
    else:
        n = 1 + len(qs)
        cR = []
        for idx, i in enumerate(range(n - 1, 0, -1)):
            q_idx = qs[idx]
            angle = math.pi / 2 ** (n - i)
            cR.append(CPHASE(coeff * angle, q, q_idx))
        return _core_qft(qs, coeff) + list(reversed(cR)) + [H(q)]

def qft(qubits: List[int]) -> Program:
    """
    Generate a program to compute the quantum Fourier transform on a set of qubits.
    :param qubits: A list of qubit indexes.
    :return: A Quil program to compute the Fourier transform of the qubits.
    """
    p = Program().inst(_core_qft(qubits, 1))
    return p

def bench(num_qubits):
    circ = qft(range(num_qubits))
    sim_backend = get_qc(str(num_qubits) + 'q-qvm')
    start = time.time()
    sim_backend.run_and_measure(circ, trials=1)
    return time.time() - start

# Reporting
def create_csv(filename):
    file_exists = os.path.isfile(filename)
    csvfile = open(filename, 'a')
   
    headers = ['name', 'num_qubits', 'time']
    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

    if not file_exists:
        writer.writeheader()  # file doesn't exist yet, write a header

    return writer

def write_csv(writer, data):
    writer.writerow(data)



@click.command()
@click.option('--samples', default=100, help='Number of samples to take for each qubit.')
@click.option('--qubits', default=28, help='How many qubits you want to test for')
@click.option('--out', default='benchmark_data.csv', help='Where to store the CSV output of each test')
@click.option('--single', default=False, help='Only run the benchmark for a single amount of qubits, and print an analysis')
def benchmark(samples, qubits, out, single):
    if single:
        low = qubits - 1
    else:
        low = 3
    high = qubits

    functions = bench,
    writer = create_csv(out)

    for n in range(low, high):
        # Progress counter
        progress = (n - low) / (high - low)
        print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

        # Run the benchmarks
        for i in range(samples):
            func = random.choice(functions)
            t = func(n + 1)
            write_csv(writer, {'name': func.__name__, 'num_qubits': n+1, 'time': t})

if __name__ == '__main__':
    benchmark()
