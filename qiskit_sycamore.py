#Adapted from https://github.com/libtangle/qcgpu/blob/master/benchmark/benchmark.py by Adam Kelly

import click
import time
import random
import csv
import os.path
import math

from qiskit import QuantumCircuit
from qiskit import execute, BasicAer

# Decomposition of ISWAP
def iswap(circ, c, t):
    circ.x(c);
    circ.s(c);
    circ.s(t);
    circ.h(t);
    circ.cx(c, t);
    circ.h(c);
    circ.h(t);
    circ.cx(c, t);
    circ.h(c);

def sqrtx(circ, t):
    circ.rx(math.pi / 2, t)

def sqrty(circ, t):
    circ.ry(math.pi / 2, t)

def sqrth(circ, t):
    # To 18 digits of precision for the angle parameters:
    circ.u3(1.04719755119659775, 0.955316618124509278, 2.18627603546528396, t)

# Implementation of Sycamore circuit
def rand_circuit(num_qubits, depth, circ):
    gateSequence = [ 0, 3, 1, 2, 1, 2, 0, 3 ]
    sequenceRowStart = [ 1, 1, 0, 0 ]
    single_bit_gates = sqrtx, sqrty, sqrth

    rowLen = math.floor(math.sqrt(num_qubits))
    while (((num_qubits / rowLen) * rowLen) != num_qubits):
        rowLen = rowLen - 1;
    colLen = num_qubits / rowLen;

    for i in range(depth):
        # Single bit gates
        for j in range(num_qubits):
            gate = random.choice(single_bit_gates)
            gate(circ, j)

        gate = gateSequence[0]
        gateSequence.pop(0)
        gateSequence.append(gate)

        startsEvenRow = (sequenceRowStart[gate] == 0)

        for row in range(sequenceRowStart[gate], math.floor(num_qubits / rowLen), 2):
            for col in range(0, math.floor(num_qubits / colLen)):
                tempRow = row
                tempCol = col

                tempRow = tempRow + (1 if (gate & 2) else -1)

                if startsEvenRow:
                    tempCol = tempCol + (0 if (gate & 1) else -1)
                else:
                    tempCol = tempCol + (1 if (gate & 1) else 0)

                if (tempRow < 0) or (tempCol < 0) or (tempRow >= rowLen) or (tempCol >= colLen):
                    continue

                b1 = row * rowLen + col;
                b2 = tempRow * rowLen + tempCol;

                # Two bit gates
                circ.cu1(math.pi / 6, b1, b2)
                iswap(circ, b1, b2)

    for j in range(num_qubits):
        circ.measure(j, j)

    return circ

sim_backend = BasicAer.get_backend('qasm_simulator')

def bench_qiskit(num_qubits, depth):
    circ = QuantumCircuit(num_qubits, num_qubits)
    circ.barrier()
    rand_circuit(num_qubits, depth, circ)
    circ.barrier()
    start = time.time()
    execute([circ], sim_backend)
    circ.barrier()
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
        low = qubits
    else:
        low = 3
    high = qubits

    functions = bench_qiskit,
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
                write_csv(writer, {'name': func.__name__, 'num_qubits': n+1, 'depth': d+1, 'time': t})

if __name__ == '__main__':
    benchmark()
