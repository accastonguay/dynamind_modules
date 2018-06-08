__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr

class mel_water_demand(Module):
        display_name = "Water demands"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.__leakage = {2005: 45, 2006: 45, 2007: 42, 2008: 41, 2009: 36, 2010: 36, 2011: 40, 2012: 42, 2013: 42, 2014: 42}

            self.__non_residential = {2005: 117, 2006: 108, 2007: 100, 2008: 97, 2009: 93, 2010: 89, 2011: 92, 2012: 100, 2013: 99, 2014: 100}

            self.city = ViewContainer("city", COMPONENT, READ)

            self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("mel_leakage", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("mel_non_residential", Attribute.DOUBLE, WRITE)

            #Register ViewContainer to stream
            self.registerViewContainers([self.city])

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            self.city.reset_reading()

            for c in self.city:

                year = c.GetFieldAsInteger("year")

                if year <= 2014:
                    c.SetField("mel_leakage", self.__leakage[year])
                    c.SetField("mel_non_residential", self.__non_residential[year])
                else:
                    c.SetField("mel_leakage", 42)
                    c.SetField("mel_non_residential", 100)

            self.city.finalise()