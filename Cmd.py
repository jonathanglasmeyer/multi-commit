import subprocess
import os

LOG_STATEMENT_REGEX='console\.[log|info]'

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
        return self.check_output('git ls-files --others --exclude-standard')

    def add_intent_to_add(self):
        self.call('git add --intent-to-add *')

    def show_console_logs(self):
        self.call('ag "{}"'.format(LOG_STATEMENT_REGEX))
        print()

    def find_console_logs(self):
        try:
            return self.check_output('ag "{}"'.format(LOG_STATEMENT_REGEX))

        except subprocess.CalledProcessError:
            return False

    def remove_console_logs(self):
        self.call('ag -l "{0}" | xargs sed -i "/{0}/d"'.format(LOG_STATEMENT_REGEX))

