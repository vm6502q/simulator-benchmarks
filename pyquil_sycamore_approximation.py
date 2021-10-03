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
from pyquil.gates import SWAP, RX, RY, H, CPHASE

def sqrtx(t):
    return RX(math.pi / 2, t)

def sqrty(t):
    return RY(math.pi / 2, t)

# pyquil/QVM has a universal gate set. It is therefore possible to decompose "sqrth" into other gates in the API.
# However, this is not necessarily practical or representative. For an "apples-to-apples" comparison with
# the other simulators, making reasonable allowance for easily-implemented extensions to the simulator API,
# replacing "sqrth" with "H" is probably a fairer test.

# Implementation of Sycamore circuit
def _core_sycamore_circuit(reg: List[int], depth: int) -> Program:
    """
    Generates the core program to perform an approximation of the Sycamore chip benchmark
    
    :param qubits: A list of qubit indexes.
    :param depth: Benchmark circuit depth
    :return: A Quil program to perform an approximation of the Sycamore chip benchmark
    """

    num_qubits = len(reg)
    gateSequence = [ 0, 3, 2, 1, 2, 1, 0, 3 ]
    single_bit_gates = sqrtx, sqrty, H # H should actually be sqrth
    circ = []

    lastSingleBitGates = []

    colLen = math.floor(math.sqrt(num_qubits))
    while ((math.floor(num_qubits / colLen) * colLen) != num_qubits):
        colLen = colLen - 1
    rowLen = num_qubits // colLen;

    for i in range(depth):
        # Single bit gates
        singleBitGates = []
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            if len(lastSingleBitGates) > 0:
                while gate == lastSingleBitGates[j]:
                    gate = random.choice(single_bit_gates)
            circ.append(gate(reg[j]))
            singleBitGates.append(gate)

        lastSingleBitGates = singleBitGates

        gate = gateSequence[0]
        gateSequence.pop(0)
        gateSequence.append(gate)

        for row in range(1, rowLen, 2):
            for col in range(0, colLen):
                tempRow = row;
                tempCol = col;

                tempRow = tempRow + (1 if (gate & 2) else -1)
                if colLen != 1:
                    tempCol = tempCol + (1 if (gate & 1) else 0)

                if (tempRow < 0) or (tempCol < 0) or (tempRow >= rowLen) or (tempCol >= colLen):
                    continue;

                b1 = row * colLen + col;
                b2 = tempRow * colLen + tempCol;

                # Two bit gates
                circ.append(CPHASE(math.pi / 6, reg[b1], reg[b2]))
                circ.append(SWAP(reg[b1], reg[b2]))

    return circ

def sycamore_circuit(qubits: List[int], depth: int) -> Program:
    """
    Generate a program to perform an approximation of the Sycamore chip benchmark.
    :param qubits: A list of qubit indexes.
    :param depth: Benchmark circuit depth
    :return: A Quil program to perform an approximation of the Sycamore chip benchmark
    """
    p = Program().inst(_core_sycamore_circuit(qubits, depth))
    return p

def bench(num_qubits, depth):
    circ = sycamore_circuit(range(num_qubits), depth)
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
        for d in [4, 9, 14, 19]:
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
