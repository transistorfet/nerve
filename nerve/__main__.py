#!/usr/bin/python3
# -*- coding: utf-8 -*-


import nerve
import argparse

def main():
    parser = argparse.ArgumentParser(prog='nerve', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Nerve Control Server')
    parser.add_argument('-c', '--configdir', action='store', help='Use specified directory for configuration', default='~/.nerve/')
    parser.add_argument('-f', '--log-to-file', action='store_true', help='Save log output to a file in the configuration directory')
    args = parser.parse_args()

    nerve.files.add_config_path(args.configdir)
    nerve.logs.log_to_file(args.log_to_file)
    nerve.logs.init_colour()

    nerve.loop()

main()

