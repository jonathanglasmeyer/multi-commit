from colors import print_color, rgb, gray
from DotDict import DotDict
import subprocess, re, os, textwrap
from subprocess import Popen, PIPE, STDOUT
from tempfile import SpooledTemporaryFile as tempfile
from pprint import pprint
REGEX_NEWFILE='diff --git a/(?P<name>[^\s]+) b/(?P=name)'
_, TERMINAL_COLUMNS = map(int,os.popen('stty size', 'r').read().split())


COLOR_GREEN = 13
COLOR_RED = 8
COLOR_GREY = gray(8)
COLOR_GREY_DARK = gray(6)
COLOR_CAPTION1_BG=gray(5)
COLOR_CAPTION2_FG=gray(9)
INDENT=3

commits = []

def pc(s, color):
    print_color(s, fg=color)

def print_line(color=None):
    pc('⎯' * TERMINAL_COLUMNS, color or gray(6))

def print_line_bottom(color=None):
    pc('⎯' * TERMINAL_COLUMNS, color or gray(6))

def print_line_dark():
    pc('.' * TERMINAL_COLUMNS, COLOR_GREY_DARK)

def print_full_length_text_block(text, bg):
    print_color(('{0: <'+str(TERMINAL_COLUMNS)+'}').format(text), bg=bg)

def print_caption1(caption):
    print_full_length_text_block(caption, COLOR_CAPTION1_BG)
    print()

def print_caption2(caption):
    print_color(caption, fg=COLOR_CAPTION2_FG)
    print()

def print_commit_caption(n, commit):
    print()
    # print_line_bottom(2)
    hunks_count = len(commit['hunks'])
    print_color('[{}] '.format(n+1), fg=2, end='')
    print_color(commit['msg'], end='')
    print_color(' ({} hunk{})'.format(
        hunks_count, 's' if hunks_count>1 else ''), fg=COLOR_GREY_DARK)
    print_line(2)
    print()

def print_commit(n, commit):
    hunks_count = len(commit['hunks'])
    print_color('[{}] '.format(n+1), fg=2, end='')
    print_color(commit['msg'], end='')
    print_color(' ({} hunk{})'.format(
        hunks_count, 's' if hunks_count>1 else ''), fg=COLOR_GREY)


def print_commits():
    if len(commits) == 0: return

    print_caption1('commit messages')
    for n, commit in enumerate(commits):
        print_commit(n, commit)
    print()

def print_indented_paragraph(paragraph, color):
    lines = textwrap.wrap(paragraph, TERMINAL_COLUMNS-INDENT-5)
    if len(lines) == 0: 
        print()
        return
    for n, line in enumerate(lines):
        pc((0 if n==0 else INDENT)*' ' + line, color)

def print_hunk(hunk, fname=None):
    sym = '|  '

    for line in hunk:
        if line.startswith('@@'):
            line = line.strip()[3:-2]
            print_caption2('{}{}'.format(fname + ': ' if fname else '', line))
        else:

            if line.startswith('+'):
                print_color('+'+(INDENT-1)*' ', fg=COLOR_GREEN, end='')
                print_indented_paragraph(line[1:], COLOR_GREEN)
            elif line.startswith('-'):
                print_color('-  ', fg=COLOR_RED, end='')
                print_indented_paragraph(line[1:], COLOR_RED)
            else: 
                # print_color('.' + ' '*(INDENT-1), end='', fg=COLOR_GREY)
                print_color(' '*INDENT, end='', fg=COLOR_GREY)
                print_indented_paragraph(line[1:], COLOR_CAPTION2_FG)
    print('')


def commit_item(fname, hunk_nr):
    return {'filename': fname, 'hunk_nr': hunk_nr}

def file_dict(fname, hunks, hunk, header):
    if len(hunk) > 0 : hunks.append(hunk)
    return {
        'filename': fname,
        'hunks': hunks,
        'header': header
    }

