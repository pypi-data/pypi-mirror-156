# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='litexplore',
    version='0.0.1',
    description='A small example package',
    long_description="# litexplore\n\n> `litexplore` is still in an early beta state. It works and it's usable, but\n> there may be signficant changes happening.\n\nThe current options to explore remote SQLite databases require running a service\non the remote and make it listen on some port. Another option is SSH'ing to the\nremote instance and use the SQLite CLI to explore the database. **Litexplore** is a\nPython web app that lets you explore remote SQLite databases over SSH\nconnections without having to copy the full DB or manually use the CLI.\n\nIt works by sending commands over an SSH connection. The connection is\nmultiplexed and it's reused to send commands. This reduces the overhead of\nopenning a new SSH connection to send each command.\n\n## Requirements\n\n- python 3.7 or higher\n- pydantic\n- fastapi\n- uvicorn\n- Jinja2\n- python-multipart\n\n## Installation\n\n1. Create a virtual env\n\n```sh\npython3 -m venv .venv\n```\n\n2. Activate the venv and install the dependencies\n\n```sh\nsource .venv/bin/activate\npython3 -m pip install litexplore\n```\n\n3. Run the program\n\n```sh\nlitexplore\n```\n\n4. Open your browser at `http://127.0.0.1:8000`\n\n_Note_: even though the server uses `0.0.0.0` as the default host, open the browser at `127.0.0.1`. Otherwise, cookies won't work and they're used to store the user config.\n\nRun `litexplore --help` to see other available options.\n\n### Using `pipx`\n\n1. Install `litexplore`\n\n```sh\npipx install litexplore\n```\n\n2. Run it:\n\n```sh\nlitexplore\n```\n\n## Usage\n\nThe main page is a form with 3 inputs.\n\n- The first input us the SSH host name as defined in your `~/.ssh`config`\n- The second input is the path to an SQLite database in the remote host\n- The third (optional) input is a path to an SQLite CLI. Some pre-installed sqlite3 CLIs have not been compiled\n  with support for the `-json` flag, which `litexplore` uses.\n\n## How it works\n\n## Roadmap\n\nSee [roadmap issues](https://github.com/litements/litexplore/labels/roadmap)\n\n## Alternatives\n",
    author_email='Ricardo Ander-Egg <rsubacc@gmail.com>',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'fastapi',
        'jinja2',
        'pydantic',
        'python-multipart',
        'uvicorn[standard]',
    ],
    entry_points={
        'console_scripts': [
            'litexplore = litexplore:__main__',
        ],
    },
    packages=[
        'litexplore',
    ],
)
