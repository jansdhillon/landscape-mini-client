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

        self.name = res.stdout.split("Launched:")[1].strip()

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

    def exec(self, cmd: str) -> str:

        cmd_list = ["multipass", "exec", "-n", self.name, "--", "sh", "-c", cmd]

        res = subprocess.run(cmd_list, check=True, capture_output=True, text=True)

        return res.stdout.strip()


instance = MultipassInstance()
print(instance)
print(instance.exec("echo hello"))
