#!/usr/bin/env python
import curses
import difflib
import git
import os
import sys
import time


def get_text(repo, sha1, file_path):
    try:
        return repo.git.show('%s:%s' % (sha1, file_path)).replace(
            '\r', '').split('\n')
    except git.exc.GitCommandError:
        return []  # Assuming that the file was deleted here.


def get_message(repo, sha1, file_path):
    short_sha1 = sha1[:7]
    author = '(%s)' % repo.git.log(sha1, n=1, format='%ae').replace(
        '\r', '').split('\n')[0]
    message = repo.git.log(sha1, n=1, oneline=True).replace(
        '\r', '').split('\n')[0][8:]
    return ' '.join((short_sha1, file_path, author, message))


def display_line(window, row, line, color, col_width=82):
    """
    Display line in fixed-width columns.
    """
    max_y, max_x = window.getmaxyx()
    display_column, display_row = divmod(row, max_y - 1)
    if display_column > 0 and (display_column + 1) * col_width > max_x:
        # Don't display additional columns if they don't completely fit.
        return False
    window.addstr(display_row, display_column * col_width,
                  line[:col_width], color)


def display_prompt(window, message):
    max_y, max_x = window.getmaxyx()
    window.addstr(max_y - 1, 0, message[:max_x - 1], curses.A_REVERSE)


def function(window):
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)

    repo = git.Repo(os.getcwd())
    top_level = repo.git.rev_parse(show_toplevel=True)
    file_path = os.path.relpath(os.path.join(os.getcwd(), sys.argv[1]),
                                top_level)

    # `commits` is a list of `(sha1, file_path)` tuples where `file_path` is
    # variable because we are following files renames. Adding the '!' into the
    # format is a hack to help us delimit sha1s in the git output.
    commits = [
        log.split('\t') for log in
        repo.git.log(file_path, name_only=True, follow=True, format='%H!')
        .replace('!\n\n', '\t').split('\n')
    ]
    commits.reverse()  # Since `git log --reverse --follow` doesn't work

    position = len(commits) - 1
    commit = 0
    first_row = 0
    next_refresh = 0
    key = 0
    playing = False
    rewinding = False
    diff = []

    while 1:
        # get keyboard input
        window.nodelay(1)  # don't wait for input
        key = window.getch()
        if (playing or rewinding) and key == curses.ERR:
            next_refresh = time.time() + 0.3
            if playing:
                key = curses.KEY_RIGHT
            elif rewinding:
                key = curses.KEY_LEFT
        else:
            playing = rewinding = False

        # Change state parameters based on keyboard input
        first_row_delta = 0
        if key == ord('r'):
            rewinding = True
        elif key == ord('p'):
            playing = True
        elif key in (curses.KEY_LEFT, ord('b')):
            if 0 <= position - 1 < len(commits):
                position -= 1
            else:
                rewinding = False
        elif key in (curses.KEY_RIGHT, ord('f')):
            if 0 <= position + 1 < len(commits):
                position += 1
            else:
                playing = False
        elif key in (curses.KEY_DOWN, ord('n') - 96):  # ctrl + n
            if first_row < len(diff) - 1:
                first_row_delta = 1
        elif key in (curses.KEY_UP, ord('p') - 96):  # ctrl + p
            if first_row > 0:
                first_row_delta = -1
        elif key == ord('q'):
            return

        if commit == commits[position] and not first_row_delta:
            time.sleep(.01)
            continue

        commit = commits[position]
        first_row += first_row_delta
        window.clear()

        old_text = get_text(repo, *commits[position - 1]) \
            if position - 1 >= 0 else []
        text = get_text(repo, *commit)
        diff = [line for line in list(difflib.ndiff(old_text, text))
                if line[:2] != '? ']

        # `row` is the line number and `line` is the line text.
        for row, line in enumerate(diff[min(first_row, len(diff) - 1):]):
            code = line[:2]
            if code == '+ ':
                color = curses.color_pair(2)
            elif code == '- ':
                color = curses.color_pair(1)
            else:
                color = curses.color_pair(0)
            display_line(window, row, line, color)
        display_prompt(window, get_message(repo, *commit))
        while time.time() < next_refresh:
            pass
        window.refresh()


def playback():
    try:
        curses.wrapper(function)
    except git.exc.GitCommandError as err:
        print >> sys.stderr, '%s: %s' % (type(err).__name__, err)
        return 1


if __name__ == '__main__':
    sys.exit(playback())
