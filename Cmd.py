import subprocess

class Cmd:
    def __init__(self, wd):
        self.wd = wd

    def check_output(self, cmd):
        return subprocess.check_output(
            cmd, shell=True, cwd=self.wd).decode('utf-8')

    def call(self, cmd):
        return subprocess.call(cmd, shell=True, cwd=self.wd)

    def e(self, fname):
        self.call('gvim --servername vim --remote-silent ' + fname)

    def untracked_files(self):
        self.check_output('git ls-files --others --exclude-standard')

