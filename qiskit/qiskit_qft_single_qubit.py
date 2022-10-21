#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from qiskit import QuantumCircuit
from qiskit import execute, Aer
from qiskit.providers.aer import QasmSimulator
from qiskit.circuit.library.standard_gates.p import PhaseGate

# Implementation of the Quantum Fourier Transform
def qft(num_qubits, circ):
    # Quantum Fourier Transform
    start = time.time()
    for i in range(num_qubits):
        circ.u(random.uniform(0, 4 * math.pi), random.uniform(0, 4 * math.pi), random.uniform(0, 4 * math.pi), 0)

        # We use the single control qubit "trick" referenced in Beauregard:
        for j in range(i):
            circ.append(PhaseGate(1.0 / (1<<(1 + i - j))), [0]).c_if(j,1)
        circ.h(0)
        circ.measure(0, i)

        circ.reset(0)

    return time.time() - start

sim_backend = Aer.get_backend('qasm_simulator')

def bench(num_qubits):
    circ = QuantumCircuit(1, num_qubits)
    qft(num_qubits, circ)
    start = time.time()
    job = execute([circ], sim_backend, timeout=600, shots=1)
    result = job.result()
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
            write_csv(writer, {'name': 'qiskit_qft', 'num_qubits': n+1, 'time': t})

if __name__ == '__main__':
    benchmark()
