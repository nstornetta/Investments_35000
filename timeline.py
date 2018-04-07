"""Includes TimelineNode to create timelines of cash flows for visualization and PV calculation purposes"""


class TimelineNode(object):
    def __init__(self, cash, time_period):
        self.cash = cash
        self.time_period = time_period
        self.timeline_graphic = "---|---"


class PerpetuityNode(TimelineNode):
    def __init__(self, cash, time_period, growth_rate=0):
        self.cash = cash
        self.time_period = time_period  # indicates time period of first payment
        self.growth_rate = growth_rate  # only relevant if growth rate > 0
        self.timeline_graphic = "--- Perpetuity ---"


class Timeline(object):
    def __init__(self, discount_rate, compound_rate=1, nodes=None, perpetuity=None):
        self.compound_rate = compound_rate
        self.discount_rate = discount_rate
        self.pv = None

        # TODO: remove implicit assumption that perpetuity occur at the end of any timeline
        self.perpetuity = None  # initialize to None to avoid issue with update_pv logic TODO: make this cleaner

        if nodes is None:
            self.nodes = []
        elif isinstance(nodes, list) and all([isinstance(x, TimelineNode) for x in nodes]):
            self.nodes = sorted(nodes, key=lambda n: n.time_period)
            self.update_pv()
        else:
            raise TypeError("nodes has to be either None or a list of TimelineNodes")

        if perpetuity and isinstance(perpetuity, PerpetuityNode):
            self.perpetuity = perpetuity
            self.update_pv()
        elif perpetuity:
            raise TypeError("perpetuity has to be either None or a PerpetuityNode")

    def __getitem__(self, item):
        pass

    def __repr__(self):
        """Print out a set of lines with notches for each payment"""
        return_string = "discount rate: {}\n".format(round(self.discount_rate, 2))
        return_string += "PV: {}\n".format(round(self.pv, 2))

        node_graphic = "---|---"
        perpetuity_graphic = "--- Perpetuity ---"
        return_string += node_graphic*len(self.nodes)
        if self.perpetuity:
            return_string += perpetuity_graphic
        return_string += "\n"

        for node in self.nodes:
            # Assume that time period <=99
            return_string += str(node.time_period).center(len(node_graphic))
        if self.perpetuity:
            return_string += str(self.perpetuity.time_period).center(len(perpetuity_graphic))
        return_string += "\n"

        for node in self.nodes:
            return_string += "C:{cash}".format(cash=node.cash).center(len(node_graphic))
        if self.perpetuity:
            return_string += "C:{cash}".format(cash=self.perpetuity.cash).center(len(perpetuity_graphic))

        return return_string

    def add_node(self, node):
        self.nodes.append(node)
        self.nodes = sorted(self.nodes, key=lambda n: n.time_period)
        self.update_pv()

    def add_perpetuity(self, cash, time_period, growth_rate=0):
        self.perpetuity = PerpetuityNode(cash, time_period, growth_rate)
        self.update_pv()

    def update_pv(self):
        self.pv = 0
        for node in self.nodes:
            self.pv += self.pv_node(node)
        if self.perpetuity:
            self.pv += self.pv_perpetuity()

    def pv_node(self, node):
        return round(node.cash / (1+self.discount_rate) ** node.time_period, 2)

    def pv_perpetuity(self, perpetuity_node=None):
        if not perpetuity_node:
            perpetuity_node = self.perpetuity
        else:
            perpetuity_node = perpetuity_node
        # first, calculate pv in terms of time period before perpetuity per std. equation
        pv = perpetuity_node.cash / (self.discount_rate - perpetuity_node.growth_rate)
        # second, discount pv back to terms of time period 0
        pv = pv / (1 + self.discount_rate) ** (perpetuity_node.time_period-1)
        return pv
