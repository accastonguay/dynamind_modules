__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *
import numpy as np


class WaterPrice(Module):
        display_name = "price"
        group_name = "test"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("price", DOUBLE)
            self.price = 1


            self.city = ViewContainer("city", COMPONENT, READ)

            self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("price", Attribute.DOUBLE, WRITE)
            # self.city.addAttribute("inflow", Attribute.DOUBLE, WRITE)



            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.city)
            # views.append(self.city)


            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            #print self.my_parameter

            #Data Stream Manipulation

            #print self.my_parameter
            self.city.reset_reading()
            # self.city.reset_reading()

            points = np.array([(2005, 1.17), (2008,  1.62), (2009,  1.85), (2010, 2.1), (2011, 2.08), (2012, 2.08), (2013, 3.04), (2014, 2.99), (2015, 3.07)])
            # get x and y vectors
            x = points[:,0]
            y = points[:,1]
            # calculate polynomial
            z = np.polyfit(x, y,3)
            f = np.poly1d(z)



            dict = {2005: 1.17, 2008:  1.62, 2009:  1.85, 2010: 2.1, 2011: 2.36, 2012: 2.11, 2013: 2.59, 2014: 2.55, 2015: 2.62}

            for b in self.city:
                year = b.GetFieldAsInteger("year")

                if year in dict.keys():
                    p = dict[year]
                    # print 'year is: '+str(year)+ ' ; inflow is: ' + str(dict[year])
                    b.SetField("price", p)

                else:
                    p = f(year)
                    b.SetField("price", p)

            self.city.finalise()
            # self.city.finalise()