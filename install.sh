cat mirrorlist > /etc/pacman.d/mirrorlist
timedatectl set-ntp true
mkfs.fat -F32 /dev/sda1
mkfs.ext4 /dev/sda2
mount /dev/sda2 /mnt
mkdir /mnt/efi
mount /dev/sda1 /mnt/efi
pacstrap /mnt base linux linux-firmware dhcp
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt ln -sf /usr/share/zoneinfo/Brazil/East /etc/localtime
arch-chroot /mnt hwclock --systohc
arch-chroot /mnt echo "pt_BR.UTF-8 UTF-8" >> /etc/locale.gen
arch-chroot /mnt locale-gen
arch-chroot /mnt echo "LANG=en_US.UTF-8" > /etc/locale.conf
arch-chroot /mnt echo "KEYMAP=br-abnt2" > /etc/vconsole.conf
arch-chroot /mnt echo "arch" > "/etc/hostname"
arch-chroot /mnt passwd
arch-chroot /mnt pacman -S grub efibootmgr
arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB
arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg