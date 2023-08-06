from pybrary.command import Command


class Run(Command):
    '''run shell cmd on target
    '''
    line = True

    def run(self):
        target = self.get('target')
        line = self.get('_line_')
        target(line)
