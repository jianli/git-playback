**Git playback** is a `git` command to play back or step through, commit by commit, the history of any git-controlled file. Its name was inspired by [mmozuras/git-playback](https://github.com/mmozuras/git-playback).

## Installation
```sh
pip install gitpython
cd ~
git clone git@github.com:jianlius/git-playback.git
git config --global alias.playback '!~/git-playback/playback.py ${GIT_PREFIX:-.}'
```

## Usage
To inspect a file `~/repo/path/to/file.py` from the repository `~/repo/`
```sh
cd ~/repo/
git playback path/to/file.py
```
and then press the following keys to navigate:
* `r`ewind
* `p`lay
* `b`ack one commit
* `f`orward one commit
* `Ctrl` + `n`ext line
* `Ctrl` + `p`revious line
* `q`uit

### Tips
* Git playback works better with files that have been edited relatively frequently in your commit history.
* Try to get the entire file on your screen by either increasing the size of your terminal window or reducing your font size.
