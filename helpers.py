from itertools import *
def find_prev_ui_id(commit_group, current_commit_ui_id):
    _, commits = commit_group
    try:
        prev_commit = list(takewhile(lambda commit: commit.ui_id != current_commit_ui_id, commits))[-1]
        return prev_commit.ui_id
    except:
        return False
        # commit = next(filter(lambda commit: commit.ui_id == current_commit_ui_id, commits), None)
        # return commit.

def find_next_ui_id(commit_group, current_commit_ui_id):
    _, commits = commit_group
    try:
        next_commit = list(dropwhile(lambda commit: commit.ui_id != current_commit_ui_id, commits))[1]
        return next_commit.ui_id
    except:
        return False
        # commit = next(filter(lambda commit: commit.ui_id == current_commit_ui_id, commits), None)
        # return commit
