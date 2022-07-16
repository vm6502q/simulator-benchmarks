#Reduced directly from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly (with thanks)

import click
import time
import random
import statistics
import csv
import os.path
import math
import numpy as np

import qcgpu

def phase_root_n(sim, n, q):
    phase_root_n_matrix = np.array([
        [1, 0],
        [0, np.exp(1j * np.pi / 4)]
    ])
    phase_root_n_gate = qcgpu.Gate(phase_root_n_matrix)
    sim.apply_gate(phase_root_n_gate, q)

def u(sim, th, ph, lm, q):
    cos0 = math.cos(th / 2);
    sin0 = math.sin(th / 2);
    u_matrix = np.array([
        [cos0, sin0 * (-math.cos(lm) - math.sin(lm) * 1j)],
        [sin0 * (math.cos(ph) + math.sin(ph) * 1j), cos0 * (math.cos(ph + lm) + math.sin(ph + lm) * 1j)]
    ])
    u_gate = qcgpu.Gate(u_matrix)
    sim.apply_gate(u_gate, q)

def bench(num_qubits):
    state = qcgpu.State(1)
    m_results = []
    start = time.time()    
    for _ in range(num_qubits):
        u(state, random.uniform(0, 4 * math.pi), random.uniform(0, 4 * math.pi), random.uniform(0, 4 * math.pi), 0)

        # We use the single control qubit "trick" referenced in Beauregard:
        m_count = len(m_results)
        for j in range(m_count):
            if m_results[j]:
                phase_root_n(state, (m_count - j) + 1, 0)
        state.h(0)
        m_results.append(state.measure())

        if m_results[-1]:
            state.x(0)

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
            write_csv(writer, {'name': 'qcgpu_qft', 'num_qubits': n+1, 'time': t})

if __name__ == '__main__':
    benchmark()
