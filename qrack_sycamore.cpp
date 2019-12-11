//////////////////////////////////////////////////////////////////////////////////////
//
// (C) Daniel Strano and the Qrack contributors 2017-2019. All rights reserved.
//

#include "qrack_benchmarks.hpp"

using namespace Qrack;

int main()
{
    // See https://doi.org/10.1038/s41586-019-1666-5

    benchmarkLoop([&](QInterfacePtr qReg, int n, int depth) {

        // The test runs 2 bit gates according to a tiling sequence.
        // The 1 bit indicates +/- column offset.
        // The 2 bit indicates +/- row offset.
        std::list<bitLenInt> gateSequence = { 0, 3, 1, 2, 1, 2, 0, 3 };

        // Depending on which element of the sequential tiling we're running, per depth iteration,
        // we need to start either with row "0" or row "1".
        std::map<bitLenInt, bitLenInt> sequenceRowStart;
        sequenceRowStart[0] = 1;
        sequenceRowStart[1] = 1;
        sequenceRowStart[2] = 0;
        sequenceRowStart[3] = 0;

        // We factor the qubit count into two integers, as close to a perfect square as we can.
        int rowLen = std::sqrt(n);
        while (((n / rowLen) * rowLen) != n) {
            rowLen--;
        }
        int colLen = n / rowLen;

        // "1/6 of a full CZ" is read to indicate the 6th root of the gate operator.
        complex sixthRoot = std::pow(-ONE_CMPLX, (real1)(1.0 / 6.0));

        real1 gateRand;
        bitLenInt gate;
        int b1, b2;
        bitLenInt i, d;
        int row, col;
        int tempRow, tempCol;

        bool startsEvenRow;

        bitLenInt controls[1];

        // We repeat the entire prepartion for "depth" iterations.
        // We can avoid maximal representational entanglement of the state as a single Schr{\"o}dinger method unit.
        // See https://arxiv.org/abs/1710.05867
        for (d = 0; d < depth; d++) {
            for (i = 0; i < n; i++) {
                gateRand = qReg->Rand();

                // Each individual bit has one of these 3 gates applied at random.
                // Qrack has optimizations for gates including X, Y, and particularly H, but these "Sqrt" variants
                // are handled as general single bit gates.
                if (gateRand < (ONE_R1 / 3)) {
                    qReg->SqrtX(i);
                } else if (gateRand < (2 * ONE_R1 / 3)) {
                    qReg->SqrtY(i);
                } else {
                    // "Square root of W" is understood to be the square root of the Walsh-Hadamard transform,
                    // (a.k.a "H" gate).
                    qReg->SqrtH(i);
                }

                // This is a QUnit specific optimization attempt method that can "compress" (or "Schmidt decompose")
                // the representation without changing the logical state of the QUnit, up to float error:
                // qReg->TrySeparate(i);
            }

            gate = gateSequence.front();
            gateSequence.pop_front();
            gateSequence.push_back(gate);

            startsEvenRow = ((sequenceRowStart[gate] & 1U) == 0U);

            for (row = sequenceRowStart[gate]; row < (n / rowLen); row += 2) {
                for (col = 0; col < (n / colLen); col++) {
                    // The following pattern is isomorphic to a 45 degree bias on a rectangle, for couplers.
                    // In this test, the boundaries of the rectangle have no couplers.
                    // In a perfect square, in the interior bulk, one 2 bit gate is applied for every pair of bits,
                    // (as many gates as 1/2 the number of bits). (Unless n is a perfect square, the "row length"
                    // has to be factored into a rectangular shape, and "n" is sometimes prime or factors
                    // awkwardly.)

                    tempRow = row;
                    tempCol = col;

                    tempRow += ((gate & 2U) ? 1 : -1);

                    if (startsEvenRow) {
                        tempCol += ((gate & 1U) ? 0 : -1);
                    } else {
                        tempCol += ((gate & 1U) ? 1 : 0);
                    }

                    if ((tempRow < 0) || (tempCol < 0) || (tempRow >= rowLen) || (tempCol >= colLen)) {
                        continue;
                    }

                    b1 = row * rowLen + col;
                    b2 = tempRow * rowLen + tempCol;

                    // For the efficiency of QUnit's mapper, we transpose the row and column.
                    tempCol = b1 / rowLen;
                    tempRow = b1 - (tempCol * rowLen);
                    b1 = (tempRow * rowLen) + tempCol;

                    tempCol = b2 / rowLen;
                    tempRow = b2 - (tempCol * rowLen);
                    b2 = (tempRow * rowLen) + tempCol;

                    // "iSWAP" is read to be a SWAP operation that imparts a phase factor of i if the bits are
                    // different.
                    qReg->ISwap(b1, b2);
                    // "1/6 of CZ" is read to indicate the 6th root.
                    controls[0] = b1;
                    qReg->ApplyControlledSinglePhase(controls, 1U, b2, ONE_CMPLX, sixthRoot);
                    // Note that these gates are both symmetric under exchange of "b1" and "b2".
                }
            }
        }

        // We measure all bits once, after the circuit is run.
        qReg->MReg(0, n);
    }, 1, 20);
}
