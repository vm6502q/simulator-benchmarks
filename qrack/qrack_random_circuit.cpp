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
    const int DimCount1Qb = 4;
    const int DimCountMultiQb = 4;

    benchmarkLoop(
        [&](QInterfacePtr qReg, int n, int Depth) {
            int d;
            bitLenInt i;
            real1_f gateRand;
            bitLenInt b1, b2, b3;

            qReg->SetReactiveSeparate(true);

            for (d = 0; d < Depth; d++) {
                for (i = 0; i < n; i++) {
                    // "Phase" transforms:
                    gateRand = DimCount1Qb * qReg->Rand();
                    if (gateRand < ONE_R1) {
                        qReg->H(i);
                    } else if (gateRand < (2 * ONE_R1)) {
                        gateRand = 2 * qReg->Rand();
                        if (gateRand < ONE_R1) {
                            qReg->S(i);
                        } else {
                            qReg->IS(i);
                        }
                    } else if (gateRand < (3 * ONE_R1)) {
                        gateRand = 2 * qReg->Rand();
                        if (gateRand < ONE_R1) {
                            qReg->H(i);
                            qReg->S(i);
                        } else {
                            qReg->IS(i);
                            qReg->H(i);
                        }
                    }
                    // else - identity

                    // "Position transforms:

                    // Continuous Z root gates option:
                    gateRand = 2 * PI_R1 * qReg->Rand();
                    qReg->Phase(ONE_R1, std::polar(ONE_R1, (real1)gateRand), i);

                    /*
                    // Discrete Z root gates option:
                    gateRand = 8 * qReg->Rand();
                    if (gateRand < ONE_R1) {
                        // Z^(1/4)
                        qReg->T(i);
                    } else if (gateRand < (2 * ONE_R1)) {
                        // Z^(1/2)
                        qReg->S(i);
                    } else if (gateRand < (3 * ONE_R1)) {
                        // Z^(3/4)
                        qReg->Z(i);
                        qReg->IT(i);
                    } else if (gateRand < (4 * ONE_R1)) {
                        // Z
                        qReg->Z(i);
                    } else if (gateRand < (5 * ONE_R1)) {
                        // Z^(-3/4)
                        qReg->Z(i);
                        qReg->T(i);
                    } else if (gateRand < (6 * ONE_R1)) {
                        // Z^(-1/2)
                        qReg->IS(i);
                    } else if (gateRand < (7 * ONE_R1)) {
                        // Z^(-1/4)
                        qReg->IT(i);
                    }
                    // else - identity
                    */
                }

                std::set<bitLenInt> unusedBits;
                for (i = 0; i < n; i++) {
                    unusedBits.insert(unusedBits.end(), i);
                }

                while (unusedBits.size() > 1) {
                    b1 = pickRandomBit(qReg, &unusedBits);
                    b2 = pickRandomBit(qReg, &unusedBits);

                    gateRand = 2 * qReg->Rand();

                    // TODO: Target "anti-" variants for optimization

                    if ((gateRand < ONE_R1) || !unusedBits.size()) {

                        gateRand = DimCountMultiQb * qReg->Rand();

                        if (gateRand < ONE_R1) {
                            gateRand = 4 * qReg->Rand();
                            if (gateRand < (3 * ONE_R1)) {
                                gateRand = 2 * qReg->Rand();
                                if (gateRand < ONE_R1) {
                                    qReg->CNOT(b1, b2);
                                } else {
                                    qReg->AntiCNOT(b1, b2);
                                }
                            } else {
                                qReg->Swap(b1, b2);
                            }
                        } else if (gateRand < (2 * ONE_R1)) {
                            gateRand = 2 * qReg->Rand();
                            if (gateRand < ONE_R1) {
                                qReg->CY(b1, b2);
                            } else {
                                qReg->AntiCY(b1, b2);
                            }
                        } else if (gateRand < (3 * ONE_R1)) {
                            gateRand = 2 * qReg->Rand();
                            if (gateRand < ONE_R1) {
                                qReg->CZ(b1, b2);
                            } else {
                                qReg->AntiCZ(b1, b2);
                            }
                        }
                        // else - identity
                    } else {
                        b3 = pickRandomBit(qReg, &unusedBits);

                        gateRand = DimCountMultiQb * qReg->Rand();

                        if (gateRand < ONE_R1) {
                            gateRand = 2 * qReg->Rand();
                            if (gateRand < ONE_R1) {
                                qReg->CCNOT(b1, b2, b3);
                            } else {
                                qReg->AntiCCNOT(b1, b2, b3);
                            }
                        } else if (gateRand < (2 * ONE_R1)) {
                            gateRand = 2 * qReg->Rand();
                            if (gateRand < ONE_R1) {
                                qReg->CCY(b1, b2, b3);
                            } else {
                                qReg->AntiCCY(b1, b2, b3);
                            }
                        } else if (gateRand < (3 * ONE_R1)) {
                            gateRand = 2 * qReg->Rand();
                            if (gateRand < ONE_R1) {
                                qReg->CCZ(b1, b2, b3);
                            } else {
                                qReg->AntiCCZ(b1, b2, b3);
                            }
                        }
                        // else - identity
                    }
                }
            }

            qReg->MAll();
        },
        1, 20, false, false, false);
}
