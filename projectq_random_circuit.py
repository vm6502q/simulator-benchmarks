#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from projectq import MainEngine
import projectq.ops as ops
from projectq.backends import Simulator
from projectq.cengines import LocalOptimizer

# Implementation of random universal circuit
def rand_circuit(num_qubits, depth, q):
    single_bit_gates = ops.H, ops.X, ops.Y, ops.Z, ops.T
    multi_bit_gates = ops.Swap, ops.CNOT, ops.CZ, ops.Toffoli

    for i in range(depth):
        # Single bit gates
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            gate | q[j]

        # Multi bit gates
        bit_set = [range(num_qubits)]
        while len(bit_set) > 1:
            b1 = random.choice(bit_set)
            bit_set.remove(b1)
            b2 = random.choice(bit_set)
            bit_set.remove(b2)
            gate = random.choice(multi_bit_gates)
            while len(bit_set) == 0 and gate == circ.ccx:
                gate = random.choice(multi_bit_gates)
            if gate == circ.ccx:
                b3 = random.choice(bit_set)
                bit_set.remove(b3)
                gate | (q[b1], q[b2], q[b3])
            else:
                gate | (q[b1], q[b2])

    for j in q:
        ops.Measure | j

sim_backend = MainEngine(backend=Simulator(), engine_list=[LocalOptimizer(m=868)])

def bench(num_qubits, depth):
    q = sim_backend.allocate_qureg(num_qubits)
    sim_backend.flush()
    start = time.time()
    rand_circuit(num_qubits, depth, q)
    sim_backend.flush()
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
                write_csv(writer, {'name': 'projectq_random', 'num_qubits': n+1, 'depth': d+1, 'time': t})

if __name__ == '__main__':
    benchmark()
