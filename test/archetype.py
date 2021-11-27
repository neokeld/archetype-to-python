from datetime import datetime
from duration_operations import parse_timedelta, duration_convert

class Archetype:
    def __init__():
        self.states = []
        self.currentState = ''

    def from_(self, state_from, state_to):
        if self.currentState == state_from:
            self.currentState = state_to
        
    def state(self, state: str):
        if state in self.states:
            return state
    
    def transfer(self, value):
        print(f"transferred {value}")
        
    def now(self):
        return datetime.now().date()
    
    def called_by(self, user):
        print(f"called by {user}")
    
    def strptime(self, date_string, format):
        return datetime.strptime(date_string, format)
    
    def parse_timedelta(self, duration_string):
        return parse_timedelta(duration_string)
        
    def duration_convert(self, maybe_duration):
        return duration_convert(maybe_duration)
        
def header(func):
    def wrapper(self, *args, **kwargs):
        transferred = 100
        return func(self, *args, **kwargs, transferred=transferred)
    return wrapper
