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
            '''Price dictionaries for three categories of uses if year = y+1 for y-y+1 period '''

            points = np.array([(2004, 0.7757),(2005, 0.88), (2006,  0.92),(2007, 0.96), (2008,  0.99)])
            # get x and y vectors
            x = points[:,0]
            y = points[:,1]
            # calculate polynomial
            z = np.polyfit(x, y,1)
            f = np.poly1d(z)
            dict1 = {2005: 0.75, 2006: 0.7842, 2007: 0.8184, 2008: 0.8517, 2009: 1.0192, 2010: 1.2532, 2011: 1.5343, 2012: 1.7756, 2013: 1.7756, 2014: 2.597, 2015: 2.5523}
            dict2 = {2005: 0.88, 2006: 0.92005, 2007: 0.9601, 2008: 0.9992, 2009: 1.1957, 2010: 1.4702, 2011: 1.8, 2012: 2.0832, 2013: 2.0832, 2014: 3.0469, 2015: 2.9944}
            dict3 = {2005: 1.3, 2006: 1.35925, 2007: 1.4185, 2008: 1.4763, 2009: 1.7666, 2010: 2.1721, 2011: 2.6594, 2012: 3.0778, 2013: 3.0778, 2014: 4.5017, 2015: 4.4242}


            for b in self.parcel:
                year = b.GetFieldAsInteger("year")
                demand = b.GetFieldAsDouble("total_daily_demand")
                if year < 2004:
                        p = f(year)
                        b.SetField("price", p)
                elif year == 2004:
                        b.SetField("price", 0.7757)
                elif year >= 2005:
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

            '''Price dictionaries for three categories of uses if year = y for y-y+1 period '''

            # points = np.array([(2003, 0.7757),(2004, 0.88), (2005,  0.92),(2006, 0.96), (2007,  0.99)])
            # # get x and y vectors
            # x = points[:,0]
            # y = points[:,1]
            # # calculate polynomial
            # z = np.polyfit(x, y,1)
            # f = np.poly1d(z)
            #
            # dict1 = {2004: 0.75, 2005: 0.7842, 2006: 0.8184, 2007: 0.8517, 2008: 1.0192, 2009: 1.2532, 2010: 1.5343, 2011: 1.7756, 2012: 1.7756, 2013: 2.597, 2014: 2.5523, 2015: 2.62}
            # dict2 = {2004: 0.88, 2005: 0.92005, 2006: 0.9601, 2007: 0.9992, 2008: 1.1957, 2009: 1.4702, 2010: 1.8, 2011: 2.0832, 2012: 2.0832, 2013: 3.0469, 2014: 2.9944, 2015: 3.07}
            # dict3 = {2004: 1.3, 2005: 1.35925, 2006: 1.4185, 2007: 1.4763, 2008: 1.7666, 2009: 2.1721, 2010: 2.6594, 2011: 3.0778, 2012: 3.0778, 2013: 4.5017, 2014: 4.4242, 2015: 4.54}
            # for b in self.parcel:
            #     year = b.GetFieldAsInteger("year")
            #     demand = b.GetFieldAsDouble("total_daily_demand")
            #     if year < 2003:
            #             p = f(year)
            #             b.SetField("price", p)
            #     elif year == 2003:
            #             b.SetField("price", 0.7757)
            #     elif year >= 2004:
            #         if demand <440:
            #             p = dict1[year]
            #             b.SetField("price", p)
            #         elif 440 <= demand < 880:
            #             p = dict2[year]
            #             b.SetField("price", p)
            #         elif demand >= 880:
            #             p = dict3[year]
            #             b.SetField("price", p)
            # self.parcel.finalise()
