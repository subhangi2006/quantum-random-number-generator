"""Educational one-qubit QRNG workflow using Qiskit's local Aer simulator."""

from __future__ import annotations

import argparse
import math
import random
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class BitStats:
    zeros: int
    ones: int
    shots: int
    one_fraction: float
    chi_squared: float
    p_value: float


def summarize_bits(zeros: int, ones: int) -> BitStats:
    """Summarize a binary sample and test the 50/50 count hypothesis."""
    if not isinstance(zeros, int) or not isinstance(ones, int):
        raise TypeError("Bit counts must be integers.")
    if zeros < 0 or ones < 0:
        raise ValueError("Bit counts cannot be negative.")

    shots = zeros + ones
    if shots == 0:
        raise ValueError("At least one bit is required.")

    expected = shots / 2
    chi_squared = ((zeros - expected) ** 2 + (ones - expected) ** 2) / expected
    # For one degree of freedom, the chi-square survival function is erfc(sqrt(x/2)).
    p_value = math.erfc(math.sqrt(chi_squared / 2))
    return BitStats(
        zeros=zeros,
        ones=ones,
        shots=shots,
        one_fraction=ones / shots,
        chi_squared=chi_squared,
        p_value=p_value,
    )


def get_qiskit_counts(shots: int, seed: int) -> tuple[int, int]:
    """Measure |+> repeatedly on Aer and return (zero_count, one_count)."""
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise RuntimeError(
            "Qiskit and Qiskit Aer are required. Install them with "
            "'python -m pip install -r requirements.txt'."
        ) from exc

    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)

    result = AerSimulator().run(
        circuit,
        shots=shots,
        seed_simulator=seed,
    ).result()
    counts = result.get_counts(circuit)
    return counts.get("0", 0), counts.get("1", 0)


def get_python_random_counts(shots: int, seed: int) -> tuple[int, int]:
    """Generate a reproducible comparison sample using Python's PRNG."""
    bits = random.Random(seed).getrandbits(shots)
    ones = bits.bit_count()
    return shots - ones, ones


def print_summary(label: str, stats: BitStats) -> None:
    print(f"\n{label}")
    print(f"  Bits: 0={stats.zeros}, 1={stats.ones} (n={stats.shots})")
    print(f"  1 proportion: {stats.one_fraction:.4f}")
    print(f"  Chi-square (df=1): {stats.chi_squared:.4f}")
    print(f"  p-value: {stats.p_value:.6g}")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare a one-qubit Qiskit/Aer demo with Python's PRNG."
    )
    parser.add_argument("--shots", type=positive_int, default=10_000)
    parser.add_argument("--seed", type=nonnegative_int, default=7,
                        help="Aer simulator seed (default: 7)")
    parser.add_argument("--python-seed", type=nonnegative_int, default=7,
                        help="Python PRNG seed (default: 7)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        quantum_zeros, quantum_ones = get_qiskit_counts(args.shots, args.seed)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    random_zeros, random_ones = get_python_random_counts(
        args.shots, args.python_seed
    )
    print("Educational comparison - Aer is a classical simulator, not a QRNG hardware source.")
    print(f"Reproducibility settings: shots={args.shots}, Aer seed={args.seed}, "
          f"Python seed={args.python_seed}")
    print_summary("Qiskit Aer simulator", summarize_bits(quantum_zeros, quantum_ones))
    print_summary("Python random.Random", summarize_bits(random_zeros, random_ones))
    print(
        "\nThe chi-square p-value tests only whether the observed 0/1 counts "
        "fit a 50/50 model. It does not test independence or prove randomness; "
        "a simulator and Python's PRNG are both classically generated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
