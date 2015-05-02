import datetime
from display import *
def print_days(date):

    def days_delta(date):
        return (datetime.datetime.now() - datetime.datetime.combine(date, datetime.datetime.min.time())).days

    days = days_delta(date)
    def p(formattedDayDelta):
        print(formattedDayDelta, end='')
        print_color(' ({})'.format(date.strftime('%a, %d.%m')), fg=COLOR_GREY)

    if days == 0: p('today'); return
    if days == 1: p('yesterday'); return
    p('{} day{} ago'.format(days, 's' if days > 1 else ''))


def print_commit_diff(commit_group, ui_id, active_hunk_nr):
    _, commits = commit_group
    commit = next(filter(lambda commit: commit.ui_id == ui_id, commits), None)
    if not commit: return
    validated_nr = commit.display_hunk(active_hunk_nr)
    return validated_nr


def print_commit_group(commit_group, active_commit_ui_id, active_hunk_nr):

    def id_encode(i):
        diff = max(i-25, 0)
        return chr(97+(diff//25)) if i>25 else '' + chr(97+(i % 25))

    validated_hunk_nr = None
    date, commits = commit_group

    # print date caption
    print()
    print_days(date)
    print_line(COLOR_YELLOW)

    # print commit list for date
    for i, commit in enumerate(commits):
        commit.ui_id = id_encode(i)
        commit.display_summary()
        print()

        # optionally print commit description
        if commit.description:
            print_indented_paragraph(3*' '+commit.description, COLOR_GREY_BRIGHT, 3)
            print()

        # if there is an active commit: print detail view instead
        if commit.ui_id == active_commit_ui_id:
            for _ in range(25): print_color('.', fg=COLOR_YELLOW)
            os.system('clear')

            # header
            print()
            print_color('({}/{})'.format(i+1, len(commits)), end=' ', fg=COLOR_GREY_BRIGHT)
            print_days(date)
            print_line(COLOR_YELLOW)
            print()
            commit.display_summary(show_ui_id=False)
            print()
            if commit.description:
                print_indented_paragraph('  '+commit.description, COLOR_GREY_BRIGHT, 2)
                print()
            print_line(COLOR_YELLOW)
            validated_hunk_nr = print_commit_diff(commit_group, active_commit_ui_id, active_hunk_nr)
            return len(commits), validated_hunk_nr
    print()
    return len(commits), validated_hunk_nr
