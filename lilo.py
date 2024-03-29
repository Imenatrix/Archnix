import os
import json
from types import SimpleNamespace

with open('config.json') as config_file:
    config = json.load(config_file, object_hook=lambda d: SimpleNamespace(**d))

packages = config.packages
services = config.services

commands = [
    'sudo pacman -S git base-devel',
    'git clone https://aur.archlinux.org/yay-bin.git',
    'cd yay-bin && makepkg -si',
    'rm -rf yay-bin',
    f'yay -S {" ".join(packages)}',
    f'sudo systemctl enable {" ".join(services)}'
]

commands += config.postinstall

for command in commands:
    if command is not None:
        os.system(command)
