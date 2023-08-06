# from qiskit import QuantumCircuit, transpile
# from qiskit.quantum_info.operators import Operator
# from qiskit.quantum_info.random import random_unitary
# from qclib.unitary import unitary, _apply_a2
# import time
#
#
# n = 4
#
# a = random_unitary(2 ** n)
#
#
# start = time.time()
#
# qc = unitary(a.data, decomposition='qsd', apply_a2=True)
# # qc = _apply_a2(qc)
# qc = transpile(qc, basis_gates=['u', 'cx'])
# end = time.time()
# print(end - start)
# print(qc.count_ops())
#
# print(Operator(qc).equiv(Operator(a)))


import numpy as np
import time
from qclib.state_preparation import LowRankInitialize
from qiskit import QuantumCircuit, transpile

n_qubits = 10 # number of qubits
opt_level = 3

random_state = np.random.rand(2 ** n_qubits) + np.random.rand(2 ** n_qubits)*1j
random_state = random_state / np.linalg.norm(random_state)

start = time.time()
lrsp_circuit = QuantumCircuit(n_qubits)
LowRankInitialize.initialize(lrsp_circuit, random_state)
lrsp_circuit = transpile(lrsp_circuit, basis_gates=['u', 'cx'], optimization_level=opt_level)
end = time.time()
lrsp_time = end - start
print('arXiv:2111.03132')
print('lrsp_time (s) = ', lrsp_time)
print('lrsp_cnots = ', lrsp_circuit.count_ops()['cx'])
print('lrsp_depth = ', lrsp_circuit.depth())
print()

# start = time.time()
# qiskit_initialize_circuit = QuantumCircuit(n_qubits)
# qiskit_initialize_circuit.initialize(random_state)
# qiskit_initialize_circuit = transpile(qiskit_initialize_circuit, basis_gates=['u', 'cx'], optimization_level=opt_level)
# end = time.time()
# initialize_time = end - start
# print('qiskit implementation of arXiv:quant-ph/0406176')
# print('qiskit_initialize_time (s) = ', initialize_time)
# print('qiskit_initialize_cnots = ', qiskit_initialize_circuit.count_ops()['cx'])
# print('qiskit_initialize_depth = ', qiskit_initialize_circuit.depth())
# print()

start = time.time()
qiskit_isometry_circuit = QuantumCircuit(n_qubits)
qiskit_isometry_circuit.iso(random_state, qiskit_isometry_circuit.qubits, [])
qiskit_isometry_circuit = transpile(qiskit_isometry_circuit, basis_gates=['u', 'cx'], optimization_level=opt_level)
end = time.time()
iso_time = end - start
print('qiskit implementation of arXiv:1501.06911')
print('qiskit_iso_time (s) = ', iso_time)
print('qiskit_iso_cnots = ', qiskit_isometry_circuit.count_ops()['cx'])
print('qiskit_iso_depth = ', qiskit_isometry_circuit.depth())
print()