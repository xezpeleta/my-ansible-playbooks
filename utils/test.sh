#! /bin/sh

#
# Ansible PING test
#

ansible -m ping -i hosts all -u root
