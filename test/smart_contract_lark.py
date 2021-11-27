from archetype import Archetype, header
class smart_contract_lark(Archetype):
    def __init__(self, holder):
        self.holder = holder
    def pay(self):
        self.transfer((1 + (7 / 100. * self.duration_convert(((self.now() - self.strptime('2021-01-01', '%Y-%m-%d').date()) + self.parse_timedelta('1w1d'))))))
