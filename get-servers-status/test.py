import ansible.runner

runner = ansible.runner.Runner(
    module_name = 'ping',
    module_args = '',
    pattern = 'test',
    forks=10
)
datastructure = runner.run()
