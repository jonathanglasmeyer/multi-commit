import os, datetime
from Cmd import CmdLog
from cached_property import cached_property
from DotDict import DotDict
from parse import parse

from display import *

NEXT=999
PREV=9999

repo_dir = os.getcwd()
cmd = CmdLog(repo_dir)

class Commit:
    def __init__(self, logline):
        self.hash_, self.date_iso, *message = logline.split()
        self.message = ' '.join(message)
        self.ui_id = 0
        # self.logline = logline

    @cached_property
    def _first_diff_line_index(self):
        try:
            return next(i for i,line in enumerate(self.full_text) if line.startswith('diff --git'))
        except:
            return 4

    @cached_property
    def full_text(self):
        return cmd.check_output('git show --format="format:%h%n%an%n%at%n%s%n%b" {}'.format(self.hash_)).split('\n')

    @cached_property
    def full_text_string(self):
        return '\n'.join(self.full_text)

    @cached_property
    def message(self):
        return self.full_text[3]

    @cached_property
    def description(self):
        return '\n'.join(self.full_text[4:self._first_diff_line_index][:-1])

    @cached_property
    def diffs(self):
        diff_lines = self.full_text[self._first_diff_line_index:-1]
        return parse(diff_string_lines=diff_lines)

    @cached_property
    def hunks(self):
        diffs = map(DotDict, self.diffs)
        all_hunks = []
        for f in diffs:
            for hunk in f.hunks:
                all_hunks.append({'filename': f.filename, 'hunk': hunk})
        return all_hunks

    def display_summary(self, show_ui_id=True):
        if show_ui_id:
            print_color('{}) '.format(self.ui_id), fg=COLOR_GREY, end='')
        print_color('{}{}: '.format('  ' if not show_ui_id else '', self.author), fg=COLOR_GREEN, end='')
        print_indented_paragraph(self.message + '\n', indent=3)

        # '[{}] {}\n'.format(self.ui_id, self.message)

    def display_hunk(self, nr):
        if nr == None: return
        if nr == -2: nr = len(self.hunks)-1
        jump_to_next_commit = False
        jump_to_prev_commit = False
        if nr > len(self.hunks)-1: jump_to_next_commit = True
        if nr < 0: jump_to_prev_commit = True
        nr = max(0, nr)
        nr = min(nr, len(self.hunks) - 1)

        hunk = self.hunks[nr]
        print_caption1('hunk {}/{} ({})'.format(nr+1, len(self.hunks), hunk['filename']))

        print_hunk(hunk['hunk'])
        print_line()
        if jump_to_prev_commit: return PREV
        return nr if not jump_to_next_commit else NEXT


    @cached_property
    def author(self):
        # TODO: print full name if first name is ambiguous (via some cache)
        author_long = self.full_text[1]
        nicknames = {'Niko Uphoff': 'Niko', 'Jonathan Werner': 'Jona'}
        return nicknames[author_long] if author_long in nicknames else author_long.split()[0]


    @cached_property
    def date(self):
        return datetime.datetime.fromtimestamp(int(self.date_iso))
