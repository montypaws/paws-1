#!/usr/bin/env python3

from docopt import docopt

opts = """
Python Asyncronous Web Server Daemon Control

Usage:
    pawsctl start <app>
    pawsctl stop <app>
    pawsctl restart <app>
    pawsctl status <app>

Options:
    -h --help       Show this screen

"""


if __name__ == "__main__":
    args = docopt(opts)
    print(args)
