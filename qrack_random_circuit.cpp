//////////////////////////////////////////////////////////////////////////////////////
//
// (C) Daniel Strano and the Qrack contributors 2017-2019. All rights reserved.
//

#include "qrack_benchmarks.hpp"

using namespace Qrack;

bitLenInt pickRandomBit(QInterfacePtr qReg, std::set<bitLenInt>* unusedBitsPtr)
{
    std::set<bitLenInt>::iterator bitIterator = unusedBitsPtr->begin();
    bitLenInt bitRand = unusedBitsPtr->size() * qReg->Rand();
    if (bitRand >= unusedBitsPtr->size()) {
        bitRand = unusedBitsPtr->size() - 1U;
    }
    std::advance(bitIterator, bitRand);
    bitRand = *bitIterator;
    unusedBitsPtr->erase(bitIterator);
    return bitRand;
}

int main()
{
    const int GateCount1Qb = 4;
    const int GateCountMultiQb = 4;

    benchmarkLoop(
        [&](QInterfacePtr qReg, int n, int Depth) {

            int d;
            bitLenInt i;
            real1 gateRand;
            bitLenInt b1, b2, b3;
            int maxGates;

            for (d = 0; d < Depth; d++) {

                for (i = 0; i < n; i++) {
                    gateRand = qReg->Rand();
                    if (gateRand < (ONE_R1 / GateCount1Qb)) {
                        qReg->H(i);
                    } else if (gateRand < (2 * ONE_R1 / GateCount1Qb)) {
                        qReg->X(i);
                    } else if (gateRand < (3 * ONE_R1 / GateCount1Qb)) {
                        qReg->Y(i);
                    } else {
                        qReg->T(i);
                    }
                }

                std::set<bitLenInt> unusedBits;
                for (i = 0; i < n; i++) {
                    // In the past, "qReg->TrySeparate(i)" was also used, here, to attempt optimization. Be aware that
                    // the method can give performance advantages, under opportune conditions, but it does not, here.
                    unusedBits.insert(unusedBits.end(), i);
                }

                while (unusedBits.size() > 1) {
                    b1 = pickRandomBit(qReg, &unusedBits);
                    b2 = pickRandomBit(qReg, &unusedBits);

                    if (unusedBits.size() > 0) {
                        maxGates = GateCountMultiQb;
                    } else {
                        maxGates = GateCountMultiQb - 1U;
                    }

                    gateRand = maxGates * qReg->Rand();

                    if (gateRand < ONE_R1) {
                        qReg->Swap(b1, b2);
                    } else if (gateRand < (2 * ONE_R1)) {
                        qReg->CZ(b1, b2);
                    } else if ((unusedBits.size() == 0) || (gateRand < (3 * ONE_R1))) {
                        qReg->CNOT(b1, b2);
                    } else {
                        b3 = pickRandomBit(qReg, &unusedBits);
                        qReg->CCNOT(b1, b2, b3);
                    }
                }
            }

            qReg->MAll();
        },
        1, 20, false, false, false);
}
