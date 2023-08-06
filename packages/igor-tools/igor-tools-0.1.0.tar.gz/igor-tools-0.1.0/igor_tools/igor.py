"""Classes for use with IGOR Pro

Partially based on asetk module by Leopold Talirz
(https://github.com/ltalirz/asetk/blob/master/asetk/format/igor.py)
"""

import re
import numpy as np

def read_wave(lines):
    """
    Reads the next wave section from the inputted list of lines
    Parsed lines are removed from the list, allowing for subsequent calls
    """

    line = lines.pop(0)
    while not re.match("WAVES",line):
        if len(lines) == 0:
            return None
        line = lines.pop(0)
    # 1d or 2d?
    d2 = False
    if "N=" in line:
        d2 = True
        match = re.search("WAVES/N=\(([\d, ]+)\)",line)
        grid = match.group(1).split(',')
        grid = np.array(grid, dtype=int)
        name = line.split(")")[-1].strip()
    else:
        name = line.split()[-1]

    line = lines.pop(0).strip()
    if not line == "BEGIN":
        raise IOError("Missing 'BEGIN' statement of data block")

    # read data
    datastring = ""
    line = lines.pop(0)
    while not re.match("END",line):
        if len(lines) == 0:
            return None
        if line.startswith("X"):
            return None
        datastring += line
        line = lines.pop(0)
    data = np.array(datastring.split(), dtype=float)
    if d2:
        data = data.reshape(grid)
    
    # read axes
    axes = []
    line = lines.pop(0)
    matches = re.findall("SetScale.+?(?:;|$)", line)
    for match in matches:
        ax = Axis(None,None,None,None)
        ax.read(match)
        axes.append(ax)
    
    if d2:
        # read also the second axis
        # is this necessary? can there be 2 lines with "SetScale" ?
        line = lines.pop(0)
        matches = re.findall("SetScale.+?(?:;|$)", line)
        for match in matches:
            ax = Axis(None,None,None,None)
            ax.read(match)
            axes.append(ax)
        return Wave2d(data, axes, name)

    return Wave1d(data, axes, name)


class Axis(object):
    """Represents an axis of an IGOR wave"""

    def __init__(self, symbol, min_, delta, unit, wavename=None):
        self.symbol = symbol
        self.min = min_
        self.delta = delta
        self.unit = unit
        self.wavename = wavename

    def __str__(self):
        """Prints axis in itx format
        Note: SetScale/P expects minimum value and step-size
        """
        delta = 0 if self.delta is None else self.delta
        s = "X SetScale/P {symb} {min},{delta}, \"{unit}\", {name};\n"\
              .format(symb=self.symbol, min=self.min, delta=delta,\
                      unit=self.unit, name=self.wavename)
        return s

    def read(self, string):
        """Read axis from string
        Format: 
        X SetScale/P x 0,2.01342281879195e-11,"m", data_00381_Up;
        SetScale d 0,0,"V", data_00381_Up
        """
        match = re.search("SetScale/?P? (.) ([+-\.\de]+),([+-\.\de]+),[ ]*\"(.*)\",\s*(\S+)", string)
        self.symbol = match.group(1)
        self.min = float(match.group(2))
        self.delta = float(match.group(3))
        self.unit = match.group(4)
        self.wavename = match.group(5)
        if self.wavename.endswith(';'):
            self.wavename = self.wavename[:-1]


class Wave(object):
    """A class for IGOR waves"""

    def __init__(self, data, axes, name=None):
        """Initialize IGOR wave of generic dimension"""
        self.data = data
        self.axes = axes
        self.name = "PYTHON_IMPORT" if name is None else name
        self.dim = len(self.data.shape)

    def __str__(self):
        """Print IGOR wave"""
        s = ""
        s += "IGOR\n"

        dimstring = "("
        for i in range(len(self.data.shape)):
            dimstring += "{}, ".format(self.data.shape[i])
        dimstring = dimstring[:-2] + ")" 

        s += "WAVES/N={}  {}\n".format(dimstring, self.name)
        s += "BEGIN\n"
        s += self.print_data()
        s += "END\n"
        for ax in self.axes:
            s += str(ax)
        return s

    @property
    def extent(self):
        """Returns extent for plotting"""
        grid = self.data.shape
        extent = []
        for i in range(len(grid)):
            ax = self.axes[i]
            extent.append(ax.min)
            extent.append(ax.min+ax.delta*grid[i])

        return np.array(extent)

    @property
    def x_min(self):
        return self.axes[0].min

    @property
    def dx(self):
        return self.axes[0].delta

    @property
    def x_max(self):
        return self.x_min + self.dx * self.data.shape[0]

    @property
    def x_arr(self):
        return self.x_min + np.arange(0, self.data.shape[0])*self.dx

    @property
    def x_symbol(self):
        return self.axes[0].symbol

    @property
    def x_unit(self):
        return self.axes[0].unit

    def print_data(self):
        """Determines how to print the data block.
        
        To be reimplemented by subclasses."""
        pass

    def write(self, fname):
        f=open(fname, 'w')
        f.write(str(self))
        f.close()
    
    def csv_header(self):
        header = ""
        shape = self.data.shape
        for i_ax in range(len(shape)):
            ax = self.axes[i_ax]
            if header != "":
                header += "\n"
            header += "axis %d: %s [unit: %s] [%.6e, %.6e], delta=%.6e, n=%d" % (
                i_ax, ax.symbol, ax.unit, ax.min, ax.min+ax.delta*(shape[i_ax]-1), ax.delta, shape[i_ax]
            )
        return header
    
    def write_csv(self, fname, fmt="%.6e"):
        np.savetxt(fname, self.data, delimiter=",", header=self.csv_header(), fmt=fmt)


class Wave1d(Wave):
    """1d Igor wave"""

    def __init__(self, data, axes, name="1d"):
        """Initialize 1d IGOR wave"""
        super().__init__(data, axes, name)

    def print_data(self):
        """Determines how to print the data block"""
        s = ""
        for line in self.data:
            s += "{:12.6e}\n".format(float(line))
        return s


class Wave2d(Wave):
    """2d Igor wave"""

    def __init__(self, data, axes, name="2d"):
        """Initialize 2d IGOR wave"""
        super().__init__(data, axes, name)

    def print_data(self):
        """Determines how to print the data block"""
        s = ""
        for line in self.data:
            for x in line:
                s += "{:12.6e} ".format(x)
            s += "\n"
        return s

    @property
    def y_min(self):
        return self.axes[1].min

    @property
    def dy(self):
        return self.axes[1].delta

    @property
    def y_max(self):
        return self.y_min + self.dy * self.data.shape[1]

    @property
    def y_arr(self):
        return self.y_min + np.arange(0, self.data.shape[1])*self.dy

    @property
    def y_symbol(self):
        return self.axes[1].symbol

    @property
    def y_unit(self):
        return self.axes[1].unit