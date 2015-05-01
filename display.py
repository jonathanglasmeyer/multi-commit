import os, textwrap
from colors import print_color, rgb, gray
_, TERMINAL_COLUMNS = map(int,os.popen('stty size', 'r').read().split())
COLOR_YELLOW = 2
COLOR_GREEN = 13
COLOR_RED = 8
COLOR_GREY = gray(8)
COLOR_GREY_DARK = gray(6)
COLOR_CAPTION1_BG=gray(5)
COLOR_CAPTION2_FG=gray(12)
COLOR_CONTEXT=gray(7)

INDENT=3

def pc(s, color):
    print_color(s, fg=color)

def print_line(color=None):
    pc('⎯' * TERMINAL_COLUMNS, color or COLOR_GREY_DARK)

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
    print_line(COLOR_YELLOW)
    hunks_count = len(commit['hunks'])
    print_color('[{}] '.format(n+1), fg=COLOR_YELLOW, end='')
    print_color(commit['msg'][0], end='')

    print_color(' ({} hunk{})'.format(
        hunks_count, 's' if hunks_count>1 else ''), fg=COLOR_GREY_DARK)

    if len(commit['msg']) == 2:
        print()
        for line in commit['msg'][1].split('\n'):
            print_indented_paragraph(' '*4 + line, COLOR_CAPTION2_FG, 4)

    print_line(COLOR_GREY_DARK)

    print()

def print_commit(n, commit):
    hunks_count = len(commit['hunks'])
    print_color('[{}] '.format(n+1), fg=2, end='')
    print_color(commit['msg'][0], end='')
    print_color(' ({} hunk{})'.format(
        hunks_count, 's' if hunks_count>1 else ''), fg=COLOR_GREY)

# overview above the commit message input prompt
def print_commits(commits):
    if len(commits) == 0: return

    for n, commit in enumerate(commits):
        print_commit(n, commit)
    print()

def print_indented_paragraph(paragraph, color, indent=INDENT):
    lines = textwrap.wrap(paragraph, TERMINAL_COLUMNS-indent-5)
    if len(lines) == 0:
        print()
        return
    for n, line in enumerate(lines):
        pc((0 if n==0 else indent)*' ' + line, color)

def print_hunk(hunk, fname=None):
    for line in hunk:
        if line.startswith('@@'):
            line = line.strip()[3:-2]
            print_caption2(' '*INDENT + '{}{}'.format(fname + ': ' if fname else '', line))
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
                print_indented_paragraph(line[1:], COLOR_CONTEXT)
    print('')

def prompt(text=None, hint=None):
    if text: print(text)
    if hint: print_color(hint, fg=COLOR_GREY)
    return input('\n> ')

def multiline_prompt(prompt_text=None):
    text = ""
    stopword = ""
    print(prompt_text)
    while True:
        line = input('> ')
        if line.strip() == stopword:
            break
        text += "%s\n" % line
    git_formatted_text = '\n'.join(
            ['\n'.join(textwrap.wrap(line, width=72)) for line in text.split('\n')])
    return git_formatted_text
