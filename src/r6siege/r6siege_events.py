import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from events import Events


class R6siegeEvents(Events):
    def __init__(self):
        Events.__init__(self, game="r6siege")
