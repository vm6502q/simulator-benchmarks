export PYOPENCL_CTX='0'

python3 pyqrack_qft.py --out=pyqrack_qft.csv;
python3 pyqrack_random_circuit.py --out=pyqrack_random_circuit.csv;
python3 pyqrack_sycamore.py --out=pyqrack_sycamore.csv;

python3 qiskit_gpu_qft.py --out=qiskit_gpu_qft.csv;
python3 qiskit_gpu_random_circuit.py --out=qiskit_gpu_random_circuit.csv;
python3 qiskit_gpu_sycamore_approximation.py --out=qiskit_gpu_sycamore_approximation.csv;

python3 qcgpu_qft.py --out=qcgpu_qft.csv;
python3 qcgpu_random_circuit.py --out=qcgpu_random_circuit.csv;
python3 qcgpu_sycamore_approximation.py --out=qcgpu_sycamore_approximation.csv
