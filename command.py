class Command:
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self, *pargs, **kargs):
        pass


class TempOnCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.move_temp_rod(kargs['rod'], kargs['target'])


class TempOffCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.stop_temp_rod()


class PowerOnCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.move_power_rod(kargs['rod'], kargs['target'])


class PowerOffCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.stop_power_rod()


class DiluteOnCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.dilute(kargs['vol'], kargs['rate'])


class DiluteOffCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.stop_dilute()


class BoronOnCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.boron(kargs['vol'], kargs['rate'])


class BoronOffCommand(Command):
    def __init__(self, receiver):
        Command.__init__(self, receiver)

    def execute(self, *pargs, **kargs):
        self.receiver.stop_boron()
