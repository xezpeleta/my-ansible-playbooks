#! /bin/sh

#
# python-simplejson must be installed in systems
# with Python 2.4
# below is a command that can help you installing it automatically...
#

ansible -i hosts all -u root -m raw -a"apt-get install -y python-simplejson"
