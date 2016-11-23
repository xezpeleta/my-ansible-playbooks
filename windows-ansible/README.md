# Managing Windows machines with Ansible

## About

Starting in version 1.7, [Ansible](https://www.ansible.com/) contains support
for managing Windows machines. In this guide I'll describe the steps you need
to follow to set it up.

## Windows machines preparation

First of all, you need to prepare Windows machines to enable PowerShell
remoting.

### Enable PowerShell script execution

In order for Ansible to manage your windows machines, you will have to enable
and configure PowerShell remoting.

To automate the setup of WinRM, you can run [this PowerShell script](https://github.com/ansible/ansible/raw/devel/examples/scripts/ConfigureRemotingForAnsible.ps1)
on the remote machine.

#### In your Windows machine

In Windows 10, by default, PowerShell can be used only in interactive mode;
no scripts can be run. That's why you have to allow script execution:

1. Download [the script](https://github.com/ansible/ansible/raw/devel/examples/scripts/ConfigureRemotingForAnsible.ps1)
2. Open command prompt (as Administrator)
3. Allow PS script executions: `powershell "Set-ExecutionPolicy -ExecutionPolicy Unrestricted"`
4. Run downloaded script: `powershell "C:\your-path\ConfigureRemoteForAnsible.ps1"`
5. Restore script execution policy: `powershell "Set-ExecutionPolicy -ExecutionPolicy Restricted"`

### Firewall policy

The script above will add a rule in your Windows firewall to allow WinRM
connections.


**_Note_**: *Kaspersky Endpoint Security 10 uses its own firewall. You need to
change the configuration there manually to allow WinRM incoming connections
(TCP/5986). For testing purposes, you can just disable Kaspersky firewall*

## Ansible control machine

Reminder: you must have a Linux Control Machine. There is no way to do that
from a Windows host.

### Instructions

Create the following directories/files structure:

```
windows/
├── group_vars/
│   └── windows.yml
└── hosts
```

#### hosts file

Add your Windows hosts to the inventory:

```yaml
# file: hosts
[windows]
192.168.1.10
192.168.1.11
```

Under the `group_vars` directory, add the following file named `windows.yml`:

```yaml
# file: group_vars/windows.yml

ansible_user: my_user
ansible_password: my_pass
ansible_port: 5986
ansible_connection: winrm
# The following is necessary for Python 2.7.9+ when using default WinRM self-signed certificates:
ansible_winrm_server_cert_validation: ignore
```

That's all. Now you can test it using the [win_ping module](http://docs.ansible.com/ansible/win_ping_module.html):

```sh
$ ansible windows -i hosts -m win_ping
192.168.1.10 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## Examples

Gather facts using [setup module](http://docs.ansible.com/ansible/setup_module.html):

```sh
$ ansible windows -i hosts -m setup
...
```

Installing Firefox with [Chocolatey](http://docs.ansible.com/ansible/win_chocolatey_module.html):

```sh
$ ansible-playbook windows -i hosts playbook-install-firefox.yml
```

```yaml
# file: playbook-install-firefox.yml
---
- name: test chocolatey with ansible
  hosts: all
  tasks:
    - name: Install Firefox
      win_chocolatey:
        name: firefox
        state: present
```

More examples? [Check available Windows modules](http://docs.ansible.com/ansible/list_of_windows_modules.html)
