"""Utility functions."""
import datetime


def mps_to_knots(vals):
    """convert the Meters/second to knots.
    knot is a unit of speed equal to one nautical mile per hour, exactly 1.852 km/h."""
    return vals * 3600.0 / 1852.0

def knots_to_mps(vals):
    """convert the Meters/second to knots.
        knot is a unit of speed equal to one nautical mile per hour, exactly 1.852 km/h."""

    return vals * 1852.0 / 3600.0

def round_time(dt=None, round_to=60):
    """
        Round a datetime object to any time lapse in seconds.
        ref: /questions/3463930/how-to-round-the-minute-of-a-datetime-object
        dt : datetime.datetime object, default now.
        round_to : Closest number of seconds to round to, default 1 minute.

        """

    if dt is None:
        dt = datetime.datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + datetime.timedelta(0, rounding - seconds, - dt.microsecond)

def twopi_to_pmpi(degrees):
    if(degrees>180): degrees = degrees-360
    if((degrees>360) or (degrees <-360)): raise ValueError('Angle of' + str(degrees))
    return degrees

def print_line():
    print('---------------------------------------------------')

def print_step(stepnote, istep=0):
    step = "   " * (istep+1) + stepnote
    print(step)