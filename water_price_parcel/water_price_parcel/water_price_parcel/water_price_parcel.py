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

            self.createParameter("time", INT)
            self.time = 1


            points = np.array([(2003, 0.7757),(2004, 0.88), (2005,  0.92),(2006, 0.96), (2007,  0.99)])

            x = points[:,0]
            y = points[:,1]
            # calculate polynomial
            z = np.polyfit(x, y,1)
            self.__f = np.poly1d(z)

            self.__dict1 = {2004: 0.75, 2005: 0.78, 2006: 0.81, 2007: 0.85, 2008: 1.01, 2009: 1.25, 2010: 1.53, 2011: 1.77, 2012: 1.77, 2013: 2.59, 2014: 2.55, 2015: 2.62}
            self.__dict2 = {2004: 0.88, 2005: 0.92, 2006: 0.96, 2007: 0.99, 2008: 1.19, 2009: 1.47, 2010: 1.8, 2011: 2.08, 2012: 2.08, 2013: 3.04, 2014: 2.99, 2015: 3.07}
            self.__dict3 = {2004: 1.3, 2005: 1.35, 2006: 1.41, 2007: 1.47, 2008: 1.76, 2009: 2.17, 2010: 2.65, 2011: 3.07, 2012: 3.07, 2013: 4.50, 2014: 4.42, 2015: 4.54}

            self.__dict4 = {2005: 0.75, 2006: 0.7842, 2007: 0.8184, 2008: 0.8517, 2009: 1.0192, 2010: 1.2532, 2011: 1.5343, 2012: 1.7756, 2013: 1.7756, 2014: 2.597, 2015: 2.5523}
            self.__dict5 = {2005: 0.88, 2006: 0.92005, 2007: 0.9601, 2008: 0.9992, 2009: 1.1957, 2010: 1.4702, 2011: 1.8, 2012: 2.0832, 2013: 2.0832, 2014: 3.0469, 2015: 2.9944}
            self.__dict6 = {2005: 1.3, 2006: 1.35925, 2007: 1.4185, 2008: 1.4763, 2009: 1.7666, 2010: 2.1721, 2011: 2.6594, 2012: 3.0778, 2013: 3.0778, 2014: 4.5017, 2015: 4.4242}


            self.__dict7 = {2004: 0.76285, 2005: 0.7671, 2006: 0.8013, 2007: 0.83505, 2008: 0.93545, 2009: 1.1362, 2010: 1.39375, 2011: 1.65495, 2012: 1.7756, 2013: 2.1863, 2014: 2.57465, 2015: 2.58615}
            self.__dict8 = {2004: 0.82785, 2005: 0.900025, 2006: 0.940075, 2007: 0.97965, 2008: 1.09745, 2009: 1.33295, 2010: 1.6351, 2011: 1.9416, 2012: 2.0832, 2013: 2.56505, 2014: 3.02065, 2015: 3.0322}
            self.__dict9 = {2004: 1.03785, 2005: 1.329625, 2006: 1.388875, 2007: 1.4474, 2008: 1.62145, 2009: 1.96935, 2010: 2.41575, 2011: 2.8686, 2012: 3.0778, 2013: 3.78975, 2014: 4.46295, 2015: 4.4821}

            self.__sewer_price = {2005: 0.9921, 2006: 1.0363, 2007: 1.07995, 2008: 1.2098, 2009: 1.41535, 2010: 1.6161, 2011: 1.8371, 2012: 1.9546, 2013: 2.0227, 2014: 2.0908}

        def init(self):
            self.parcel = ViewContainer("parcel", COMPONENT, READ)

            self.parcel.addAttribute("year", Attribute.INT, READ)
            self.parcel.addAttribute("total_daily_demand", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("price", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("sewer_price", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("time", Attribute.INT, WRITE)
            self.parcel.addAttribute("level", Attribute.INT, WRITE)

            #Compile views
            views = []
            views.append(self.parcel)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            self.parcel.reset_reading()
            # self.city.reset_reading()
            '''Price dictionaries for three categories of uses if year = y+1 for y-y+1 period '''

            for b in self.parcel:
                year = b.GetFieldAsInteger("year")
                demand = b.GetFieldAsDouble("total_daily_demand")
                if self.time == 1:

                    if year < 2003:
                        p = self.__f(year)
                        b.SetField("price", p)
                        b.SetField("level", 1)
                    elif year == 2003:
                        b.SetField("price", 0.7757)
                        b.SetField("level", 1)
                    elif year >= 2004:
                        if demand < 440:
                            p = self.__dict1[year]
                            b.SetField("price", p)
                            b.SetField("level", 1)
                        elif 440 <= demand < 880:
                            p = self.__dict2[year]
                            b.SetField("price", p)
                            b.SetField("level", 2)
                        elif demand >= 880:
                            p = self.__dict3[year]
                            b.SetField("price", p)
                            b.SetField("level", 3)
                    b.SetField("time", self.time)

                elif self.time == 2:
                    if year < 2004:
                        p = self.__f(year)
                        b.SetField("price", p)
                        b.SetField("level", 1)
                    elif year == 2004:
                            b.SetField("price", 0.7757)
                            b.SetField("level", 1)
                    elif year >= 2005:
                        if demand <440:
                            p = self.__dict4[year]
                            b.SetField("price", p)
                            b.SetField("level", 1)
                        elif 440 <= demand < 880:
                            p = self.__dict5[year]
                            b.SetField("price", p)
                            b.SetField("level", 2)
                        elif demand >= 880:
                            p = self.__dict6[year]
                            b.SetField("price", p)
                            b.SetField("level", 3)
                    b.SetField("time", self.time)

                elif self.time == 3:
                    if year < 2004:
                        p = self.__f(year)
                        b.SetField("price", p)
                        b.SetField("level", 1)
                    elif year == 2004:
                            b.SetField("price", 0.7757)
                            b.SetField("level", 1)
                    elif year >= 2005:
                        if demand <440:
                            p = self.__dict7[year]
                            b.SetField("price", p)
                            b.SetField("level", 1)
                        elif 440 <= demand < 880:
                            p = self.__dict8[year]
                            b.SetField("price", p)
                            b.SetField("level", 2)
                        elif demand >= 880:
                            p = self.__dict9[year]
                            b.SetField("price", p)
                            b.SetField("level", 3)

                    b.SetField("time", self.time)
                b.SetField("sewer_price", self.__sewer_price[year])
            self.parcel.finalise()
