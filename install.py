import os
import json
from types import SimpleNamespace

with open('config.json') as config_file:
    config = json.load(config_file, object_hook = lambda d: SimpleNamespace(**d))

efi = config.partitions.efi.partition
root = config.partitions.root.partition

hostname = config.hostname
language = config.language

commands = [
    'cat mirrorlist > /etc/pacman.d/mirrorlist',
    'timedatectl set-ntp true',
    f'mkfs.fat -F32 {efi}',
    f'mkfs.ext4 {root}',
    f'mount {root} /mnt',
    'mkdir /mnt/efi',
    f'mount {efi} /mnt/efi',
    'pacstrap /mnt base linux linux-firmware dhcpcd',
    'genfstab -U /mnt >> /mnt/etc/fstab',
    'arch-chroot /mnt ln -sf /usr/share/zoneinfo/Brazil/East /etc/localtime',
    'arch-chroot /mnt hwclock --systohc',
    f'arch-chroot /mnt bash -c "echo {language}.UTF-8 UTF-8 >> /etc/locale.gen"',
    'arch-chroot /mnt locale-gen',
    f'arch-chroot /mnt bash -c "echo LANG={language}.UTF-8 > /etc/locale.conf"',
    'arch-chroot /mnt bash -c "echo KEYMAP=br-abnt2 > /etc/vconsole.conf"',
    f'arch-chroot /mnt bash -c "echo {hostname} > /etc/hostname"',
    'arch-chroot /mnt passwd',
    'arch-chroot /mnt pacman -S grub efibootmgr',
    'arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=Arch',
    'arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg',
]

for command in commands:
    os.system(command)