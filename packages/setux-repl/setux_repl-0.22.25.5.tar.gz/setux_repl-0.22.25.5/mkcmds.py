from setux.cmd.cmd import get_commands


with open('docs/commands.md', 'w') as out:
    def w(txt=''):
        out.write(f'{txt}  \n')

    w(f'# Commands')
    for name, cmd in get_commands().items():
        w(f'## {name}')
        for n, line in enumerate(cmd.__doc__.split('\n')):
            if n==0:
                w(f'**{line}**')
            else:
                w(f'{line}')
