all: qft random_circuit sycamore

qft:
	g++ -O3 -std=c++11 -Wall -Werror qrack_qft.cpp -lqrack -lOpenCL -o qrack_qft

random_circuit:
	g++ -O3 -std=c++11 -Wall -Werror qrack_random_circuit.cpp -lqrack -lOpenCL -o qrack_random_circuit

sycamore:
	g++ -O3 -std=c++11 -Wall -Werror qrack_sycamore.cpp -lqrack -lOpenCL -o qrack_sycamore
