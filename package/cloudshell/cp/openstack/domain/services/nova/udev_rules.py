
udev_rules_str = \
'''#!/usr/bin/env python

import sys
import os

NETDEV_RULES_FILE = "/etc/udev/rules.d/70-attach-interface-qs-cloudshell.rules"

if sys.platform.lower().find("linux") < 0:
    print "Non Linux OS. Doing Nothing..."
    sys.exit(0)


def generate_udev_rules_str():
    if not os.path.exists("/sbin/ifconfig"):
        print "Ifconfig does not exist. Doing nothing..."
        sys.exit(0)

    if not os.path.exists("/sbin/dhclient"):
        print "dhclient does not exist or not in standard path. Doing Noting."
        sys.exit(0)

    etc_net_file_str = '\\n'.join(['KERNEL=="eth0", GOTO="no_eth0_config"', 'SUBSYSTEM=="net", ACTION=="add", KERNEL=="eth*", RUN+="/sbin/ifconfig %k up", RUN+="/sbin/dhclient -v %k -lf /var/run/dhclient--%.lease -pf /var/run/dhclient--%k.pid"', '', 'LABEL="no_eth0_config"', ''])

    print etc_net_file_str
    with open(NETDEV_RULES_FILE, "w") as f:
        f.write(etc_net_file_str)

    result = os.system("udevadm control --reload")

    print result

generate_udev_rules_str()
'''