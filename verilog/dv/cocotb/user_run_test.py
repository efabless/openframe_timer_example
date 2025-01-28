from caravel_cocotb.scripts.verify_cocotb.RunTest import RunTest


class UserRunTest(RunTest):
    def __init__(self, args, paths, test, logger) -> None:
        super().__init__(args, paths, test, logger)

    # since exmaple has no cpu no hex needed
    def hex_generate(self) -> str:
        return "hex_generated"

    def write_vcs_includes_file(self):
        self.vcs_dirs = ""
        self.generate_includes()

    def write_iverilog_includes_file(self):
        self.iverilog_dirs = " "
        self.iverilog_dirs += f"-I {self.paths.USER_PROJECT_ROOT}/verilog/rtl"
        self.generate_includes()

    def iverilog_compile(self):
        macros = " -D" + " -D".join(self.test.macros)
        compile_command = (
            f"cd {self.test.compilation_dir} &&"
            f"iverilog -g2012 -Ttyp {macros} {self.iverilog_dirs} -o {self.test.compilation_dir}/sim.vvp"
            f" {self.paths.USER_PROJECT_ROOT}/rtl/toplevel_cocotb.v -s caravel_top"
        )
        docker_compilation_command = self._iverilog_docker_command_str(compile_command)
        self.run_command_write_to_file(
            docker_compilation_command if not self.args.no_docker else compile_command,
            self.test.compilation_log,
            self.logger,
            quiet=False if self.args.verbosity == "debug" else True,
        )

    def generate_includes(self):
        if self.test.sim == "RTL":
            include_list = f"{self.paths.USER_PROJECT_ROOT}/verilog/includes/includes.rtl.caravel_user_project"
        elif self.test.sim == "GL":
            include_list = f"{self.paths.USER_PROJECT_ROOT}/verilog/includes/includes.gl.caravel_user_project"
        elif self.test.sim == "GL_SDF":
            include_list = f"{self.paths.USER_PROJECT_ROOT}/verilog/includes/includes.gl+sdf.caravel_user_project"
        includes_files = ""
        with open(include_list, "r") as f:
            for line in f:
                # Remove leading and trailing whitespace
                line = line.strip()
                # Check if line is not empty or a comment
                if line and not line.startswith("#"):
                    # Replace $(VERILOG_PATH) with actual path
                    line = line.replace("$(VERILOG_PATH)", self.paths.VERILOG_PATH)
                    line = line.replace("$(CARAVEL_PATH)", self.paths.CARAVEL_PATH)
                    line = line.replace(
                        "$(USER_PROJECT_VERILOG)",
                        f"{self.paths.USER_PROJECT_ROOT}/verilog",
                    )
                    line = line.replace("$(PDK_ROOT)", f"{self.paths.PDK_ROOT}")
                    line = line.replace("$(PDK)", f"{self.paths.PDK}")
                    # Extract file path from command
                    if line.startswith("-v"):
                        file_path = line.split(" ")[1]
                        includes_files += f'`include "{file_path}"\n'
        self.test.includes_file = f"{self.test.compilation_dir}/includes.v"
        open(self.test.includes_file, "w").write(includes_files)