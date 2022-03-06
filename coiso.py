import os
import json
from types import SimpleNamespace
from subprocess import check_output

with open('config.json') as config_file:
    config = json.load(config_file, object_hook = lambda d: SimpleNamespace(**d))

hostname = config.hostname
language = config.language
keymap = config.keymap
timezone = config.timezone
users = config.users
services = config.services

commands = [
    f'ln -sf /usr/share/zoneinfo/{timezone} /etc/localtime',
    'hwclock --systohc',
    f'echo {language}.UTF-8 UTF-8 >> /etc/locale.gen',
    'locale-gen',
    f'echo LANG={language}.UTF-8 > /etc/locale.conf',
    f'echo KEYMAP={keymap} > /etc/vconsole.conf',
    f'echo {hostname} > /etc/hostname',
    'passwd',
    'grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=Arch',
    'bash -c "echo GRUB_DISABLE_OS_PROBER=false >> /etc/default/grub"',
    'grub-mkconfig -o /boot/grub/grub.cfg',
    'pacman -S git base-devel',
    'useradd -m -G wheel yay-tmp',
    'cd /home/yay-tmp',
    'git clone https://aur.archlinux.org/yay-bin.git',
    'cd yay-bin',
    'su yay-tmp makepkg -si',
    f'su yay -S {" ".join(config.packages)}',
    'userdel -r yay-tmp',
    f'systemctl enable {" ".join(services)}',
]

for user in users:
    commands.append(f'useradd -m -G wheel -s /bin/{user.shell} {user.login}')
    commands.append(f'passwd {user.login}')

#commands += config.postinstall

for command in commands:
    if command != None:
        os.system(command)