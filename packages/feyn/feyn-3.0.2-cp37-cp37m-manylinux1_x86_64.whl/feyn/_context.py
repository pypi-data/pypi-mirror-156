import os
from typing import List, Tuple

import feyn
import _qepler

class Context:

    def __init__(self):
        self.registers = []


    def lookup_by_fname(self, name: str, arity: int) -> int:
        """Recover the opcode of 'fname' with arity 'arity'."""
        assert arity <= 2

        if arity == 0:
            try:
                ix = self.registers.index(name)
            except ValueError:
                # New register
                ix = len(self.registers)
                self.registers.append(name)

            return 10000 + ix

        for opcode, fname in feyn.OPCODE_MAP.items():
            if fname == name and opcode // 1000 == arity:
                return opcode

        raise ValueError(f"Unaware of '{name}' with arity {arity} in the context.")

    def get_codes(self, arity: int, names: list):
        if arity == 0:
            # A register
            names = set(names)
            extra = sorted(names.difference(self.registers))
            self.registers += extra

            base = 10000
            return [base + ix for ix, name in enumerate(self.registers) if name in names]

        if names is None:
            names = feyn.OPCODE_MAP.values()

        # An operator
        return [
            opcode
            for opcode, function_name in feyn.OPCODE_MAP.items()
            if function_name in names and opcode // 1000 == arity
        ]

    def to_model(self, program, output_name, stypes={}):
        l = len(program)
        if l < 2:
            # TODO: Why not raise an exception?
            # Invalid program
            return None

        names = []
        fnames = []

        for ix in range(l):
            if ix == 0:
                names.append(output_name)
                stype = stypes.get(output_name, "f")
                if stype in ("b"):  # Classifier?
                    fnames.append("out:lr")
                else:
                    fnames.append("out:linear")
                continue

            code = program[ix]
            arity = program.arity_at(ix)

            if arity == 0:
                name = self.registers[code - 10000]
                names.append(name)

                stype = stypes.get(name, "f")
                if stype in ["c", "cat", "categorical"]:
                    fnames.append("in:cat")
                else:
                    fnames.append("in:linear")
            else:
                name = ""
                fname = feyn.OPCODE_MAP.get(code)
                fnames.append(fname)
                names.append("")

        return feyn.Model(program, names, fnames)
