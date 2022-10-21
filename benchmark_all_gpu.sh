export PYOPENCL_CTX='1'

# python3 pyqrack/pyqrack_qft.py --out=pyqrack_qft.csv;
# python3 pyqrack/pyqrack_t_nn.py --out=pyqrack_t_nn.csv;
# python3 pyqrack/pyqrack_sycamore.py --out=pyqrack_sycamore.csv;

python3 qiskit_gpu/qiskit_gpu_qft.py --out=qiskit_gpu_qft.csv;
python3 qiskit_gpu/qiskit_gpu_t_nn.py --out=qiskit_gpu_t_nn.csv;
python3 qiskit_gpu/qiskit_gpu_sycamore.py --out=qiskit_gpu_sycamore.csv;

python3 qcgpu/qcgpu_qft.py --out=qcgpu_qft.csv;
python3 qcgpu/qcgpu_t_nn.py --out=qcgpu_t_nn.csv;
python3 qcgpu/qcgpu_sycamore_approximation.py --out=qcgpu_sycamore_approximation.csv
