import os
import json
from types import SimpleNamespace
from subprocess import check_output

with open('config.json') as config_file:
    config = json.load(config_file, object_hook = lambda d: SimpleNamespace(**d))

efi = config.partitions.efi.partition
root = config.partitions.root.partition

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
    microcode
]
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
    'arch-chroot /mnt bash -c "echo GRUB_DISABLE_OS_PROBER=false >> /etc/default/grub"',
    'arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg',
    'arch-chroot /mnt pacman -S git base-devel',
    'arch-chroot /mnt useradd -m -G wheel yay-tmp',
    'arch-chroot /mnt sed -i "s/^# %wheel ALL=(ALL) NOPASSWD: ALL/%wheel ALL=(ALL) NOPASSWD: ALL/" /etc/sudoers',
    'arch-chroot /mnt /usr/bin/runuser -u yay-tmp -- bash -c "cd ~ && git clone https://aur.archlinux.org/yay-bin.git"',
    'arch-chroot /mnt /usr/bin/runuser -u yay-tmp -- bash -c "cd ~/yay-bin && makepkg -si"',
    f'arch-chroot /mnt /usr/bin/runuser -u yay-tmp -- yay -S {" ".join(config.packages)}',
    'arch-chroot /mnt userdel -r yay-tmp',
    'arch-chroot /mnt sed -i "s/^%wheel ALL=(ALL) NOPASSWD: ALL/# %wheel ALL=(ALL) NOPASSWD: ALL/" /etc/sudoers',
    'arch-chroot /mnt sed -i "s/^# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/" /etc/sudoers',
    f'arch-chroot /mnt systemctl enable {" ".join(services)}',
]

for user in users:
    commands.append(f'arch-chroot /mnt useradd -m -G wheel -s /bin/{user.shell} {user.login}')
    commands.append(f'arch-chroot /mnt passwd {user.login}')

commands += config.postinstall

for command in commands:
    os.system(command)