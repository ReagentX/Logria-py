from setuptools import setup, find_packages
from logria import APP_NAME, VERSION

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name=APP_NAME,
    version=VERSION,
    description='A powerful CLI tool that puts log analytics at your fingertips.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author='Christopher Sardegna',
    author_email='github@reagentx.net',
    url='https://github.com/ReagentX/Logria',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'logria = logria.__main__:main'
        ]
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console :: Curses',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Logging',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
