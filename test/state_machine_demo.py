from archetype import Archetype, header
class state_machine_demo(Archetype):
    def __init__(self, holder):
        self.holder = holder
        self.states = ['Created', 'Initialized', 'Terminated']
        self.currentState = "Created"
    @header
    def initialize(self, transferred):
        if transferred > 10:
            self.from_(self.state('Created'), self.state('Initialized'))
    def terminate(self):
        self.from_(self.state('Initialized'), self.state('Terminated'))
        self.transfer(1 + 1)
