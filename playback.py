#!/usr/bin/env python
import curses
import difflib
import git
import os
import sys
import time


def commit(position):
    return 'HEAD~%d' % position


def get_text(repo, position, file_dir):
    try:
        return repo.git.show('%s:%s' % (commit(position), file_dir)). \
            replace('\r', '').split('\n')
    except git.exc.GitCommandError:
        return []


def get_message(repo, position, file_dir):
    author = repo.git.show(commit(position), format='%ae'). \
        replace('\r', '').split('\n')[0]
    message = repo.git.show(commit(position), oneline=True). \
        replace('\r', '').split('\n')[0]
    return ' '.join((commit(position), author, message))


def display_line(window, row, line, color, col_width=82):
    """
    Display all lines in fixed_width columns.
    """
    max_y, max_x = window.getmaxyx()
    display_column, display_row = divmod(row, max_y - 1)
    if display_column * col_width + col_width > max_x - 1:
        # Don't display line if it doesn't completely fit on the
        # screen.
        return False
    window.addstr(display_row, display_column * col_width,
                  line[:col_width],
                  color,
                  )


def display_prompt(window, message):
    max_y, max_x = window.getmaxyx()
    window.addstr(max_y - 1, 0,
                  message[:max_x - 1],
                  curses.A_REVERSE)


def function(window):
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)

    # Because this script is run through git alias, os.getcwd() will
    # actually return the top level of the git repo instead of the
    # true cwd. Therefore, the alias command needs to pass in
    # $GIT_PREFIX in order to get the true cwd
    top_level = os.getcwd()
    file_dir = os.path.join(
        sys.argv[1],  # $GIT_PREFIX passed in by git alias
        sys.argv[2],  # relative path
        )

    repo = git.Repo(top_level, odbt=git.GitCmdObjectDB)

    position = 0
    playing = False
    rewinding = False

    while 1:
        window.clear()

        old_text = get_text(repo, position + 1, file_dir)
        text = get_text(repo, position, file_dir)
        diff = list(difflib.ndiff(old_text, text))

        # `row` is the line number and `line` is the line text.
        row = 0
        for line in diff:
            code = line[:2]
            if code == '? ':
                continue
            elif code == '+ ':
                color = curses.color_pair(2)
            elif code == '- ':
                color = curses.color_pair(1)
            else:
                color = curses.color_pair(0)
            display_line(window, row, line, color)
            row += 1
        display_prompt(window, get_message(repo, position, file_dir))

        window.refresh()
        if (playing or rewinding) and old_text != text:
            time.sleep(1)

        if rewinding:
            c = curses.KEY_LEFT
        elif playing:
            c = curses.KEY_RIGHT
        else:
            c = window.getch()

        if c == ord('r'):
            rewinding = True
        elif c == ord('p'):
            playing = True
        elif c in (curses.KEY_LEFT, ord('b')):
            if get_text(repo, position + 1, file_dir):
                position += 1
            else:
                rewinding = False
        elif c in (curses.KEY_RIGHT, ord('f')):
            if get_text(repo, position - 1, file_dir):
                position -= 1
            else:
                playing = False
        elif c == ord('q'):
            break

curses.wrapper(function)
