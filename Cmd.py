import subprocess

class Cmd:
    def __init__(self, wd):
        self.wd = wd

    def check_output(self, cmd):
        return subprocess.check_output(cmd, shell=True, cwd=self.wd)

    def call(self, cmd):
        return subprocess.call(cmd, shell=True, cwd=self.wd)

    def e(self, fname):
        self.call('gvim --servername vim --remote-silent ' + fname)
