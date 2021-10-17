#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from qiskit import QuantumCircuit
from qiskit import execute, Aer

def sqrtx(circ, t):
    circ.sx(math.pi / 2, t)

def sqrty(circ, t):
    circ.ry(math.pi / 2, t)

def sqrtw(circ, t):
    circ.unitary([[(1-1j)/2, 1/math.sqrt(2)+0j], [1j/math.sqrt(2), (1-1j)/2]], [t])

# Implementation of Sycamore circuit
def sycamore_circuit(num_qubits, depth, circ):
    gateSequence = [ 0, 3, 2, 1, 2, 1, 0, 3 ]
    single_bit_gates = sqrtx, sqrty, sqrtw

    colLen = math.floor(math.sqrt(num_qubits))
    while ((math.floor(num_qubits / colLen) * colLen) != num_qubits):
        colLen = colLen - 1
    rowLen = num_qubits // colLen;

    lastSingleBitGates = []

    for i in range(depth):
        # Single bit gates
        singleBitGates = []
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            if len(lastSingleBitGates) > 0:
                while gate == lastSingleBitGates[j]:
                    gate = random.choice(single_bit_gates)
            gate(circ, j)
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
                circ.cp(math.pi / 6, b1, b2)
                circ.iswap(b1, b2)

    for j in range(num_qubits):
        circ.measure(j, j)

    return circ

sim_backend = Aer.get_backend('qasm_simulator')

def bench(num_qubits, depth):
    circ = QuantumCircuit(num_qubits, num_qubits)
    sycamore_circuit(num_qubits, depth, circ)
    start = time.time()
    job = execute([circ], sim_backend, timeout=600)
    result = job.result()
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
                write_csv(writer, {'name': 'qiskit_sycamore', 'num_qubits': n+1, 'depth': d+1, 'time': t})

if __name__ == '__main__':
    benchmark()
