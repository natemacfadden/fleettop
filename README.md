# fleettop

Live CPU, RAM, disk and GPU graphs for all your machines in one terminal,
nvtop-style — over plain SSH. Nothing to install on the machines you watch:
they need only `bash` and an SSH login.

```
fleettop  sample 1s   graphs view, v to switch   l lines   +/- time window   s save   q quit
gpu-box        CPU   3%  load 1.41/24    RAM 11.0/30.1 GiB    I/O read 0.0K/s  write 44K/s
               disk  / 68% 300G/444G  /mnt/ssd 78% 694G/890G  /mnt/hdd1 0% 57M/906G  /mnt/hdd2 79% 720G/906G
               gpu  RTX 5090 0% 25.2/31.8 GiB 40C 10W   RTX 5060 Ti 10% 1.5/15.9 GiB 44C 12W
┌─ ━━ cpu  ━━ ram ────────────────────────────── 100% ┐┌─ RTX 5090  ━━ util  ━━ mem ─────────────────── 100% ┐
│                                                     ││                                                     │
│                                                     ││─────────────────────────────────────────────────────│
│                                                     ││                                                     │
│                                                     ││─────────────────────────────────────────────────────│
│                                                     │└─ -53s ───────────────────────────────────────── now ┘
│                                                     │┌─ RTX 5060 Ti  ━━ util  ━━ mem ──────────────── 100% ┐
│─────────────────────────────────────────────────────││                                                     │
│                                                     ││                                                     │
│         ╭╮                                          ││──╮                                    ╭╮            │
│─────────╯╰──────────────────────────────────────────││─────────────────────────────────────────────────────│
└─ -53s ───────────────────────────────────────── now ┘└─ -53s ───────────────────────────────────────── now ┘
macbook        CPU   6%  load 1.39/10    RAM 16.5/32.0 GiB
               disk  / 72% 649G/898G
┌─ ━━ cpu  ━━ ram ───────────────────────────────────────────────────────────────────────────────────── 100% ┐
│                                                                                                            │
│                                                                                                            │
│                                                                                                            │
│                                                                                                            │
│                                                                                                            │
│                                   ─────────────────────────────────────────────────────────────────────────│
│                                                                                                            │
│                                                                                                            │
│                                                                                                            │
│                                   ──────╮    ╭──╮    ╭──╮    ╭────╮  ╭────╮  ╭────╮  ╭────╮  ╭──────╮ ╭────│
│                                         ╰────╯  ╰────╯  ╰────╯    ╰──╯    ╰──╯    ╰──╯    ╰──╯      ╰─╯    │
└─ -108s ─────────────────────────────────────────────────────────────────────────────────────────────── now ┘

```

## Install

Needs Python 3.9+ on the machine you run it from (Linux or macOS; on Windows,
use WSL). No dependencies.

```bash
pipx install git+https://github.com/natemacfadden/fleettop
# or
uv tool install git+https://github.com/natemacfadden/fleettop
# or, into the current environment
pip install git+https://github.com/natemacfadden/fleettop
```

Upgrade with `pipx upgrade fleettop` / `uv tool upgrade fleettop` /
`pip install -U git+https://github.com/natemacfadden/fleettop`.

## Telling it which machines

```bash
fleettop gpu01 me@gpu02 workstation     # hosts as arguments
fleettop -f ~/my-hosts                  # a hosts file
fleettop                                # ~/.config/fleettop/hosts if it exists,
                                        # otherwise just this machine
```

Arguments and `-f` files combine (and `-f` repeats). A hosts file is one host
per line; blank lines and `#` comments are ignored:

```
# ~/.config/fleettop/hosts
localhost          # this machine, read directly
gpu01
me@gpu02           # the big one
lab-mac            # an alias from ~/.ssh/config works too
```

A host is anything `ssh` accepts. SSH has to log in **without a prompt** — set
up keys (`ssh-copy-id host`) or an agent first. A host that doesn't answer
shows as offline and is retried every few seconds.

## Using it

| key | |
|---|---|
| `v` | graphs ↔ bars |
| `l` | solid lines ↔ braille dots (twice the detail, but reads as dots) |
| `+` / `-` | widen / narrow the time window, up to 6 hours |
| `s` | save the screen, with colors, to `~/.cache/fleettop/screen.ansi` (`cat` it to view) |
| `q` | quit |

Flags: `-n SECS` sample interval (default 2), `--bars` start in the bar view,
`--once` print one plain-text snapshot and exit (also what happens when output
isn't a terminal, so `fleettop | less` works).

Each number in a machine's header is colored like its line: cyan CPU, magenta
RAM, and in each GPU's graph green utilization, yellow memory. Disks show usage
per filesystem plus read/write throughput.

History is kept only while fleettop is running. For long-term history, use
something with a database, like Prometheus + Grafana.

## What it reads

Each sample pipes [`fleettop/probe.sh`](fleettop/probe.sh) to `bash -s` on every
host (one persistent SSH connection per host, so it's cheap) and parses its
`key=value` output. Read the script to see exactly what runs.

| | Linux | macOS |
|---|---|---|
| CPU, load | `/proc/stat`, `/proc/loadavg` | `top`, `sysctl` |
| RAM | `/proc/meminfo` (MemAvailable) | `vm_stat` (active + wired + compressed) |
| Disks | `df`, `/proc/diskstats` | `df` (usage only) |
| NVIDIA GPU | `nvidia-smi` | — |
| AMD GPU | sysfs (`gpu_busy_percent`, VRAM; APUs add GTT) | — |

Not supported: Apple GPUs (they need `sudo powermetrics`) and Intel GPUs.

## Development

```bash
git clone https://github.com/natemacfadden/fleettop && cd fleettop
python3 -m fleettop            # run from the checkout
python3 -m unittest discover -s tests -t .
```
