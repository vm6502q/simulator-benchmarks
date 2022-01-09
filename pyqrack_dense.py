#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from pyqrack import QrackSimulator, Pauli

def x_to_y(circ, q):
    circ.s(q)

def x_to_z(circ, q):
    circ.h(q)

def y_to_z(circ, q):
    circ.adjs(q)
    circ.h(q)

def y_to_x(circ, q):
    circ.adjs(q)

def z_to_x(circ, q):
    circ.h(q)

def z_to_y(circ, q):
    circ.h(q)
    circ.s(q)

def cx(circ, q1, q2):
    circ.mcx([q1], q2)

def cy(circ, q1, q2):
    circ.mcy([q1], q2)

def cz(circ, q1, q2):
    circ.mcz([q1], q2)

def acx(circ, q1, q2):
    circ.macx([q1], q2)

def acy(circ, q1, q2):
    circ.macy([q1], q2)

def acz(circ, q1, q2):
    circ.macz([q1], q2)

def swap(circ, q1, q2):
    circ.swap(q1, q2)

def ccx(circ, q1, q2, q3):
    circ.mcx([q1, q2], q2)

def ccy(circ, q1, q2, q3):
    circ.mcy([q1, q2], q3)

def ccz(circ, q1, q2, q3):
    circ.mcz([q1, q2], q3)

def accx(circ, q1, q2, q3):
    circ.macx([q1, q2], q3)

def accy(circ, q1, q2, q3):
    circ.macy([q1, q2], q3)

def accz(circ, q1, q2, q3):
    circ.macz([q1, q2], q3)

# Implementation of random universal circuit
def bench(sim, depth):
    sim.reset_all()
    single_bit_gates = x_to_y, x_to_z, y_to_z, y_to_x, z_to_x, z_to_y
    two_bit_gates = swap, cx, cz, cy, acx, acz, acy
    three_bit_gates = ccx, ccy, ccz, accx, accy, accz

    start = time.time()

    num_qubits = sim.num_qubits()

    for i in range(depth):
        # Single bit gates
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            gate(sim, j)
            sim.r(Pauli.PauliZ, random.uniform(0, 2 * math.pi), j)

        # Multi bit gates
        bit_set = [i for i in range(num_qubits)]
        while len(bit_set) > 1:
            b1 = random.choice(bit_set)
            bit_set.remove(b1)
            b2 = random.choice(bit_set)
            bit_set.remove(b2)
            gate = random.choice(two_bit_gates + three_bit_gates)
            if len(bit_set) == 0 and (gate in three_bit_gates):
                gate = random.choice(two_bit_gates)
            if gate in three_bit_gates:
                b3 = random.choice(bit_set)
                bit_set.remove(b3)
                gate(sim, b1, b2, b3)
            else:
                gate(sim, b1, b2)

    qubits = [i for i in range(num_qubits)]
    sim.m_all()

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
@click.option('--depth', default=6, help='How large a circuit depth you want to test for')
@click.option('--out', default='benchmark_data.csv', help='Where to store the CSV output of each test')
@click.option('--single', default=True, help='Only run the benchmark for a single amount of qubits, and print an analysis')
def benchmark(samples, qubits, depth, out, single):
    if single:
        low = qubits - 1
    else:
        low = 3
    high = qubits

    writer = create_csv(out)

    for n in range(low, high):
        sim = QrackSimulator(n + 1)

        for d in range(depth):
            # Progress counter
            progress = (((n - low) * depth) + d) / ((high - low) * depth)
            print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

            # Run the benchmarks
            for i in range(samples):
                try:
                    t = bench(sim, d + 1)
                    write_csv(writer, {'name': 'pyqrack_random_extended', 'num_qubits': n+1, 'depth': d+1, 'time': t})
                except:
                    del sim
                    write_csv(writer, {'name': 'pyqrack_random_extended', 'num_qubits': n+1, 'depth': d+1, 'time': -999})
                    sim = QrackSimulator(n + 1)

        # Call old simulator width destructor BEFORE initializing new width
        del sim

if __name__ == '__main__':
    benchmark()