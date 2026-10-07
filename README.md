# Qiskit QRNG demonstration

This small experiment prepares one qubit in the equal superposition
`(|0> + |1>) / sqrt(2)` with a Hadamard gate, measures it, and compares the
observed bit counts with a sample from Python's `random.Random`.

## Run

Use Python 3.10 or newer with a version supported by your Qiskit/Aer wheels,
then install the dependencies and run:

```sh
python -m pip install -r requirements.txt
python qrng_demo.py
python qrng_demo.py --shots 10000 --seed 7 --python-seed 7
python -m unittest -v
```

The defaults use 10,000 measurements and fixed seeds so the experiment can be
reproduced with the same compatible software stack. Different Qiskit/Aer
versions or platforms may not produce identical simulator streams.

## What the statistics mean

For each source, the script reports the number of zeros and ones, the fraction
of ones, and Pearson's chi-square goodness-of-fit statistic for the null
hypothesis that the two outcomes have equal probability (one degree of
freedom). Its p-value quantifies how unusual that count imbalance would be
under this model. It is not the probability that the source is random and does
not test bit independence; a large p-value does not prove randomness.

## Important backend limitation

This example uses **Qiskit AerSimulator**, which simulates the circuit on a
classical computer. It demonstrates the circuit and analysis, but its output
is not physical quantum entropy and should not be presented as a true QRNG.
For physical quantum randomness, run the same circuit on an accessible
quantum-hardware backend using that provider's current authentication and
execution workflow. Hardware access, credentials, queueing, and provider
packages are intentionally not assumed or bundled here.
