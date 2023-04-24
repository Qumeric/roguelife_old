from datetime import datetime, timedelta

from blinker import Signal

from events import TickEvent

_ticks = 0
tick_signal = Signal("tick")


def tick():
    global _ticks
    _ticks += 1
    print("sending tick", _ticks)
    tick_signal.send(event=TickEvent(current_datetime()))


def current_datetime() -> datetime:
    return datetime(1, 1, 1) + timedelta(minutes=_ticks)
