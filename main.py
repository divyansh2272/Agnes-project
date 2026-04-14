"""Main entrypoint for the Agnes Voice Assistant project.

Usage examples:
  python main.py run                # start voice assistant (interactive)
  python main.py demo               # run voice demo (listen + echo)
  python main.py devices            # list known simulated devices
  python main.py parse "text"      # show parsed command structure
  python main.py control "text"    # parse and apply a textual command

This script ties together modules in the `voice` package and provides
convenient CLI access for development and testing.
"""
from __future__ import annotations
import argparse
import sys


def import_voice_module(name: str):
    try:
        module = __import__(f"voice.{name}", fromlist=[name])
        return module
    except Exception:
        # Fallback to direct import when running from package-less layout
        return __import__(name)


def run_assistant():
    mod = import_voice_module('simple_assistant')
    # simple_assistant exposes main()
    if hasattr(mod, 'main'):
        mod.main()
    else:
        print('No assistant main() found in voice.simple_assistant')


def run_demo():
    mod = import_voice_module('voice_demo')
    if hasattr(mod, 'main'):
        mod.main()
    else:
        print('No demo main() found in voice.voice_demo')


def list_devices():
    try:
        sm = import_voice_module('smart_home')
        devices = sm.list_devices()
        for name, state in devices.items():
            print(f"{name}: {state}")
    except Exception as e:
        print('Could not list devices:', e)


def parse_text(text: str):
    cp = import_voice_module('command_parser')
    parsed = cp.parse_command(text)
    print('Parsed command:')
    for k, v in parsed.items():
        print(f"  {k}: {v}")


def control_text(text: str):
    cp = import_voice_module('command_parser')
    sm = import_voice_module('smart_home')
    parsed = cp.parse_command(text)
    print('Parsed:', parsed)
    result = sm.apply_command(parsed)
    print('Result:', result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Agnes Voice Assistant main runner')
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('run', help='Start interactive voice assistant')
    sub.add_parser('demo', help='Run voice demo (listen + echo)')
    sub.add_parser('devices', help='List simulated devices')

    pparse = sub.add_parser('parse', help='Parse a text command')
    pparse.add_argument('text', help='Text to parse', nargs='+')

    pcontrol = sub.add_parser('control', help='Parse and apply a text command')
    pcontrol.add_argument('text', help='Text to control', nargs='+')

    args = parser.parse_args(argv)
    if args.cmd == 'run':
        run_assistant()
    elif args.cmd == 'demo':
        run_demo()
    elif args.cmd == 'devices':
        list_devices()
    elif args.cmd == 'parse':
        parse_text(' '.join(args.text))
    elif args.cmd == 'control':
        control_text(' '.join(args.text))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
