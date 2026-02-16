from setuptools import setup, find_packages


setup(
    name='git-playback-ng',
    version='0.0.1.dev0',
    url='https://github.com/laur89/git-playback-ng',
    description='A git command to play back file history.',
    packages=find_packages('.'),
    entry_points={
        'console_scripts': (
            'git-playback = playback:playback',
        ),
    },
    install_requires=[
        'GitPython',
    ],
)
