all: qft random_circuit sycamore universal_nearest_neighbor

qft:
	g++ -O3 -std=c++11 -Wall -Werror qrack_qft.cpp -L/usr/local/bin -lqrack -lOpenCL -lpthread -o qrack_qft

random_circuit:
	g++ -O3 -std=c++11 -Wall -Werror qrack_random_circuit.cpp -L/usr/local/bin -lqrack -lOpenCL -lpthread -o qrack_random_circuit

sycamore:
	g++ -O3 -std=c++11 -Wall -Werror qrack_sycamore.cpp -L/usr/local/bin -lqrack -lOpenCL -lpthread -o qrack_sycamore

universal_nearest_neighbor:
	g++ -O3 -std=c++11 -Wall -Werror qrack_universal_nearest_neighbor.cpp -L/usr/local/bin -lqrack -lOpenCL -lpthread -o qrack_universal_nearest_neighbor
