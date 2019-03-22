"""
# File with info about BIOMEK
"""

class Machine:

    """
    Parameters
    ----------
    id
        Machine id number
    name
        string name
    min_vol
    res_vol
    dead_vol
    """

    def __init__(self, name, min_vol, res_vol, dead_vol):
        self.name = name
        self.min_vol = min_vol
        self.res_vol = res_vol
        self.dead_vol = dead_vol

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
