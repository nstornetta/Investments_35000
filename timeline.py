"""Includes TimelineNode and PerpetuityNode to create timelines of cash flows
for visualization and PV calculation purposes"""


class TimelineNode(object):
    def __init__(self, cash, time_period):
        self.cash = cash
        self.time_period = time_period
        self.timeline_graphic = "---|---"

    def __repr__(self):
        return "{}\nCash: {} Time Period: {}".format(self.__class__.__name__,
                                                     self.cash,
                                                     self.time_period)


class PerpetuityNode(TimelineNode):
    def __init__(self, cash, time_period, growth_rate=0):
        super().__init__(cash, time_period)
        self.growth_rate = growth_rate  # only relevant if growth rate > 0
        self.timeline_graphic = "-- Perpetuity --"


class Timeline(object):
    def __init__(self, discount_rate, compound_rate=1, nodes=None):
        self.compound_rate = compound_rate
        self.discount_rate = discount_rate
        self.pv = None
        self.terminal_value = None

        if nodes is None:
            self.nodes = []
        elif isinstance(nodes, list) and all([isinstance(x, TimelineNode) for x in nodes]):
            self.nodes = sorted(nodes, key=lambda n: n.time_period)
            self.update_pv()
        else:
            raise TypeError("nodes has to be either None or a list of TimelineNodes")

    def __getitem__(self, key):
        return self.nodes.__getitem__(key)

    def __repr__(self):
        """Print out a set of lines with notches for each payment"""
        return_string = "discount rate: {}\n".format(round(self.discount_rate, 2))
        return_string += "PV: {}\n".format(round(self.pv, 2))

        # Add in the basic timeline graphics
        for node in self.nodes:
            return_string += node.timeline_graphic
        return_string += "\n"

        # Add indication of time period for each node
        for node in self.nodes:
            return_string += str(node.time_period).center(len(node.timeline_graphic))
        return_string += "\n"

        # Add cash for each node
        for node in self.nodes:
            return_string += "C:{cash}".format(cash=node.cash).center(len(node.timeline_graphic))

        return return_string

    def add_node(self, node):
        if not isinstance(node, TimelineNode):
            raise TypeError("node has to be a timelineNode object")
        self.nodes.append(node)
        self.nodes = sorted(self.nodes, key=lambda n: n.time_period)
        self.update_pv()

    def update_pv(self):
        self.pv = 0
        if self.terminal_value is not None:
            self.terminal_value = 0
        for node in self.nodes:
            if isinstance(node, PerpetuityNode):
                self.pv += self.pv_perpetuity(node)
            else:
                self.pv += self.pv_node(node)

    def pv_node(self, node):
        return round(node.cash / (1 + self.discount_rate) ** node.time_period, 2)

    def pv_perpetuity(self, perpetuity_node):
        # first, calculate pv in terms of time period before perpetuity per std. equation
        pv = perpetuity_node.cash / (self.discount_rate - perpetuity_node.growth_rate)
        # second, discount pv back to being in terms of time period 0
        return pv / (1 + self.discount_rate) ** (perpetuity_node.time_period-1)
