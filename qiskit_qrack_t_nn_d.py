#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from qiskit import QuantumCircuit
from qiskit import execute
from qiskit.providers.qrack import QasmSimulator
from qiskit.compiler.transpiler import transpile

def x_to_y(circ, q):
    circ.s(q)

def x_to_z(circ, q):
    circ.h(q)

def y_to_z(circ, q):
    circ.sdg(q)
    circ.h(q)

def y_to_x(circ, q):
    circ.sdg(q)

def z_to_x(circ, q):
    circ.h(q)

def z_to_y(circ, q):
    circ.h(q)
    circ.s(q)

def cx(circ, q1, q2):
    circ.cx(q1, q2)

def cy(circ, q1, q2):
    circ.cy(q1, q2)

def cz(circ, q1, q2):
    circ.cz(q1, q2)

def acx(circ, q1, q2):
    circ.x(q1)
    circ.cx(q1, q2)

def acy(circ, q1, q2):
    circ.x(q1)
    circ.cy(q1, q2)

def acz(circ, q1, q2):
    circ.x(q1)
    circ.cz(q1, q2)

def swap(circ, q1, q2):
    circ.swap(q1, q2)

def ident(circ, q1, q2):
    pass

# Implementation of random universal circuit
def random_circuit(num_qubits, depth, circ):
    single_bit_gates = x_to_y, x_to_z, y_to_z, y_to_x, z_to_x, z_to_y
    two_bit_gates = ident, swap, cx, cz, cy, acx, acz, acy
    gateSequence = [ 0, 3, 2, 1, 2, 1, 0, 3 ]
    colLen = math.floor(math.sqrt(num_qubits))
    while ((math.floor(num_qubits / colLen) * colLen) != num_qubits):
        colLen = colLen - 1
    rowLen = num_qubits // colLen;

    start = time.time()

    for i in range(depth):
        # Single bit gates
        for j in range(num_qubits):
            # Random basis switch
            gate = random.choice(single_bit_gates)
            gate(circ, j)

            # Random 1/4 increment phase change, x0 to x3
            if random.getrandbits(1) > 0:
                circ.z(j)
            if random.getrandbits(1) > 0:
                if random.getrandbits(1) > 0:
                    circ.s(j)
                else:
                    circ.sdg(j)

            # T gate probability is scaled so (num_qubits + 2) average T gates in total, for any width and depth choice
            if random.uniform(0, (num_qubits + 2) * depth) < 1:
                if random.getrandbits(1) > 0:
                    circ.t(j)
                else:
                    circ.tdg(j)

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
                g = random.choice(two_bit_gates)
                g(circ, b1, b2)

    for j in range(num_qubits):
        circ.measure(j, j)

    return circ

def bench(sim_backend, num_qubits, depth):
    circ = QuantumCircuit(num_qubits, num_qubits)
    circ = random_circuit(num_qubits, depth, circ)
    start = time.time()
    circ = transpile(circ, optimization_level=3)
    job = execute([circ], sim_backend, timeout=600, shots=1)
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


# Run with export QRACK_QUNIT_SEPARABILITY_THRESHOLD=0.1464466 for example
@click.command()
@click.option('--samples', default=100, help='Number of samples to take for each qubit.')
@click.option('--qubits', default=36, help='How many qubits you want to test for')
@click.option('--depth', default=36, help='How large a circuit depth you want to test for')
@click.option('--out', default='benchmark_data.csv', help='Where to store the CSV output of each test')
@click.option('--single', default=True, help='Only run the benchmark for a single amount of qubits, and print an analysis')
def benchmark(samples, qubits, depth, out, single):
    if single:
        low = qubits - 1
    else:
        low = 3
    high = qubits

    writer = create_csv(out)
    
    sim = QasmSimulator(shots=1)

    for n in range(low, high):
        for d in range(depth):
            # Progress counter
            progress = (((n - low) * depth) + d) / ((high - low) * depth)
            print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

            # Run the benchmarks
            for i in range(samples):
                try:
                    t = bench(sim, n+1, d+1)
                    write_csv(writer, {'name': 'qiskiit_qrack_t_nn_d', 'num_qubits': n+1, 'depth': d+1, 'time': t})
                except:
                    del sim
                    write_csv(writer, {'name': 'qiskiit_qrack_t_nn_d', 'num_qubits': n+1, 'depth': d+1, 'time': -999})
                    sim = QasmSimulator(shots=1)

if __name__ == '__main__':
    benchmark()
