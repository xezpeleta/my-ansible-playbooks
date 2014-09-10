#! /usr/bin/python

import ansible.runner
import sys

def copyScript(i, surl, sdest):
	#i = ansible.inventory.Inventory(hosts)
	results = ansible.runner.Runner(
		inventory = i,
		pattern = '*', forks = 10,
		remote_user = 'root',
		module_name = 'get_url', module_args = 'url=' + surl + ' dest=' + sdest + ' force=yes validate_certs=no',
		#module_name = 'copy', module_args = 'src=' + script + ' dest=/tmp mode=0700',
		#module_name='command', module_args='/usr/bin/uptime',
	).run()
	return results

def execScript(i, script):
	#i = ansible.inventory.Inventory(hosts)
	results = ansible.runner.Runner(
		inventory = i,
		pattern = '*', forks = 10,
		remote_user = 'root',
		module_name = 'command', module_args = 'python ' + script,
		#module_name='command', module_args='/usr/bin/uptime',
	).run()
	return results

def purgeInventory(i, hosts):
		#i = ansible.inventory.Inventory(hosts)
		return i.restrict_to(hosts)

def getErrors(results):
	errors = ''
	failed = []
	down = []
	for (hostname, result) in results['contacted'].items():
		if 'failed' in result:
			failed.append(hostname)

	for (hostname, result) in results['dark'].items():
		down.append(hostname)

	if len(failed) > 0:
		errors += '\n*** ERROR ***'
		for (hostname,result) in  results['contacted'].items():
			if 'failed' in result:
				errors += "\n%s: %s" % (hostname, result['msg'])

	if len(down) > 0:
		errors += '\n*** DOWN ***'
		for (hostname,result) in results['dark'].items():
			errors += "\n%s: %s" % (hostname, result['msg'])
	return errors

if __name__ == '__main__':
	u = 'root'
	surl = 'https://github.com/xezpeleta/3ware-check/raw/master/3wcheck.py'
	spath = '/tmp/3wcheck.py'
	#h = ['srv-01.tknika.net', 'srv-03.tknika.net', 'srv-06.tknika.net', 'srv-11.tknika.net', 'srv-12.tknika.net', 'srv-20.tknika.net', 'srv-21.tknika.net']
	h = 'hosts'
	i = ansible.inventory.Inventory(h)


	results = copyScript(i, surl, spath)
	# Purge not contacted hosts
	restrict = []
	for (hostname, result) in results['contacted'].items():
		if not 'failed' in result:
			restrict.append(hostname)
	i.restrict_to(restrict)

	errors = getErrors(results)

	#Print inventory
	#hosts = i.list_hosts()
	#print 'Inventory: ' + str(sorted(hosts))

	results = execScript(i, spath)
	for (hostname, result) in results['contacted'].items():
		if not 'failed' in result:
			print "%s: %s" % (hostname, result['stdout'])
	errors += getErrors(results)

	#print cperrors
	#print execerrors
	print errors
