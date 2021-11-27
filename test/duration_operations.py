from decimal import Decimal
from datetime import timedelta

def parse_timedelta(duration_string): #example: '3w8d4h34m18s'
    total_seconds = Decimal('0')
    prev_num = []
    for character in duration_string:
        if character.isalpha():
            if prev_num:
                num = Decimal(''.join(prev_num))
                if character == 'w':
                    total_seconds += num * 60 * 60 * 24 * 7
                elif character == 'd':
                    total_seconds += num * 60 * 60 * 24
                elif character == 'h':
                    total_seconds += num * 60 * 60
                elif character == 'm':
                    total_seconds += num * 60
                elif character == 's':
                    total_seconds += num
                prev_num = []
        elif character.isnumeric() or character == '.':
            prev_num.append(character)
    return timedelta(seconds=float(total_seconds))

def duration_convert(maybe_duration):
    if isinstance(maybe_duration, timedelta):
        return maybe_duration.days
    return maybe_duration
