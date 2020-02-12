//////////////////////////////////////////////////////////////////////////////////////
//
// (C) Daniel Strano and the Qrack contributors 2017-2019. All rights reserved.
//

#include "qrack_benchmarks.hpp"

int main()
{

    // Random permutation basis eigenstate initialization
    std::cout<<">>>Random Permutation Basis Eigenstate Initialization:"<<std::endl;
    benchmarkLoop(
        [](Qrack::QInterfacePtr qftReg, int n, int unused) {
            qftReg->QFT(0, n, false);
            qftReg->MReg(0, n);
        }, 1, 1, true, false, false, false);

    // Random permutation basis eigenstate, with random Hadamard gates initialization
    std::cout<<">>>Random Permutation Basis w/ Random Hadamard Initialization:"<<std::endl;
    benchmarkLoop(
        [](Qrack::QInterfacePtr qftReg, int n, int unused) {
            qftReg->QFT(0, n, false);
            qftReg->MReg(0, n);
        }, 1, 1, true, true, false, false);

    // Totally random, totally separable qubits, for initialization
    std::cout<<">>>Random Separable Bits:"<<std::endl;
    benchmarkLoop(
        [](Qrack::QInterfacePtr qftReg, int n, int unused) {
            qftReg->QFT(0, n, false);
            qftReg->MReg(0, n);
        }, 1, 1, false, false, false, true);
}
