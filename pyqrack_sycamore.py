#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from pyqrack import QrackSimulator, Pauli

def sqrtx(circ, t):
    circ.u(t, -3 * math.pi / 2, -math.pi / 2, math.pi / 2)

def sqrty(circ, t):
    circ.u(t, -3 * math.pi / 2, 0, 0)

def sqrtw(circ, t):
    circ.mtrx([(1-1j)/2, 1/math.sqrt(2)+0j, 1j/math.sqrt(2), (1-1j)/2], t)

def bench(sim, depth):
    sim.reset_all()
    gateSequence = [ 0, 3, 2, 1, 2, 1, 0, 3 ]
    single_bit_gates = sqrtx, sqrty, sqrtw

    start = time.time()

    num_qubits = sim.num_qubits()

    colLen = math.floor(math.sqrt(num_qubits))
    while (((num_qubits / colLen) * colLen) != num_qubits):
        colLen = colLen - 1
    rowLen = num_qubits // colLen;

    lastSingleBitGates = []

    for i in range(depth):
        # Single bit gates
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            gate(sim, j)

        singleBitGates = []
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            if len(lastSingleBitGates) > 0:
                while gate == lastSingleBitGates[j]:
                    gate = random.choice(single_bit_gates)
            gate(sim, j)
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
                sim.mcmtrx([b1], [1, 0, 0, pow(-1, math.pi / 6)], b2)
                sim.iswap(b1, b2)

    try:
        sim.measure_pauli([Pauli.PauliZ] * num_qubits, range(num_qubits))
        return time.time() - start
    except:
        return 'failure'

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
        for d in range(depth):
            # Progress counter
            progress = (((n - low) * depth) + d) / ((high - low) * depth)
            print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

            # Run the benchmarks
            for i in range(samples):
                t = bench(sim, d+1)
                write_csv(writer, {'name': 'pyqrack_sycamore', 'num_qubits': n+1, 'depth': d+1, 'time': t})

if __name__ == '__main__':
    benchmark()
