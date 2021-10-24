#!/bin/sh
#
# Called from udev
#
# Attempt to mount any added block devices and umount any removed devices

# By default we boot from a block device the BSP uses the first partition to
# store the files used by U-Boot, aka. the bootfs. The second partition of the
# same block device then contains the rootfs.
# Read the PARTUUID of the rootfs from /proc/cmdline, check if that device
# exists and then assume that the first partition on that device is the one
# with the bootpartion on it.
# Symlink that partition to /dev/boot-part, that then gets mounted to /boot,
# compare with /etc/fstab.

# expects 'root=PARTUUID=fe6beb3d-02' in /proc/cmdline

BASEUUID=$(sed -r 's/^.*\broot=PARTUUID=([0-9a-f]+)-02.*$/\1/' /proc/cmdline)
if [ -b /dev/disk/by-partuuid/${BASEUUID}-02 ]; then
	BOOTPART=$(readlink -f /dev/disk/by-partuuid/${BASEUUID}-01)
	if [ x$DEVNAME = x$BOOTPART ]; then
		logger "$0 creating symlink"
		ln -sf $BOOTPART /dev/boot-part
	fi
fi

MOUNT="/bin/mount"
PMOUNT="/usr/bin/pmount"
UMOUNT="/bin/umount"
for line in `grep -v ^# /etc/udev/mount.blacklist`
do
	if [ ` expr match "$DEVNAME" "$line" ` -gt 0 ];
	then
		logger "udev/mount.sh" "[$DEVNAME] is blacklisted, ignoring"
		exit 0
	fi
done

automount() {	
#	name="`basename "$DEVNAME"`"
	name="flashdrive"
        mkdosfs -F 32 -I "$DEVNAME"
	! test -d "/media/$name" && mkdir -p "/media/$name"
	# Silent util-linux's version of mounting auto
	if [ "x`readlink $MOUNT`" = "x/bin/mount.util-linux" ] ;
	then
		MOUNT="$MOUNT -o silent"
	fi
	
	# If filesystem type is vfat, change the ownership group to 'disk', and
	# grant it with  w/r/x permissions.
	case $ID_FS_TYPE in
	vfat|fat)
		MOUNT="$MOUNT -o umask=007,gid=`awk -F':' '/^disk/{print $3}' /etc/group`"
		;;
	# TODO
	*)
		;;
	esac

	if ! $MOUNT -t auto $DEVNAME "/media/$name"
	then
		#logger "mount.sh/automount" "$MOUNT -t auto $DEVNAME \"/media/$name\" failed!"
		rm_dir "/media/$name"
	else
		logger "mount.sh/automount" "Auto-mount of [/media/$name] successful"
		touch "/tmp/.automount-$name"
	fi
        jq --arg a "Active" '.device.STORAGEFLAG = $a' /etc/gateway/config/gateway.conf > "tmpt" && mv "tmpt" /etc/gateway/config/gateway.conf
        chmod 777 /etc/gateway/config/gateway.conf
}
	
rm_dir() {
	# We do not want to rm -r populated directories
	if test "`find "$1" | wc -l | tr -d " "`" -lt 2 -a -d "$1"
	then
		! test -z "$1" && rm -r "$1"
	else
		logger "mount.sh/automount" "Not removing non-empty directory [$1]"
	fi
	#jq --arg a "Inactive" '.device.STORAGEFLAG = $a' /etc/gateway/config.conf > "tmpt" && mv "tmpt" /etc/gateway/config.conf
}

# No ID_FS_TYPE for cdrom device, yet it should be mounted
name="`basename "$DEVNAME"`"
[ -e /sys/block/$name/device/media ] && media_type=`cat /sys/block/$name/device/media`

if [ "$ACTION" = "add" ] && [ -n "$DEVNAME" ] && [ -n "$ID_FS_TYPE" -o "$media_type" = "cdrom" ]; then
	if [ -x "$PMOUNT" ]; then
		$PMOUNT $DEVNAME 2> /dev/null
	elif [ -x $MOUNT ]; then
    		$MOUNT $DEVNAME 2> /dev/null
	fi
	
	# If the device isn't mounted at this point, it isn't
	# configured in fstab (note the root filesystem can show up as
	# /dev/root in /proc/mounts, so check the device number too)
	if expr $MAJOR "*" 256 + $MINOR != `stat -c %d /`; then
		grep -q "^$DEVNAME " /proc/mounts || automount
	fi
fi


if [ "$ACTION" = "remove" ] || [ "$ACTION" = "change" ] && [ -x "$UMOUNT" ] && [ -n "$DEVNAME" ]; then
	for mnt in `cat /proc/mounts | grep "$DEVNAME" | cut -f 2 -d " " `
	do
		$UMOUNT $mnt
	done
	
	# Remove empty directories from auto-mounter
	name="`basename "$DEVNAME"`"
	#test -e "/tmp/.automount-$name" && rm_dir "/media/$name"
        jq --arg a "Inactive" '.device.STORAGEFLAG = $a' /etc/gateway/config/gateway.conf > "tmpt" && mv "tmpt" /etc/gateway/config/gateway.conf
        chmod 777 /etc/gateway/config/gateway.conf
        
fi
