import re

REGEX_NEWFILE = r'diff --git a/(?P<name>[^\s]+) b/(?P=name)'
REGEX_MINUS_OR_PLUS = r'(?:---|\+\+\+) [ab]/'
REGEX_INDEX = r'index \w+\.\.\w+'
REGEX_HUNK = r'@@ -\d+,\d+ \+\d+,\d+'
REGEX_MODE = r'(?:old|new) mode \d+'

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

        elif re.search(REGEX_MODE, line):
            continue

        elif re.search(REGEX_MINUS_OR_PLUS + current_file, line) or \
         re.search(REGEX_INDEX, line):
            current_header.append(line)
            continue

        elif re.search(REGEX_HUNK, line):
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

