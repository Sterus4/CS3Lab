from src.isa import Instruction


class ControlUnit:
    output: list[chr] = []

    def __init__(self, source_input: list[int], start: int):
        self.source_input = source_input
        self.start = start

    def simulate(self):
        pass
