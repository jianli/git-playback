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
    message = repo.git.show(commit(position), oneline=True). \
        replace('\r', '').split('\n')[0]
    return ' '.join((commit(position), message))


def get_added_lines(old_text, text):
    diffs = difflib.ndiff(old_text, text)
    line = 0
    for diff in diffs:
        code = diff[:2]
        if code == '+ ':
            yield line
        if code in ('  ', '+ '):
            line += 1


def function(window):
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)

    repo = git.Repo(os.getcwd(), odbt=git.GitCmdObjectDB)
    file_dir = sys.argv[1]

    position = 0
    playing = False
    rewinding = False

    while 1:
        window.clear()
        text = get_text(repo, position, file_dir)
        old_text = get_text(repo, position + 1, file_dir)
        added_lines = list(get_added_lines(old_text, text))

        for line in range(window.getmaxyx()[0]):
            color = curses.color_pair(0)
            if line in added_lines:
                color = curses.color_pair(2)
            window.addstr(line, 0,
                          text[line] if line < len(text) else '',
                          color,
                          )
        window.addstr(window.getmaxyx()[0] - 1, 0,
                      get_message(repo, position, file_dir),
                      curses.A_REVERSE)
        window.refresh()

        if rewinding:
            c = curses.KEY_LEFT
            time.sleep(0.1)
        elif playing:
            c = curses.KEY_RIGHT
            time.sleep(0.1)
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
                curses.flash()
        elif c in (curses.KEY_RIGHT, ord('f')):
            if get_text(repo, position - 1, file_dir):
                position -= 1
            else:
                playing = False
                curses.flash()
        elif c == ord('q'):
            break

curses.wrapper(function)
