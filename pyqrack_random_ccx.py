#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from pyqrack import QrackSimulator, Pauli

def toffoli(circ, q1, q2, q3):
    circ.mcx([q1, q2], q3)

# Implementation of random universal circuit
def bench(sim, depth):
    sim.reset_all()

    start = time.time()

    num_qubits = sim.num_qubits()

    rand_perm = math.floor((1 << num_qubits) * random.random())
    if rand_perm == (1 << num_qubits):
        rand_perm = rand_perm - 1

    for qubit in qubits:
        if ((rand_perm >> qubit) & 1) > 0:
            sim.x(qubit)

    for i in range(depth):
        # Multi bit gates
        bit_set = [i for i in range(num_qubits)]
        while len(bit_set) > 2:
            b1 = random.choice(bit_set)
            bit_set.remove(b1)
            b2 = random.choice(bit_set)
            bit_set.remove(b2)
            b3 = random.choice(bit_set)
            bit_set.remove(b2)
            toffoli(sim, b1, b2, b3)

    qubits = [i for i in range(num_qubits)]
    sim.measure_shots(qubits, 1)

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

        for d in [4, 9, 14, 19]:
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
