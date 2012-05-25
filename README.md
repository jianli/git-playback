Git playback is a command-line utility to play back, commit by commit, the history of any git-controlled file.

## Installation
```sh
pip install gitpython
cd ~
git clone git@github.com:jianlius/git-playback.git
```

## Usage
To inspect `~/repo/file.py` from the repository `~/repo/`
```sh
cd ~/repo/
~/git-playback/playback.py file.py
```
and then press the following keys to navigate:
* `b`ack one commit
* `f`orward one commit
* `r`ewind
* `p`lay
* `q`uit
