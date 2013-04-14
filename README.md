**Git playback** is a `git` command to play back or step through, commit by commit, the history of any git-controlled file. Its name was inspired by [mmozuras/git-playback](https://github.com/mmozuras/git-playback).

## Installation
```sh
pip install git-playback
```

## Usage
To inspect a file `~/repo/path/to/file.py` from the repository `~/repo/`
```sh
cd ~/repo/
git playback path/to/file.py
```

![git playback README.md](https://raw.github.com/jianli/git-playback/master/animation.gif "git playback README.md")

and then press the following keys to navigate:
* `r`ewind
* `p`lay
* `b`ack one commit
* `f`orward one commit
* `Ctrl` + `n`ext line
* `Ctrl` + `p`revious line
* `q`uit
