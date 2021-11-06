cat mirrorlist > /etc/pacman.d/mirrorlist
timedatectl set-ntp true
mkfs.fat -F32 /dev/sda1
mkfs.ext4 /dev/sda2
mount /dev/sda2 /mnt
mkdir /mnt/efi
mount /dev/sda1 /mnt/efi
pacstrap /mnt base linux linux-firmware dhcp
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt << 'EOF'
ln -sf /usr/share/zoneinfo/Brazil/East /etc/localtime
hwclock --systohc
echo "pt_BR.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "KEYMAP=br-abnt2" > /etc/vconsole.conf
echo "arch" > "/etc/hostname"
passwd
pacman -S grub efibootmgr
grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
EOF