my-ansible-playbooks
====================

[Ansible](http://www.ansible.com) is an open-source software platform for configuring and managing computers.

Here you have some useful receipes:
  * [VirtualBox remote installation](https://github.com/xezpeleta/my-ansible-playbooks/tree/master/install-virtualbox)
  * More1
  * More2

Examples
---------

Simple ping:
```
ansible -i hosts all -m ping
```

Advanced ping:
```
ansible --private-key=my_id_rsa -u root -i hosts all -m ping
```

Simple command:
```
ansible -i hosts all -a “/bin/echo kaixo”
```

Playbook:
```
ansible-playbook -i playbook.yml --private-key=my_id_rsa
```
