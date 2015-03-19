import networkx

import idaapi
from .code import lines


class CodeBlock(idaapi.BasicBlock):
    @property
    def lines(self):
        return lines(self.startEA, self.endEA)

    @property
    def next(self):
        return self.succs()

    @property
    def prev(self):
        return self.preds()

    def set_color(self, color=None):
        for line in self.lines:
            line.color = color

    @property
    def color(self):
        return next(self.lines).color

    @color.setter
    def color(self, color):
        self.set_color(color)


class FlowChart(idaapi.FlowChart):
    def _getitem(self, index):
        return CodeBlock(index, self._q[index], self)


def flowchart(ea):
    func = idaapi.get_func(ea)
    flowchart_ = FlowChart(func)
    return flowchart_


def codeblock(ea):
    flowchart_ = flowchart(ea)
    for code_block in flowchart_:
        if code_block.startEA <= ea < code_block.endEA:
            return code_block


def get_block_start(ea):
    """Get the start address of an IDA Graph block."""
    return codeblock(ea).startEA


def get_nx_graph(ea):
    """Convert an IDA flowchart to a NetworkX graph."""
    nx_graph = networkx.DiGraph()
    func = idaapi.get_func(ea)
    flowchart = FlowChart(func)
    for block in flowchart:
        for pred in block.preds():
            nx_graph.add_edge(pred.startEA, block.startEA)
        for succ in block.succs():
            nx_graph.add_edge(block.startEA, succ.startEA)

    return nx_graph