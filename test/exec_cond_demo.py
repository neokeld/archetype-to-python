from archetype import Archetype, header
class exec_cond_demo(Archetype):
    def __init__(self, value):
        self.value = value
    @header
    def setvalue(self, v, transferred):
        self.called_by('admin')
        if transferred > self.value and self.now() < self.strptime('2022-01-01', '%Y-%m-%d').date():
            self.value = v
