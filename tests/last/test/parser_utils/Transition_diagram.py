from enum import Enum
import json


class StateType(Enum):
    MID = "MID"
    START = "Start"
    ACC = "Acc"


class State:
    def __init__(self, n, mainG, state_type=StateType.MID):
        self.main_grammar = mainG
        self.stateType = state_type
        self.number = n
        self.states = {}

    def add_state(self, n, index, t, accepting, NT):
        if index >= len(t):
            return
        if index == len(t) - 1:
            self.states[t[index]] = accepting
            accepting.number = n
            return
        temp = State(n + 1, NT)
        self.states[t[index]] = temp
        temp.add_state(temp.number, index + 1, t, accepting, NT)

    def __str__(self):
        return str(self.number)


class Diagram:
    def __init__(self):
        self.state_number = 0
        self.grammar = json.load(open("./parser_utils/grammar.json"))
        self.first = json.load(open("./parser_utils/files/first.json"))
        self.follow = json.load(open("./parser_utils/files/follow.json"))
        self.predict = json.load(open("./parser_utils/files/predict.json"))
        self.non_terminals = list(self.grammar.keys())
        self.terminals = set(self.flatten(list(self.grammar.values()))) - set(self.non_terminals)
        self.diagrams = {}
        for NT in self.non_terminals:
            self.diagrams[NT] = self.create_diagram_each(self.grammar[NT], NT)

    def create_diagram_each(self, productions, NT):
        starting = State(self.state_number, NT, StateType.START)
        accepting = State(self.state_number, NT, StateType.ACC)
        for product in productions:
            starting.add_state(self.state_number, 0, product, accepting, NT)
            self.state_number = accepting.number
        self.state_number = accepting.number + 1
        accepting.number = self.state_number
        self.state_number = self.state_number + 1
        return starting

    def flatten(self, x):
        if isinstance(x, list):
            return [a for i in x for a in self.flatten(i)]
        else:
            return [x]
