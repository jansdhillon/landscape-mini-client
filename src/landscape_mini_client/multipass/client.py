import re
import subprocess
from typing import Literal


class MultipassInstance:
    """Instance of Ubuntu managed by Multipass"""

    def __init__(
        self,
        name: str | None = None,
        cpus: int = 1,
        memory: int = 1,
        disk: int = 15,
        series: Literal["noble", "jammy", "focal"] = "noble",
    ):
        self.name = name if name is not None else None
        self._cpus = str(cpus)
        self.memory = memory
        self.disk = disk
        self.series = series

        cmd = ["multipass", "launch", self.series]

        if self.name is not None:
            cmd.extend(["--name", self.name])

        cmd.extend(["--cpus", self._cpus])

        cmd.extend(["--memory", f"{self.memory}G"])

        cmd.extend(["--disk", f"{self.disk}G"])

        res = subprocess.run(cmd, check=True, capture_output=True, text=True)

        self.name = re.sub(r"[^a-z-]", "", res.stdout.split("Launched:")[1].strip())

        # Push SSH key

        # subprocess.run(
        #     [
        #         f"multipass transfer ~/.ssh/id_rsa {self.name}:/home/ubuntu/.ssh/id_rsa",
        #         f"multipass transfer ~/.ssh/id_rsa.pub {self.name}:/home/ubuntu/.ssh/id_rsa.pub",
        #     ],
        #     check=True,
        # )

    def __repr__(self) -> str:
        """Return string representation of instance configuration"""
        attrs = []

        attrs.append(f"cpus={self._cpus}")

        attrs.append(f"memory={self.memory}G")

        attrs.append(f"disk={self.disk}G")

        return f"MultipassInstance(name='{self.name}', {', '.join(attrs)})"

    @property
    def cpus(self):
        """Fetch CPU info dynamically"""
        result = subprocess.run(
            ["multipass", "info", self.name], capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "CPU" in line:
                return line.split(":")[1].strip()
        return None

    def exec(self, cmd: str, _print=True) -> str | None:
        """Run a single command inside Multipass"""
        cmd_list = ["multipass", "exec", "-n", self.name, "--", "sh", "-c", cmd]

        res = subprocess.run(cmd_list, check=True, capture_output=True, text=True)

        output = res.stdout.strip()
        if _print:
            print(output)
        return output

    def execl(self, cmds: list[str], _print=True) -> str | None:
        """Run a list of commands inside Multipass"""

        full_cmd = " && ".join(cmds)

        cmd_list = ["multipass", "exec", "-n", self.name, "--", "sh", "-c", full_cmd]

        res = subprocess.run(cmd_list, check=True, capture_output=True, text=True)

        output = res.stdout.strip()
        if _print:
            print(output)
        return output


gh_username = "jansdhillon"
instance = MultipassInstance()
print(instance)
instance.execl(
    [
        f"git clone https://github.com/{gh_username}/landscape-mini-client.git",
        "cd landscape-mini-client",
        "python3 -m venv ./venv",
        ". ./venv/bin/activate",
        "pip install -r ./requirements.txt",
        # "python -m src.landscape_mini_client register \
        # --account-name=standalone \
        # --computer-title=mini-client \
        # --server-host=localhost \
        # --port=8080",
    ]
)
