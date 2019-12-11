//////////////////////////////////////////////////////////////////////////////////////
//
// (C) Daniel Strano and the Qrack contributors 2017-2019. All rights reserved.
//

#include "qrack_benchmarks.hpp"

int main()
{

#if 0
    // Random permutation initialization: trivial problem for QUnit, but not generally representative
    benchmarkLoop(
        [](QInterfacePtr qftReg, int n) {
            qftReg->QFT(0, n, false);
    }, true, false, testEngineType == QINTERFACE_QUNIT);
#endif

    // Totally random, totally separable qubits, for initialization
    benchmarkLoop(
        [](Qrack::QInterfacePtr qftReg, int n, int unused) {
            qftReg->QFT(0, n, false);
            qftReg->MReg(0, n);
        }, 1, 1, false, false, false, true);
}
