import os
import subprocess
import tempfile
import unittest
from unittest import mock

from fleettop import cli

LINUX_SAMPLE = """\
io=128 0
cpu=22
load=9.75
ncpu=24
mem=6200 30800
disk=/, 327122660, 465081868
disk=/mnt/ssd, 724571152, 933351788
gpu=RTX 5090, 89, 28122, 32607, 71, 464.58
gpu=AMD Navi 22, sleep, 0, 12272, -, -
"""


class Parse(unittest.TestCase):
    def test_linux(self):
        d = cli.parse(LINUX_SAMPLE)
        self.assertEqual(d["cpu"], 22)
        self.assertEqual(d["mem"], (6200, 30800))
        self.assertEqual(d["io"], (128, 0))
        self.assertEqual([m for m, _, _ in d["disks"]], ["/", "/mnt/ssd"])
        g0, g1 = d["gpus"]
        self.assertEqual((g0["name"], g0["util"], g0["pw"]), ("RTX 5090", 89, 464.58))
        self.assertTrue(g1["asleep"])
        self.assertIsNone(g1["temp"])

    def test_mac_has_no_io_or_gpu(self):
        d = cli.parse("cpu=12\nload=2.1\nncpu=10\nmem=15000 32768\ndisk=/, 1, 2\n")
        self.assertIsNone(d["io"])
        self.assertEqual(d["gpus"], [])

    def test_garbage_is_offline(self):
        self.assertIsNone(cli.parse(""))
        self.assertIsNone(cli.parse("ssh: connect to host x port 22: refused\n"))

    def test_series_are_percent(self):
        left, right = cli.series(cli.parse(LINUX_SAMPLE))
        self.assertAlmostEqual(left["ram"], 100 * 6200 / 30800)
        self.assertEqual(right["g1"], 0)   # a sleeping GPU graphs as idle


class Hosts(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, name, text):
        path = os.path.join(self.dir.name, name)
        with open(path, "w") as f:
            f.write(text)
        return path

    def test_file_format(self):
        f = self.write("hosts", "# fleet\ngpu01\n\n  me@gpu02   # the big one\n")
        self.assertEqual(cli.read_hosts(f), ["gpu01", "me@gpu02"])

    def test_args_and_files_combine_without_duplicates(self):
        f = self.write("hosts", "b\nc\n")
        hs, source = cli.resolve_hosts(["a", "b"], [f], config="/nonexistent")
        self.assertEqual((hs, source), (["a", "b", "c"], "arguments"))

    def test_config_used_when_nothing_given(self):
        cfg = self.write("cfg", "x\ny\n")
        self.assertEqual(cli.resolve_hosts([], [], config=cfg), (["x", "y"], cfg))

    def test_falls_back_to_this_machine(self):
        hs, source = cli.resolve_hosts([], [], config="/nonexistent")
        self.assertEqual((hs, source), ([cli.LOCAL], None))
        self.assertTrue(cli.is_local(hs[0]))

    def test_localhost_is_local(self):
        self.assertTrue(cli.is_local("localhost"))
        self.assertFalse(cli.is_local("me@some-other-box"))


class Graph(unittest.TestCase):
    """Draw into a recorder instead of a terminal."""

    def draw(self, style, cpu, ram, h=10, w=20):
        out = []
        ui = cli.UI()
        ui.style = style
        with mock.patch.object(cli, "put", lambda scr, y, x, t, a=0: out.append((y, x, t, a))), \
                mock.patch.object(cli.curses, "color_pair", lambda n: n):
            cli.graph(None, 0, 0, h, w, cli.CPU_LEGEND, [({"cpu": cpu, "ram": ram}, {})] * 50,
                      0, ui, 1)
        # plot cells only: inside the border, not the frame or its labels
        return [(y, t, a & ~cli.curses.A_BOLD) for y, x, t, a in out
                if 0 < y < h - 1 and 0 < x < w - 1]

    def test_braille_cell_takes_one_series(self):
        # 0% and 10% share the bottom braille row; its dots must all be RAM's,
        # not CPU's dots painted in RAM's color
        cells = self.draw("dots", cpu=0, ram=10)
        self.assertEqual({a for _, _, a in cells}, {cli.SERIES_COLOR["ram"]})
        self.assertEqual({t for _, t, _ in cells}, {"⠉"})

    def test_lines_separate_rows(self):
        cells = self.draw("lines", cpu=0, ram=50)
        rows = {a: {y for y, _, a2 in cells if a2 == a} for _, _, a in cells}
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[cli.SERIES_COLOR["cpu"]].isdisjoint(rows[cli.SERIES_COLOR["ram"]]))


class Probe(unittest.TestCase):
    def test_probe_runs_here(self):
        r = subprocess.run(["bash", "-s"], input=cli.PROBE, capture_output=True, text=True,
                           timeout=30)
        self.assertIsNotNone(cli.parse(r.stdout), r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
