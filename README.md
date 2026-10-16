# fleettop

nvtop for all your machines at once. CPU, RAM, disk and GPU graphs over SSH;
nothing to install on the machines you watch.

```
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
```

## Install

```bash
pip install git+https://github.com/natemacfadden/fleettop
```

## Use

```bash
fleettop gpu01 me@gpu02      # watch these machines
fleettop -f hosts.txt        # or list them in a file, one per line
fleettop                     # reads ~/.config/fleettop/hosts, else just this machine
```

You need SSH keys set up so `ssh gpu01` logs in without a password.

Keys: `v` bars/graphs, `l` line style, `+`/`-` time window, `s` save screen, `q` quit.
