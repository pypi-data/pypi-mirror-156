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
"""MLonMCU ETISS/Pulpino Target definitions"""

import os
import re
import csv
from pathlib import Path

from mlonmcu.logging import get_logger
from mlonmcu.artifact import Artifact, ArtifactFormat
from mlonmcu.feature.features import SUPPORTED_TVM_BACKENDS
from .common import cli, execute
from .riscv import RISCVTarget
from .metrics import Metrics

logger = get_logger()


class EtissPulpinoTarget(RISCVTarget):
    """Target using a Pulpino-like VP running in the ETISS simulator"""

    FEATURES = ["gdbserver", "etissdbg", "trace", "log_instrs"]

    DEFAULTS = {
        **RISCVTarget.DEFAULTS,
        "gdbserver_enable": False,
        "gdbserver_attach": False,
        "gdbserver_port": 2222,
        "debug_etiss": False,
        "trace_memory": False,
        "plugins": [],
        "verbose": False,
        "cpu_arch": "RISCV",  # For V/P-Extension support, use RV32IMAFDCPV
        "etissvp.rom_start": 0x0,
        "etissvp.rom_size": 0x800000,  # 8 MB
        "etissvp.ram_start": 0x800000,
        "etissvp.ram_size": 0x4000000,  # 64 MB
        "etissvp.cycle_time_ps": 31250,  # 32 MHz
    }
    REQUIRED = RISCVTarget.REQUIRED + ["etiss.src_dir", "etiss.install_dir", "etissvp.script"]

    def __init__(self, name="etiss_pulpino", features=None, config=None):
        super().__init__(name, features=features, config=config)
        self.metrics_script = Path(self.etiss_src_dir) / "src" / "bare_etiss_processor" / "get_metrics.py"

    @property
    def etiss_src_dir(self):
        return self.config["etiss.src_dir"]

    @property
    def etiss_dir(self):
        return self.config["etiss.install_dir"]

    @property
    def etiss_script(self):
        return self.config["etissvp.script"]

    @property
    def gdbserver_enable(self):
        return bool(self.config["gdbserver_enable"])

    @property
    def gdbserver_attach(self):
        return bool(self.config["gdbserver_attach"])

    @property
    def gdbserver_port(self):
        return int(self.config["gdbserver_port"])

    @property
    def debug_etiss(self):
        return bool(self.config["debug_etiss"])

    @property
    def trace_memory(self):
        return bool(self.config["trace_memory"])

    @property
    def plugins(self):
        return self.config["plugins"]

    @property
    def verbose(self):
        return bool(self.config["verbose"])

    @property
    def rom_start(self):
        return int(self.config["etissvp.rom_start"])

    @property
    def rom_size(self):
        return int(self.config["etissvp.rom_size"])

    @property
    def ram_start(self):
        return int(self.config["etissvp.ram_start"])

    @property
    def ram_size(self):
        return int(self.config["etissvp.ram_size"])

    @property
    def cycle_time_ps(self):
        return int(self.config["etissvp.cycle_time_ps"])

    @property
    def cpu_arch(self):
        return self.config["cpu_arch"]

    # TODO: other properties

    def write_ini(self, path):
        # TODO: Either create artifact for ini or prefer to use cmdline args.
        with open(path, "w") as f:
            if self.cpu_arch:
                f.write("[StringConfigurations]\n")
                f.write(f"arch.cpu={self.cpu_arch}\n")
            f.write("[IntConfigurations]\n")
            f.write(f"simple_mem_system.memseg_origin_00={hex(self.rom_start)}\n")
            f.write(f"simple_mem_system.memseg_length_00={hex(self.rom_size)}\n")
            f.write(f"simple_mem_system.memseg_origin_01={hex(self.ram_start)}\n")
            f.write(f"simple_mem_system.memseg_length_01={hex(self.ram_size)}\n")
            f.write("\n")
            f.write(f"arch.cpu_cycle_time_ps={self.cycle_time_ps}\n")

            if self.gdbserver_enable:
                f.write("[Plugin gdbserver]\n")
                # This could also be accomplished using `--plugin.gdbserver.port` on the cmdline
                f.write(f"plugin.gdbserver.port={self.gdbserver_port}")

    def exec(self, program, *args, cwd=os.getcwd(), **kwargs):
        """Use target to execute a executable with given arguments"""
        etiss_script_args = []
        if len(self.extra_args) > 0:
            etiss_script_args.extend(self.extra_args.split(" "))

        # TODO: this is outdated
        # TODO: validate features (attach xor noattach!)
        if self.debug_etiss:
            etiss_script_args.append("gdb")
        if self.gdbserver_enable:
            etiss_script_args.append("tgdb")
            if not self.gdbserver_attach:
                etiss_script_args.append("noattach")
        if self.trace_memory:
            etiss_script_args.append("trace")
            etiss_script_args.append("nodmi")
        if self.verbose:
            etiss_script_args.append("v")
        # Alternative to stdout parsing: etiss_script_args.append("--vp.stats_file_path=stats.json")

        # TODO: working directory?
        etiss_ini = os.path.join(cwd, "custom.ini")
        self.write_ini(etiss_ini)
        etiss_script_args.append("-i" + etiss_ini)
        if len(self.plugins):
            plugins_str = " ".join(self.plugins)  # TODO: find out separator
            etiss_script_args.extend(["-p", plugins_str])

        if self.timeout_sec > 0:
            raise NotImplementedError
        else:
            ret = execute(
                Path(self.etiss_script).resolve(),
                program,
                *etiss_script_args,
                *args,
                cwd=cwd,
                **kwargs,
            )
        return ret

    def parse_stdout(self, out, handle_exit=None):
        exit_match = re.search(r"exit called with code: (.*)", out)
        if exit_match:
            exit_code = int(exit_match.group(1))
            if handle_exit is not None:
                exit_code = handle_exit(exit_code)
            if exit_code != 0:
                logger.error("Execution failed - " + out)
                raise RuntimeError(f"unexpected exit code: {exit_code}")
        error_match = re.search(r"ETISS: Error: (.*)", out)
        if error_match:
            error_msg = error_match.group(1)
            raise RuntimeError(f"An ETISS Error occured during simulation: {error_msg}")

        cpu_cycles = re.search(r"CPU Cycles \(estimated\): (.*)", out)
        if not cpu_cycles:
            if exit_code == 0:
                logger.warning("unexpected script output (cycles)")
            cycles = None
        else:
            cycles = int(float(cpu_cycles.group(1)))
        mips_match = re.search(r"MIPS \(estimated\): (.*)", out)
        if not mips_match:
            if exit_code == 0:
                raise logger.warning("unexpected script output (mips)")
            mips = None
        else:
            mips = int(float(mips_match.group(1)))

        return cycles, mips

    def get_metrics(self, elf, directory, handle_exit=None, num=None):
        assert num is None
        out = ""
        if self.trace_memory:
            trace_file = os.path.join(directory, "dBusAccess.csv")
            if os.path.exists(trace_file):
                os.remove(trace_file)
        else:
            trace_file = None

        metrics_file = os.path.join(directory, "metrics.csv")
        if os.path.exists(metrics_file):
            os.remove(metrics_file)

        if self.print_outputs:
            out += self.exec(elf, cwd=directory, live=True, handle_exit=handle_exit)
        else:
            out += self.exec(
                elf, cwd=directory, live=False, print_func=lambda *args, **kwargs: None, handle_exit=handle_exit
            )
        total_cycles, mips = self.parse_stdout(out, handle_exit=handle_exit)

        get_metrics_args = [elf]
        etiss_ini = os.path.join(directory, "custom.ini")
        if os.path.exists(etiss_ini):
            get_metrics_args.extend(["--ini", etiss_ini])
        if trace_file:
            get_metrics_args.extend(["--trace", trace_file])
        get_metrics_args.extend(["--out", metrics_file])
        if self.print_outputs:
            out += execute(self.metrics_script.resolve(), *get_metrics_args, live=True)
        else:
            out += execute(
                self.metrics_script.resolve(),
                *get_metrics_args,
                live=False,
                cwd=directory,
                print_func=lambda *args, **kwargs: None,
            )

        metrics = Metrics()
        metrics.add("Total Cycles", total_cycles)
        metrics.add("MIPS", mips, optional=True)

        metrics_file = os.path.join(directory, "metrics.csv")
        with open(metrics_file, "r") as handle:
            metrics_content = handle.read()
            lines = metrics_content.splitlines()
            reader = csv.DictReader(lines)
            data = list(reader)[0]

            def get_rom_sizes(data):
                assert "rom_rodata" in data
                rom_ro = int(data["rom_rodata"])
                assert "rom_code" in data
                rom_code = int(data["rom_code"])
                assert "rom_misc" in data
                rom_misc = int(data["rom_misc"])

                rom_total = rom_ro + rom_code + rom_misc
                return rom_total, rom_ro, rom_code, rom_misc

            def get_ram_sizes(data):
                assert "ram_data" in data
                ram_data = int(data["ram_data"])
                assert "ram_zdata" in data
                ram_zdata = int(data["ram_zdata"])
                ram_total = ram_data + ram_zdata
                if self.trace_memory:
                    assert "ram_stack" in data
                    ram_stack = int(data["ram_stack"])
                    assert "ram_heap" in data
                    ram_heap = int(data["ram_heap"])
                    ram_total += ram_stack + ram_heap
                else:
                    ram_stack = None
                    ram_heap = None
                return ram_total, ram_data, ram_zdata, ram_stack, ram_heap

            rom_total, rom_ro, rom_code, rom_misc = get_rom_sizes(data)
            ram_total, ram_data, ram_zdata, ram_stack, ram_heap = get_ram_sizes(data)
            metrics.add("Total ROM", rom_total)
            metrics.add("Total RAM", ram_total)
            metrics.add("ROM read-only", rom_ro)
            metrics.add("ROM code", rom_code)
            metrics.add("ROM misc", rom_misc)
            metrics.add("RAM data", ram_data)
            metrics.add("RAM zero-init data", ram_zdata)
            if self.trace_memory:
                metrics.add("RAM stack", ram_stack)
                metrics.add("RAM heap", ram_heap)

        artifacts = []
        ini_content = open(etiss_ini, "r").read()
        ini_artifact = Artifact("custom.ini", content=ini_content, fmt=ArtifactFormat.TEXT)
        artifacts.append(ini_artifact)

        return metrics, out, artifacts

    def get_target_system(self):
        return self.name

    def get_platform_defs(self, platform):
        assert platform == "mlif"
        ret = super().get_platform_defs(platform)
        ret["ETISS_DIR"] = self.etiss_dir
        ret["PULPINO_ROM_START"] = self.rom_start
        ret["PULPINO_ROM_SIZE"] = self.rom_size
        ret["PULPINO_RAM_START"] = self.ram_start
        ret["PULPINO_RAM_SIZE"] = self.ram_size
        return ret

    def get_backend_config(self, backend):
        ret = super().get_backend_config(backend)
        if backend in SUPPORTED_TVM_BACKENDS:
            ret.update({"target_model": "etissvp"})
        return ret


if __name__ == "__main__":
    cli(target=EtissPulpinoTarget)