def parse(diff_string):
    files = []
    current_file = ''
    current_hunks = []
    current_header = []
    current_hunk = []
    for line in diff_string.split('\n'):
        new_file_line = re.search(REGEX_NEWFILE, line)
        if new_file_line: 
            fname = new_file_line.group('name')
            if current_file: 
                files.append(file_dict(
                  current_file, current_hunks, current_hunk, current_header))
            current_file = fname
            current_hunks = []
            current_hunk = []
            current_header = [line]

        elif re.search(r'(?:---|\+\+\+) [ab]/' + current_file, line) or \
         re.search(r'index \w+\.\.\w+ \w+', line):
            current_header.append(line)
            continue
            
        elif re.search(r'@@ -\d+,\d+ \+\d+,\d+ ', line): 
            if len(current_hunk) > 0: 
                current_hunks.append(current_hunk)
                current_hunk = []

            current_hunk.append(line)
            continue

        else:
            current_hunk.append(line)

    files.append(file_dict(
      current_file, current_hunks, current_hunk, current_header))

    return files

def prompt(text=None):
    print_line_bottom()
    return input('{}> '.format(text + '\n' if text else ''))

def interact(diffs):
    diffs = map(DotDict, diffs)
    for f in diffs:
        for hunk_nr, hunk in enumerate(f.hunks):
            os.system('clear')
            print_commits()
            print_caption1(f.filename)
            print_hunk(hunk)
            item = commit_item(f.filename, hunk_nr)
            while 1:
                i = prompt()
                if len(i)==0: break

                if i.isdigit() and len(i) == 1:
                    number = int(i)
                    if number <= len(commits):
                        commits[number-1]['hunks'].append(item)
                        break
                    else:
                        continue
                else:
                    if not i: continue
                    commits.append({'msg': i})
                    commits[-1]['hunks'] = [item]
                    break

def show_summary(diffs):
    os.system('clear')
    print_caption1('Commit Summary')
    for n, commit in enumerate(commits):
        print_commit_caption(n, commit)
        for hunk_obj in commit['hunks']:
            fname = hunk_obj['filename']
            hunk_nr = hunk_obj['hunk_nr']
            hunk = get_hunks(diffs, fname)[hunk_nr]
            print_hunk(hunk, fname)

def format_patch(header, hunk):
    return '\n'.join(header) + '\n' + '\n'.join(hunk)

def create_patches(diffs, commit):
    patches = []
    for hunk_obj in commit['hunks']:
        fname = hunk_obj['filename']
        hunk_nr = hunk_obj['hunk_nr']
        hunk = get_hunks(diffs, fname)[hunk_nr]
        header = get_header(diffs, fname)
        patch = format_patch(header, hunk)
        patches.append(patch)

    return patches

def get_header(diffs, fname):
    return [f for f in diffs if f['filename'] == fname][0]['header']

def get_hunks(diffs, fname):
    return [f for f in diffs if f['filename'] == fname][0]['hunks']

def main():
    repo_dir='/home/jwerner/dev/multi-commit'

    diff = subprocess.check_output('git diff -U1', shell=True, cwd=repo_dir)
    diff_string = diff.decode('utf-8')

    diffs = parse(diff_string)
    interact(diffs)
    show_summary(diffs)

    if prompt('Commit everything? (y/_)') != 'y': return
    for commit in commits:
        patches = create_patches(diffs, commit)
        print("Committing '{}'".format(commit['msg']))
        for patch in patches:
            f = tempfile()
            f.write(bytes(patch, 'utf-8') + b'\n'); f.seek(0)
            stdout = Popen('git apply -v --cached', shell=True, stdout=PIPE, stdin=f, stderr=STDOUT, cwd=repo_dir).stdout.read()
            print(stdout.decode('utf-8'))

        stdout = subprocess.check_output("git commit -m '{}'".format(commit['msg']), shell=True, cwd=repo_dir)
        print(stdout.decode('utf-8'))



main()
