import os
import json
from types import SimpleNamespace

with open('config.json') as config_file:
    config = json.load(config_file, object_hook = lambda d: SimpleNamespace(**d))

efi = config.partitions.efi.partition
root = config.partitions.root.partition

hostname = config.hostname
language = config.language
keymap = config.keymap
timezone = config.timezone

users = config.users

packages = [
    'base',
    'base-devel',
    'linux',
    'linux-firmware',
    'grub',
    'efibootmgr'
] + config.packages
services = config.services

commands = [
    'cat mirrorlist > /etc/pacman.d/mirrorlist',
    'timedatectl set-ntp true',
    f'mkfs.fat -F32 {efi}',
    f'mkfs.ext4 {root}',
    f'mount {root} /mnt',
    'mkdir /mnt/efi',
    f'mount {efi} /mnt/efi',
    f'pacstrap /mnt {" ".join(packages)}',
    'genfstab -U /mnt >> /mnt/etc/fstab',
    f'arch-chroot /mnt ln -sf /usr/share/zoneinfo/{timezone} /etc/localtime',
    'arch-chroot /mnt hwclock --systohc',
    f'arch-chroot /mnt bash -c "echo {language}.UTF-8 UTF-8 >> /etc/locale.gen"',
    'arch-chroot /mnt locale-gen',
    f'arch-chroot /mnt bash -c "echo LANG={language}.UTF-8 > /etc/locale.conf"',
    f'arch-chroot /mnt bash -c "echo KEYMAP={keymap} > /etc/vconsole.conf"',
    f'arch-chroot /mnt bash -c "echo {hostname} > /etc/hostname"',
    'arch-chroot /mnt passwd',
    'arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=Arch',
    'arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg',
    f'arch-chroot /mnt systemctl enable {" ".join(services)}',
    'arch-chroot /mnt bash -c "echo %wheel ALL=\(ALL\) ALL >> /etc/sudoers"'
]

for user in users:
    commands.append(f'arch-chroot /mnt useradd -m -G wheel {user}')
    commands.append(f'arch-chroot /mnt passwd {user}')

for command in commands:
    os.system(command)