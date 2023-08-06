#
# Copyright (c) 2022 TUM Department of Electrical and Computer Engineering.
#
# This file is part of MLonMCU.
# See https://github.com/tum-ei-eda/mlonmcu.git for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""MLonMCU OVPSim Target definitions"""

import os
import re
from pathlib import Path

from mlonmcu.logging import get_logger
from .common import cli, execute
from .riscv import RISCVTarget
from .metrics import Metrics

logger = get_logger()


class OVPSimTarget(RISCVTarget):
    """Target using an ARM FVP (fixed virtual platform) based on a Cortex M55 with EthosU support"""

    FEATURES = ["vext", "pext", "gdbserver"]

    DEFAULTS = {
        **RISCVTarget.DEFAULTS,
        "vlen": 32,  # vectorization=off
        "enable_vext": False,
        "enable_pext": False,
        "enable_fpu": True,
        "variant": "RVB32I",
        # "extensions": "MAFDCV",
        "extensions": "MAFDC",  # rv32gc
    }
    REQUIRED = RISCVTarget.REQUIRED + ["ovpsim.exe"]

    def __init__(self, name="ovpsim", features=None, config=None):
        super().__init__(name, features=features, config=config)

    @property
    def ovpsim_exe(self):
        return Path(self.config["ovpsim.exe"])

    @property
    def variant(self):
        return str(self.config["variant"])

    @property
    def extensions(self):
        ret = str(self.config["extensions"])

        if self.enable_pext:
            if "P" not in ret:
                ret += "BP"
        if self.enable_vext:
            if "V" not in ret:
                ret += "V"
        return ret

    @property
    def vlen(self):
        return int(self.config["vlen"])

    @property
    def enable_fpu(self):
        return bool(self.config["enable_fpu"])

    @property
    def enable_vext(self):
        return bool(self.config["enable_vext"])

    @property
    def enable_pext(self):
        return bool(self.config["enable_pext"])

    @property
    def arch(self):
        ret = str(self.config["arch"])
        if self.enable_pext:
            if "p" not in ret[2:]:
                ret += "p"
        if self.enable_vext:
            if "v" not in ret[2:]:
                ret += "v"
        return ret

    def get_default_ovpsim_args(self):
        args = [
            "--variant",
            self.variant,
            "--override",
            f"riscvOVPsim/cpu/add_Extensions={self.extensions}",
            "--override",
            "riscvOVPsim/cpu/unaligned=T",
        ]
        if self.enable_pext:
            args.extend(
                [
                    "--override",
                    "riscvOVPsim/cpu/dsp_version=0.9.6",
                    "--override",
                    "riscvOVPsim/cpu/bitmanip_version=1.0.0",
                ]
            )
        if self.enable_vext:
            assert self.enable_fpu, "Spike V-Extension requires enabled FPU"
            args.extend(
                [
                    "--override",
                    "riscvOVPsim/cpu/vector_version=1.0-draft-20210130",
                    "--override",
                    f"riscvOVPsim/cpu/VLEN={self.vlen}",
                    "--override",
                    "riscvOVPsim/cpu/ELEN=32",
                ]
            )
            args.extend(["--override", f"riscvOVPsim/cpu/mstatus_VS={int(self.enable_vext)}"])
        if self.enable_fpu:
            assert "F" in self.extensions
            # if "F" not in self.extensions:
            #     self.extensions += "F"
        args.extend(["--override", f"riscvOVPsim/cpu/mstatus_FS={int(self.enable_fpu)}"])
        if False:  # ?
            args.append("--trace")
            args.extend(["--port", "3333"])
            args.append("--gdbconsole")
        return args

    def exec(self, program, *args, cwd=os.getcwd(), **kwargs):
        """Use target to execute a executable with given arguments"""
        ovpsim_args = []

        ovpsim_args.extend(["--program", str(program)])
        ovpsim_args.extend(self.get_default_ovpsim_args())

        if len(self.extra_args) > 0:
            ovpsim_args.extend(self.extra_args.split(" "))

        if self.timeout_sec > 0:
            raise NotImplementedError

        ret = execute(
            self.ovpsim_exe.resolve(),
            *ovpsim_args,
            *args,  # Does this work?
            **kwargs,
        )
        return ret

    def parse_stdout(self, out):
        # cpi = 1
        cpu_cycles = re.search(r"  Simulated instructions:(.*)", out)
        if not cpu_cycles:
            raise RuntimeError("unexpected script output (cycles)")
            cycles = None
        else:
            cycles = int(cpu_cycles.group(1).replace(",", ""))
        mips = None  # TODO: parse mips?
        mips_match = re.search(r"  Simulated MIPS:(.*)", out)
        if mips_match:
            mips_str = float(mips_match.group(1))
            if "run too short for meaningful result" not in mips:
                mips = float(mips_str)
        return cycles, mips

    def get_metrics(self, elf, directory, handle_exit=None, num=None):
        assert num is None
        out = ""
        if self.print_outputs:
            out += self.exec(elf, cwd=directory, live=True, handle_exit=handle_exit)
        else:
            out += self.exec(
                elf, cwd=directory, live=False, print_func=lambda *args, **kwargs: None, handle_exit=handle_exit
            )
        cycles, mips = self.parse_stdout(out)

        metrics = Metrics()
        metrics.add("Total Cycles", cycles)
        metrics.add("MIPS", cycles, optional=True)

        return metrics, out, []


if __name__ == "__main__":
    cli(target=OVPSimTarget)
