from restarting_automata import BaseAutomaton, types
from inspect import getmembers, isfunction

print([i[0] for i in getmembers(types, isfunction)])
