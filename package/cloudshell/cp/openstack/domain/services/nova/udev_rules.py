
udev_rules_sh_str = '''#!/bin/sh

PYTHON=
if [ -e '/usr/bin/python' ]; then
    PYTHON=/usr/bin/python
elif [ -e '/usr/bin/python3' ]; then
    PYTHON=/usr/bin/python3
fi

OS_TYPE=`$PYTHON -c 'import sys;print(sys.platform)'`

LOGGER_TAG="ADD_QS_TAG"

if [ $OS_TYPE != 'linux2' -a $OS_TYPE != 'linux' ]; then
    logger -i -s --tag ${LOGGER_TAG} "Platform $OS_TYPE is not supported for Udev rules."
    exit 1
fi

QS_UDEV_FILE='/etc/udev/rules.d/70-a-qs-connectivity.rules'

logger -i -s --tag ${LOGGER_TAG}  "Creating UDEV Entries in file $QS_UDEV_FILE"
cat <<TOEND > $QS_UDEV_FILE
# Udev Rules for Quali Systems Apply Connectivity

# KERNEL=="eth0", GOTO="no_eth0_config"

SUBSYSTEM=="net", ACTION=="add", KERNEL=="eth*", RUN+="/sbin/ifconfig %k up", RUN+="/sbin/dhclient -v %k -lf /var/run/dhclient-qs-%k.lease -pf /var/run/dhclient-qs-%k.pid"'
SUBSYSTEM=="net", ACTION=="add", KERNEL=="en*", RUN+="/sbin/ifconfig %k up", RUN+="/sbin/dhclient -v %k -lf /var/run/dhclient-qs-%k.lease -pf /var/run/dhclient-qs-%k.pid"'

# LABEL="no_eth0_config"

TOEND

# We are going to stop renaming of the devices - this messes things up. Everything will be eth0->ethN
logger -i -s --tag $LOGGER_TAG "Disabling device name change."
/bin/ln -s /dev/null /etc/udev/rules.d/80-net-name-slot.rules
/bin/ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules


logger -i -s --tag $LOGGER_TAG  "Calling udevadm control"
/sbin/udevadm control --reload && /sbin/udevadm trigger --subsystem-match=net

'''