import traceback

from . import igor

from .igor import Wave, Wave1d, Wave2d

__version__ = "0.1.0"


def read_itx(fname):
    """
    Returns the list of igor waves that are included in the .itx file 
    """
    f=open(fname, 'r')
    lines=f.readlines()
    f.close()

    line = lines.pop(0).strip()
    if not line == "IGOR":
        raise IOError("Files does not begin with 'IGOR'")

    waves = []
    while len(lines) != 0:
        try:
            wave = igor.read_wave(lines)
            if wave is not None:
                waves.append(wave)
        except Exception:
            traceback.print_exc()

    return waves

def write_2d_itx(fname, data, xaxis, yaxis, wavename):
    """
    Write a 2-dimensional data as .itx file

    Args:
        fname: Name of the output file
        data: the 2d data
        xaxis: iterable containing (x_min, x_delta, unit)
        yaxis: iterable containing (y_min, y_delta, unit)
        wavename: name of the igor wave
    """

    x = igor.Axis('x', xaxis[0], xaxis[1], xaxis[2], wavename)
    y = igor.Axis('y', yaxis[0], yaxis[1], yaxis[2], wavename)

    wave = Wave2d(
            data=data,
            axes=[x,y],
            name=wavename,
        )
    
    wave.write(fname)
    
