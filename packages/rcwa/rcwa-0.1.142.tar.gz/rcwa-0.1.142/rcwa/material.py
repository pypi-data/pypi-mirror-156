"""
I think the way this currently works is too convoluted. It needs to be refactored to be understandable.

"""
import numpy as np
import pandas as pd
import rcwa
import os
from rcwa.utils import CSVLoader, RIDatabaseLoader

class Material:
    database = RIDatabaseLoader()

    def __init__(self, name=None, er=1, ur=1, n=None, database_path=None, filename=None, source=None):
        """
        Material class for defining materials permittivity / permeability / refractive index as a function of wavelength / angle.

        :param filename: File containing n/k data for the material in question
        :param name: Material name to be looked up in database (i.e. Si)
        :param er: Complex-valued numerical permittivity value or function of wavelength
        :param ur: Complex-valued numerical permeability value or function of wavelength
        :param source: Excitation source to link to material (mandatory for dispersive materials)
        """
        self.name = ''
        self.source=source
        self.dispersive = False
        self.loader = None

        if callable(er) or callable(ur):
            self.dispersive = True
            self._er_dispersive = er
            self._ur_dispersive = ur
        else:
            self._er = er
            self._ur = ur

        if name is not None or database_path is not None:
            self.dispersive = True
            self.load_from_database(name, filename=database_path)
        elif filename is not None:
            self.dispersive = True
            self.load_from_nk_table(filename=filename)
        else:
            self.dispersive = False
            if n == None: # If the refractive index is not defined, go with the permittivity
                self._er = er
                self._ur = ur
                self._n = np.sqrt(er*ur)
            else: # If the refractive index is defined, ignore the permittivity and permeability
                self._n = n
                self._er = np.square(n)
                self._ur = 1

    def set_dispersive_nk(self, data_dict):
        """
        Set our internal dispersive refractive index, permittivity, and permeability based on
        received data dictionary
        """
        self._n_dispersive = data_dict['n']
        self._er_dispersive = data_dict['er']
        self._ur_dispersive = data_dict['ur']
        if 'dispersion_type' in data_dict.keys():
            self.dispersion_type = data_dict['dispersion_type']
        if 'wavelength' in data_dict.keys():
            self.wavelengths = data_dict['wavelength']

    def load_from_nk_table(self, filename):
        self.dispersion_type = 'tabulated'
        loader = CSVLoader(filename=filename)
        data_dict = loader.load()
        self.set_dispersive_nk(data_dict)

    def load_from_database(self, material_name, filename=None):
        """
        Parses data from a CSV or database YAML file into a set of numpy arrays.

        :param filename: File containing n/k data for material in question
        """

        if filename is not None:
            file_to_load = os.path.join(rcwa.nkLocation, 'data', filename)

        if material_name in self.database.materials.keys():
            file_to_load = os.path.join(rcwa.nkLocation, 'data', self.database.materials[material_name])

        data_dict = self.database.load(file_to_load)
        self.set_dispersive_nk(data_dict)

    @property
    def n(self):
        if self.dispersive == False:
            return self._n
        else:
            return self.lookupParameter(self._n_dispersive)

    @n.setter
    def n(self, n):
        self._n = n
        self._er = np.square(n)
        self._ur = 1

    @property
    def er(self):
        if self.dispersive == False:
            return self._er
        else:
            return self.lookupParameter(self._er_dispersive)

    @er.setter
    def er(self, er):
        self._er = er
        self._n = np.sqrt(self._er * self._ur)

    @property
    def ur(self):
        if self.dispersive == False:
            return self._ur
        else:
            return self.lookupParameter(self._ur_dispersive)

    @ur.setter
    def ur(self, ur):
        self._ur = ur
        self._n = np.sqrt(self._ur*self._er)


    def lookupParameter(self, parameter):
        if self.dispersion_type == 'tabulated':
            return self.lookupNumeric(parameter)
        elif self.dispersion_type == 'formula':
            wavelength = self.source.wavelength
            return parameter(wavelength)

    def lookupNumeric(self, parameter):
        """
        Looks up a numeric value of a parameter

        :param parameter: Either _n_dispersive, _er_dispersive, or _ur_dispersive
        """
        wavelength = self.source.wavelength
        indexOfWavelength = np.searchsorted(self.wavelengths, wavelength)
        return_value = 0

        if wavelength > self.wavelengths[-1]: # Extrapolate if necessary
            slope = (parameter[-1] - parameter[-2]) / (self.wavelengths[-1] - self.wavelengths[-2])
            deltaWavelength = wavelength - self.wavelengths[-1]
            return_value = parameter[-1] + slope * deltaWavelength

        elif wavelength < self.wavelengths[0]: # Extrapolate the other direction if necessary
            slope = (parameter[1] - parameter[0]) / (self.wavelengths[1] - self.wavelengths[0])
            deltaWavelength = self.wavelengths[0] - wavelength
            return_value = parameter[0] - slope * deltaWavelength

        else: # Our wavelength is in the range over which we have data
            if wavelength == self.wavelengths[indexOfWavelength]: # We found the EXACT wavelength
                return_value = parameter[indexOfWavelength]
            else: # We need to interpolate the wavelength. The indexOfWavelength is pointing to the *next* value
                slope = (parameter[indexOfWavelength] - parameter[indexOfWavelength-1]) / (self.wavelengths[indexOfWavelength] - self.wavelengths[indexOfWavelength-1]) # wavelength spacing between two points
                deltaWavelength = wavelength - self.wavelengths[indexOfWavelength]
                return_value = parameter[indexOfWavelength] + slope * deltaWavelength

        return return_value
