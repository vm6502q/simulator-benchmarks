//////////////////////////////////////////////////////////////////////////////////////
//
// (C) Daniel Strano and the Qrack contributors 2017-2020. All rights reserved.
//

#include <list>

#include "qrack_benchmarks.hpp"

using namespace Qrack;

int main()
{
    benchmarkLoop([&](QInterfacePtr qReg, int n, int depth) {

        // The test runs 2 bit gates according to a tiling sequence.
        // The 1 bit indicates +/- column offset.
        // The 2 bit indicates +/- row offset.
        // This is the "ABCDCDAB" pattern, from the Cirq definition of the circuit in the supplemental materials to the
        // paper.
        std::list<bitLenInt> gateSequence = { 0, 3, 2, 1, 2, 1, 0, 3 };

        // We factor the qubit count into two integers, as close to a perfect square as we can.
        int colLen = std::sqrt(n);
        while (((n / colLen) * colLen) != n) {
            colLen--;
        }
        int rowLen = n / colLen;

        // std::cout<<"n="<<(int)n<<std::endl;
        // std::cout<<"rowLen="<<(int)rowLen<<std::endl;
        // std::cout<<"colLen="<<(int)colLen<<std::endl;

        real1 gateRand;
        bitLenInt gate;
        int b1, b2;
        bitLenInt i, d;
        int row, col;
        int tempRow, tempCol;

        std::vector<int> lastSingleBitGates;
        std::set<int>::iterator gateChoiceIterator;
        int gateChoice;

        // We repeat the entire prepartion for "depth" iterations.
        // We can avoid maximal representational entanglement of the state as a single Schr{\"o}dinger method unit.
        // See https://arxiv.org/abs/1710.05867
        for (d = 0; d < depth; d++) {
            for (i = 0; i < n; i++) {
                gateRand = qReg->Rand();

                // Each individual bit has one of these 3 gates applied at random.
                // The same gate is not applied twice consecutively in sequence.

                if (d == 0) {
                    // For the first iteration, we can pick any gate.

                    if (gateRand < (ONE_R1 / 4)) {
                        qReg->H(i);
                        lastSingleBitGates.push_back(0);
                    } else if (gateRand < (2 * ONE_R1 / 4)) {
                        qReg->X(i);
                        lastSingleBitGates.push_back(1);
                    } else if (gateRand < (3 * ONE_R1 / 4)) {
                        qReg->T(i);
                        // Don't IT on next iteration.
                        lastSingleBitGates.push_back(3);
                    } else {
                        qReg->IT(i);
                        // Don't T on next iteration.
                        lastSingleBitGates.push_back(2);
                    }
                } else {
                    // For all subsequent iterations after the first, we eliminate the choice of the same gate applied
                    // on the immediately previous iteration.

                    std::set<int> gateChoices = { 0, 1, 2, 3 };
                    gateChoiceIterator = gateChoices.begin();
                    std::advance(gateChoiceIterator, lastSingleBitGates[i]);
                    gateChoices.erase(gateChoiceIterator);

                    gateChoiceIterator = gateChoices.begin();
                    if (gateRand == 1) {
                        gateChoice = *(gateChoices.rbegin());
                    } else {
                        std::advance(gateChoiceIterator, (int)(gateRand * 3));
                    }
                    gateChoice = *gateChoiceIterator;
                    if (gateChoice == 0) {
                        qReg->H(i);
                        lastSingleBitGates[i] = 0;
                    } else if (gateChoice == 1) {
                        qReg->X(i);
                        lastSingleBitGates[i] = 1;
                    } else if (gateChoice == 2) {
                        qReg->T(i);
                        // Don't IT on next iteration.
                        lastSingleBitGates[i] = 3;
                    } else {
                        qReg->T(i);
                        // Don't T on next iteration.
                        lastSingleBitGates[i] = 2;
                    }
                }

                // This is a QUnit specific optimization attempt method that can "compress" (or "Schmidt decompose")
                // the representation without changing the logical state of the QUnit, up to float error:
                // qReg->TrySeparate(i);
            }

            gate = gateSequence.front();
            gateSequence.pop_front();
            gateSequence.push_back(gate);

            for (row = 1; row < rowLen; row += 2) {
                for (col = 0; col < colLen; col++) {
                    // The following pattern is isomorphic to a 45 degree bias on a rectangle, for couplers.
                    // In this test, the boundaries of the rectangle have no couplers.
                    // In a perfect square, in the interior bulk, one 2 bit gate is applied for every pair of bits,
                    // (as many gates as 1/2 the number of bits). (Unless n is a perfect square, the "row length"
                    // has to be factored into a rectangular shape, and "n" is sometimes prime or factors
                    // awkwardly.)

                    tempRow = row;
                    tempCol = col;

                    tempRow += ((gate & 2U) ? 1 : -1);
                    tempCol += (colLen == 1) ? 0 : ((gate & 1U) ? 1 : 0);

                    if ((tempRow < 0) || (tempCol < 0) || (tempRow >= rowLen) || (tempCol >= colLen)) {
                        continue;
                    }

                    b1 = row * colLen + col;
                    b2 = tempRow * colLen + tempCol;

                    gateRand = qReg->Rand();

                    if (gateRand < (ONE_R1 / 2)) {
                        if (qReg->Rand() < (ONE_R1 / 2)) {
                           std::swap(b1, b2);
                        }
                        qReg->CNOT(b1, b2);
                    } else {
                        qReg->CZ(b1, b2);
                    }
                }
            }
        }

        // We measure all bits once, after the circuit is run.
        qReg->MReg(0, n);
    }, 1, 20);
}
