"""Includes TimelineNode to create timelines of cash flows for visualization and PV calculation purposes"""
class TimelineNode(object):
    def __init__(self, cash, time_period):
        self.cash = cash
        self.time_period = time_period


class Timeline(object):
    def __init__(self, discount_rate, compound_rate=1, nodes=None):
        self.compound_rate = compound_rate
        self.discount_rate = discount_rate
        self.pv = None

        if nodes is None:
            self.nodes = []
        elif isinstance(nodes, list) and all([isinstance(x, TimelineNode) for x in nodes]):
            self.nodes = sorted(nodes, key=lambda n: n.time_period)
            self.update_pv()
        else:
            raise TypeError("nodes has to be either None or a list of TimelineNodes")

    def __repr__(self):
        """Print out a set of lines with notches for each payment"""
        node_graphic = "---|---"
        return_string = "discount rate: {}\n".format(round(self.discount_rate, 2))
        return_string += "PV: {}\n".format(self.pv)
        return_string += node_graphic*len(self.nodes) + "\n"
        for node in self.nodes:
            # Assume that time period <=99
            return_string += str(node.time_period).center(7, " ")
        return_string += "\n"
        for node in self.nodes:
            return_string += "C:{cash}".format(cash=node.cash).center(7," ")
        return return_string

    def __getitem__(self, item):
        pass

    def add_node(self, node):
        self.nodes.append(node)
        self.nodes = sorted(self.nodes, key=lambda n: n.time_period)
        self.update_pv()

    def update_pv(self):
        self.pv = 0
        for node in self.nodes:
            self.pv += self.pv_node(node)

    def pv_node(self, node):
        return round(node.cash / (1+self.discount_rate) ** node.time_period, 2)