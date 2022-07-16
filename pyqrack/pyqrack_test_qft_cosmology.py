#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from pyqrack import QrackSimulator, Pauli

# Optimized, based on 'test_qft_cosmology` in the C++ Qrack library benchmark suite.

def phase_root_n(sim, n, q):
    sim.mtrx([1, 0, 0, -1**(1.0 / (1<<(n - 1)))], q)

def bench(sim, num_qubits):
    sim.reset_all()
    m_results = []
    start = time.time()
    for _ in range(num_qubits):
        sim.u(0, random.uniform(0, 4 * math.pi), random.uniform(0, 4 * math.pi), random.uniform(0, 4 * math.pi))

        # We use the single control qubit "trick" referenced in Beauregard:
        m_count = len(m_results)
        for j in range(m_count):
            if m_results[j]:
                phase_root_n(sim, (m_count - j) + 1, 0)
        sim.h(0)
        m_results.append(sim.m(0))

        if m_results[-1]:
            sim.x(0)

    return time.time() - start, m_results

# Reporting
def create_csv(filename):
    file_exists = os.path.isfile(filename)
    csvfile = open(filename, 'a')
   
    headers = ['name', 'num_qubits', 'time', 'measurement']
    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

    if not file_exists:
        writer.writeheader()  # file doesn't exist yet, write a header

    return writer

def write_csv(writer, data):
    writer.writerow(data)



@click.command()
@click.option('--samples', default=100, help='Number of samples to take for each qubit.')
@click.option('--qubits', default=128, help='How many qubits you want to test for')
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
        sim = QrackSimulator(1)

        # Progress counter
        progress = (n - low) / (high - low)
        print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

        # Run the benchmarks
        for i in range(samples):
            try:
                t, m = bench(sim, n)
                mi = 0
                for i in range(len(m)):
                    if m[i]:
                        mi |= 1 << i
                write_csv(writer, {'name': 'pyqrack_test_qft_cosmology', 'num_qubits': n+1, 'time': t, 'measurement': mi})
            except:
                del sim
                write_csv(writer, {'name': 'pyqrack_test_qft_cosmology', 'num_qubits': n+1, 'time': -999, 'measurement': -999})
                sim = QrackSimulator(1)

        # Call old simulator width destructor BEFORE initializing new width
        del sim

if __name__ == '__main__':
    benchmark()
