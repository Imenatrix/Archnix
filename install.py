import os
import json
from types import SimpleNamespace
from subprocess import check_output

with open('config.json') as config_file:
    config = json.load(config_file, object_hook = lambda d: SimpleNamespace(**d))

efi = config.partitions.efi.partition
efi_format = config.partitions.efi.format
root = config.partitions.root.partition
root_format = config.partitions.root.format

hostname = config.hostname
language = config.language
keymap = config.keymap
timezone = config.timezone

users = config.users

vendor = list(
    filter(
        lambda x: x.startswith('Vendor ID:'),
        check_output(['lscpu'])
            .decode()
            .split('\n')
    )
)[0].split(' ')[-1]

microcode = 'intel-ucode' if vendor == 'GenuineIntel' else 'amd-ucode' if vendor == 'AuthenticAMD' else ''


packages = [
    'base',
    'sudo',
    'linux',
    'linux-firmware',
    'grub',
    'efibootmgr',
    'os-prober',
    'python',
    microcode
]
services = config.services

commands = [
    'cat mirrorlist > /etc/pacman.d/mirrorlist',
    'timedatectl set-ntp true',
    f'mkfs.fat -F32 {efi}' if efi_format else None,
    f'mkfs.ext4 {root}' if root_format else None,
    f'mount {root} /mnt',
    'mkdir /mnt/efi',
    f'mount {efi} /mnt/efi',
    f'pacstrap /mnt {" ".join(packages)}',
    'genfstab -U /mnt >> /mnt/etc/fstab',
    'cp coiso.py /mnt',
    'cp config.json /mnt',
    'arch-chroot /mnt python coiso.py',
    'rm /mnt/coiso.py',
    'rm /mnt/config.json',
]

commands += config.postinstall

for command in commands:
    if command != None:
        os.system(command)