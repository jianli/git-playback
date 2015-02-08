from setuptools import find_packages
from setuptools import setup


setup(
    name='git-playback',
    version='0.2',
    url='https://github.com/jianli/git-playback',
    description='A git command to play back file history.',
    packages=find_packages('.'),
    entry_points={
        'console_scripts': (
            'git-playback = playback:playback',
        ),
    },
    install_requires=[
        'gitpython>=0.3.2.RC1',
    ],
)
