"""
Boat polars file
Have TWA(True wind Angle) and TWS (True Wind speed) value for calculate boat speed and properties


"""
import numpy as np
""" Interpolation  a method of constructing new data points based on the range of a discrete set of known data points. 
The data must be defined on a regular grid; the grid spacing however may be uneven. Linear and nearest-neighbor
 interpolation are supported """
from scipy.interpolate import RegularGridInterpolator

from utils import knots_to_mps #Convert  knot value in meter per second


class Boat:
    speedfunc: float
    polars: np.ndarray

    def __init__(self, rpm, filepath):
        self.rpm = rpm
        self.boat_properties(filepath)

    def get_rpm(self):
        return self.rpm

    def get_fuel_per_time(self, delta_time):
        f = 0.0007 * self.rpm**3 + 0.0297 * self.rpm**2 + 2.8414 * self.rpm - 19.359  # fuel [kg/h]
        f *=  delta_time/3600 * 1/1000      # amount of fuel for this time interval
        return f

    def get_speed_dict(self):
        return {'func': self.speedfunc, 'polars': self.polars}

    def set_rpm(self, rpm):
        self.rpm = rpm

    def boat_properties(self, filepath):
        """
        Load boat properties from boat file.

            Parameters:
                    filepath (string): Path to polars file polar VO7O

            Returns:
                    boat (dict): Dict with function and raw polars
        """
        self.polars = np.genfromtxt(filepath, delimiter=';')
        self.polars = np.nan_to_num(self.polars)  # Replace with NAN value with the zero or infinity values

        ws = self.polars[0, 1:]
        wa = self.polars[1:, 0]
        values = self.polars[1:, 1:]

        # internally we use only meters per second
        ws = knots_to_mps(ws)
        values = knots_to_mps(values)

        self.speedfunc = RegularGridInterpolator(  # returns interpolated grid
            (ws, wa), values.T,
            bounds_error=False,
            fill_value=None
        )
        # return {'func': f, 'polars': polars}

    def boat_speed_function(self, wind):
        """
        Vectorized boat speed function.

            Parameters:
                    boat (dict): Boat dict with wind function
                    wind (dict): Wind dict with TWA and TWS arrays

            Returns:
                    boat_speed (array): Array of boat speeds
        """
        twa = wind['twa']
        tws = wind['tws']
        # Assert to check the condition if false give assertion error
        assert twa.shape == tws.shape, "Input shape mismatch"
        # func = boat['func']

        # get rid of negative and above 180
        twa = np.abs(twa)
        twa[twa > 180] = 360. - twa[twa > 180]

        # init boat speed vector
        boat_speed = self.speedfunc((tws, twa))
        return boat_speed
