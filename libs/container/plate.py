"""
# Library to create a class for different plates
"""


from ..misc import calc


class Plate:

    """
    Parameters
    ----------
    name
      The well's name, for instance "A1"

    rows
      The well's row (a number, starting from 0)

    cols
      The well's column (a number, starting from 0)

    num_wells
      The quantity of wells in the plate (96, 384, 1536)

    wells
      A matrix of wells according the number of cols and rows
      the function coordiantes_to_wellname Convert (0,0)->A1,
    """
    counter = 0

    def __init__(self, rows, cols, name):
        self.name = name
        self.num_rows = rows
        self.num_cols = cols
        self.num_wells = rows * cols
        self.wells = [[Well(calc.coordinates_to_wellname(coords=[j, i]), i, j)
                       for i in range(0, self.num_cols)] for j in range(0, self.num_rows)]
        self.id = Plate.counter
        Plate.counter += 1

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_empty_well_coord(self):
        for i in range(0, self.num_rows):
            for j in range(0, self.num_cols):
                if len(self.wells[i][j].samples) == 0:
                    return i, j
        return None

    def iterR(self, n):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                for k in range(0, n):
                    yield self.wells[i][j]

    def iterC(self, n):
        for j in range(self.num_cols):
            for i in range(self.num_rows):
                for k in range(0, n):
                    yield self.wells[i][j]

    def iterRC_by_spot(self, n):
        start = 0
        count = n
        while count <= self.num_cols:
            for i in range(self.num_rows):
                for j in range(start, count):
                    yield self.wells[i][j]
            if count < self.num_cols:
                start+=n
                count+=n
            else:
                return


class Well:

    """
    Parameters
    ----------
    name
      The well's name, for instance "A1"

    row
      The well's row (a number, starting from 0)

    column
      The well's column (a number, starting from 0)

    contents
      A vector of well_contents like Name, Lenght, Concentration.
    """

    MAX_VOL = 200
    MIN_VOL = 35

    def __init__(self, name, row, column):
        self.name = name
        self.row = row
        self.column = column
        self.samples = []

    def set_name(self, name):
        self.name = name

    def set_row(self, row):
        self.row = row

    def set_column(self, column):
        self.column = column

    def get_row(self):
        return self.row

    def get_column(self):
        return self.column

    def get_num_samples(self):
        return len(self.samples)

    def get_sample(self):
        return self.samples

    def is_empty(self):
        if len(self.samples) == 0:
            return True
        else:
            return False


class Sample:

    """
    Parameters
    ----------
    contents
      Sample: Name, Lenght, Concentration, volume.
    """
    counter = 0
    MAX_VOL = 35
    MIN_VOL = 4
    AVR_VOL = 10

    def __init__(self, name, type, length, concentration, volume):
        self.name = name
        self.type = type
        self.length = length
        self.concentration = concentration
        self.volume = volume
        self.id = Sample.counter
        Sample.counter += 1

    def set_sample_name(self, name):
        self.name = name

    def set_length(self, length):
        self.length = length

    def set_concentration(self, concentration):
        self.concentration = concentration

    def set_volume(self, volume):
        self.volume = volume

    def get_name(self):
        return self.name

    def get_length(self):
        return self.length

    def get_concentration(self):
        return self.concentration

    def get_volume(self):
        return self.volume