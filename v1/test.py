from assemblers.frisc_assembler import FRISCAssembler
from simulators.frisc_simulator import FRISCSimulator

FRISCAssembler.assemble('test.a')
fs = FRISCSimulator(65536)
fs.load('test.p')
fs.run()
print(fs.state)
for rn, rv in fs.registers.items():
    print(rn, ':', rv.to_pretty_hex_string())
