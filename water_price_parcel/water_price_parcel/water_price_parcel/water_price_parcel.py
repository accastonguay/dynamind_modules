__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *
import numpy as np


class WaterPriceParcel(Module):
        display_name = "price per use"
        group_name = "ABM"
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


            self.parcel = ViewContainer("parcel", COMPONENT, READ)

            self.parcel.addAttribute("year", Attribute.INT, READ)
            self.parcel.addAttribute("total_daily_demand", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("price", Attribute.DOUBLE, WRITE)
            # self.city.addAttribute("inflow", Attribute.DOUBLE, WRITE)



            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.parcel)
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
            self.parcel.reset_reading()
            # self.city.reset_reading()

            points = np.array([(2005, 1.17), (2008,  1.62), (2009,  1.85), (2010, 2.1), (2011, 2.08), (2012, 2.08), (2013, 3.04), (2014, 2.99), (2015, 3.07)])
            # get x and y vectors
            x = points[:,0]
            y = points[:,1]
            # calculate polynomial
            z = np.polyfit(x, y,3)
            f = np.poly1d(z)



            dict = {2005: 1.17, 2008:  1.62, 2009:  1.85, 2010: 2.1, 2011: 2.36, 2012: 2.11, 2013: 2.59, 2014: 2.55, 2015: 2.62}
            dict1 = {2012: 1.78, 2013: 2.59, 2014: 2.55, 2015: 2.62}
            dict2 = {2012: 2.08, 2013: 3.04, 2014: 2.99, 2015: 3.07}
            dict3 = {2012: 3.08, 2013: 4.5, 2014: 4.4, 2015: 4.54}

            for b in self.parcel:
                year = b.GetFieldAsInteger("year")
                demand = b.GetFieldAsDouble("total_daily_demand")
                if year < 2011:
                    if year in dict.keys():
                        p = dict[year]
                        b.SetField("price", p)
                    else:
                        p = f(year)
                        b.SetField("price", p)
                elif year == 2011:
                    if demand <160:
                        b.SetField("price", 1.77)
                    elif 160 <= demand < 320:
                        b.SetField("price", 2.08)
                    elif demand >= 320:
                        b.SetField("price", 3.07)
                elif year > 2011:
                    if demand <440:
                        p = dict1[year]
                        b.SetField("price", p)
                    elif 440 <= demand < 880:
                        p = dict2[year]
                        b.SetField("price", p)
                    elif demand >= 880:
                        p = dict3[year]
                        b.SetField("price", p)



            self.parcel.finalise()
            # self.city.finalise()
