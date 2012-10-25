#!/usr/bin/env python
import curses
import difflib
import git
import os
import sys
import time


def get_text(repo, commit, file_dir):
    return repo.git.show('%s:%s' % (commit, file_dir)).replace(
        '\r', '').split('\n')


def get_message(repo, commit, file_dir):
    short_commit = commit[:7]
    author = '(%s)' % repo.git.log(commit, n=1, format='%ae').replace(
        '\r', '').split('\n')[0]
    message = repo.git.log(commit, n=1, oneline=True).replace(
        '\r', '').split('\n')[0][8:]
    return ' '.join((short_commit, file_dir, author, message))


def display_line(window, row, line, color, col_width=82):
    """
    Display line in fixed-width columns.
    """
    max_y, max_x = window.getmaxyx()
    display_column, display_row = divmod(row, max_y - 1)
    if display_column * col_width + col_width > max_x - 1:
        # Don't display line if it doesn't completely fit on the screen.
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

    # Because this script is run through git alias, os.getcwd() will actually
    # return the top level of the git repo instead of the true cwd. Therefore,
    # the alias command needs to pass in $GIT_PREFIX to get the true cwd.
    top_level = os.getcwd()
    file_dir = os.path.join(
        sys.argv[1],  # $GIT_PREFIX passed in by git alias
        sys.argv[2],  # relative path
        )
    repo = git.Repo(top_level, odbt=git.GitCmdObjectDB)

    try:
        # Assume that file_dir is a path instead of a ref; it doesn't seem
        # possible to use ' -- ' in GitPython.
        commits = repo.git.log(file_dir, format="%H", reverse=True).split('\n')
    except git.exc.GitCommandError:
        return

    position = len(commits) - 1
    first_row = 0
    next_refresh = 0
    c = 0
    playing = False
    rewinding = False

    while 1:
        if c != curses.ERR:  # clear screen unless nothing changed
            window.clear()

        commit = commits[position]

        old_text = get_text(repo, commits[position - 1], file_dir) \
            if position - 1 >= 0 else []
        text = get_text(repo, commit, file_dir)
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
        display_prompt(window, get_message(repo, commit, file_dir))
        while time.time() < next_refresh:
            pass
        window.refresh()

        # get keyboard input
        window.nodelay(1)  # don't wait for input
        c = window.getch()
        if (playing or rewinding) and c == curses.ERR:
            next_refresh = time.time() + 0.3
            if playing:
                c = curses.KEY_RIGHT
            elif rewinding:
                c = curses.KEY_LEFT
        else:
            playing = rewinding = False

        # Change state parameters based on keyboard input
        if c == ord('r'):
            rewinding = True
        elif c == ord('p'):
            playing = True
        elif c in (curses.KEY_LEFT, ord('b')):
            if 0 <= position - 1 < len(commits):
                position -= 1
            else:
                rewinding = False
        elif c in (curses.KEY_RIGHT, ord('f')):
            if 0 <= position + 1 < len(commits):
                position += 1
            else:
                playing = False
        elif c in (curses.KEY_DOWN, ord('n') - 96):  # ctrl + n
            if first_row < len(diff) - 1:
                first_row += 1
        elif c in (curses.KEY_UP, ord('p') - 96):  # ctrl + p
            if first_row > 0:
                first_row -= 1
        elif c == ord('q'):
            return

curses.wrapper(function)
