__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *
import numpy as np


class SampledCosts(Module):
    display_name = "Sampled costs"
    group_name = "ABM"
    """
    Module Initialisation
    """

    def __init__(self):
        Module.__init__(self)

        # To use the GDAL API
        self.setIsGDALModule(True)
        # Parameter Definition

        # self.createParameter("rwht_view_name", STRING)
        # self.rwht_view_name = "rwht"
        self.createParameter("quartile", INT)
        self.quartile = 2

        self.__construction_cost_indoor_db = {
            2000: {2: 1854, 10: 2299, 5: 2262},
            2001: {2: 1936, 10: 2401, 5: 2362},
            2002: {2: 1995, 10: 2474, 5: 2434},
            2003: {2: 2051, 10: 2544, 5: 2503},
            2004: {2: 2092, 10: 2595, 5: 2553},
            2005: {2: 2144, 10: 2659, 5: 2616},
            2006: {2: 2213, 10: 2745, 5: 2700},
            2007: {2: 2264, 10: 2809, 5: 2763},
            2008: {2: 2359, 10: 2927, 5: 2879},
            2009: {2: 2393, 10: 2968, 5: 2919},
            2010: {2: 2467, 10: 3060, 5: 3010},
            2011: {2: 2552, 10: 3165, 5: 3114},
            2012: {2: 2593, 10: 3216, 5: 3164},
            2013: {2: 2657, 10: 3296, 5: 3242},
            2014: {2: 2719, 10: 3372, 5: 3317},
            2015: {2: 2757, 10: 3420, 5: 3364}}
        self.__construction_cost_outdoor_db = {
            2000: {2: 1395, 10: 1840, 5: 1803},
            2001: {2: 1456, 10: 1922, 5: 1882},
            2002: {2: 1501, 10: 1980, 5: 1940},
            2003: {2: 1543, 10: 2036, 5: 1995},
            2004: {2: 1574, 10: 2077, 5: 2035},
            2005: {2: 1613, 10: 2128, 5: 2085},
            2006: {2: 1665, 10: 2197, 5: 2152},
            2007: {2: 1704, 10: 2248, 5: 2202},
            2008: {2: 1775, 10: 2342, 5: 2294},
            2009: {2: 1800, 10: 2375, 5: 2327},
            2010: {2: 1856, 10: 2449, 5: 2399},
            2011: {2: 1920, 10: 2534, 5: 2482},
            2012: {2: 1951, 10: 2574, 5: 2522},
            2013: {2: 1999, 10: 2638, 5: 2584},
            2014: {2: 2046, 10: 2699, 5: 2644},
            2015: {2: 2075, 10: 2737, 5: 2681}}

        discount_rate = 0.05
        self.__years = []

        self.__discount_factor = []
        for y in xrange(1, 21, 1):
            self.__years.append(y)
            self.__discount_factor.append(1. / (1. + discount_rate) ** (y - 1))

        annum = range(2000, 2017)
        cpi_list = [70.5, 74.7, 76.9, 79.6, 81.1, 82.7, 85.0, 86.9, 90.7, 92.6, 95.2, 98.5, 99.9, 102.4, 105.3, 106.4,
                    108.2]
        self.__cpi = {}
        for y, c in zip(annum, cpi_list):
            self.__cpi[y] = c

        self.__pump2010 = 355
        self.__plumb2010 = 730
        self.__inst2010 = 550
        self.__mus = {2:930,5:1536,10:1593}
        self.__sigmas = {2:350,5:723,10:217}


    def init(self):

            self.__rwht_option = ViewContainer("rwht_option", COMPONENT, READ)
            # self.rwht_option.addAttribute("plumbed", Attribute.DOUBLE, READ)
            self.__rwht_option.addAttribute("year", Attribute.INT, READ)
            self.__rwht_option.addAttribute("volume", Attribute.DOUBLE, READ)
            self.__rwht_option.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
            self.__rwht_option.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
            self.__rwht_option.addAttribute("price", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
            self.__rwht_option.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)

            # self.rwht_option.addAttribute("cost_factor", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("indoor_factor", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("outdoor_factor", Attribute.DOUBLE, READ)

            self.__rwht_option.addAttribute("pv_total_costs_indoor", Attribute.DOUBLE, WRITE)
            self.__rwht_option.addAttribute("pv_total_costs_outdoor", Attribute.DOUBLE, WRITE)

            self.__rwht_option.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
            self.__rwht_option.addAttribute("pv_outdoor_saving", Attribute.DOUBLE, WRITE)

            self.__rwht_option.addAttribute("pv_indoor", Attribute.DOUBLE, WRITE)
            self.__rwht_option.addAttribute("pv_outdoor", Attribute.DOUBLE, WRITE)

            self.registerViewContainers([self.__rwht_option])

            # Compile views
            # views = []
            # views.append(self.rwht_option)
            #
            # # Register ViewContainer to stream
            # self.registerViewContainers(views)

            # Data Stream   Definition

    """
    Data Manipulation Process (DMP)
    """



    def construction_costs_indoor(self,year, size):
        """
        Returns construction costs based on the tank size
        :param size:
        :return:
        """
        sampled = int(np.random.normal(self.__mus[size], self.__sigmas[size], 1))
        sampled_2010 = sampled * self.__cpi[2010] / self.__cpi[2016]

        nominal = sampled_2010 + self.__pump2010 + self.__plumb2010 + self.__inst2010

        try:
            return nominal* self.__cpi[year]/ self.__cpi[2010]
        except:
            raise LookupError("No such tank found")

    def construction_costs_outdoor(self,year, size):
        """
        Returns construction costs based on the tank size
        :param size:
        :return:
        """
        sampled = int(np.random.normal(self.__mus[size], self.__sigmas[size], 1))
        sampled_2010 = sampled * self.__cpi[2010] / self.__cpi[2016]

        nominal = sampled_2010 + self.__plumb2010 + self.__inst2010

        try:
            return nominal* self.__cpi[year]/ self.__cpi[2010]
        except:
            raise LookupError("No such tank found")

    def maintenance_costs(self):
        maintenance_cost = []
        for y in self.__years:
            maintenance_cost.append(20.)

        discount_maintenance_cost = [d * m for d, m in zip(self.__discount_factor, maintenance_cost)]

        return sum(discount_maintenance_cost)

    def pv_total_costs_indoor_fun(self, year, volume):

        try:
            return self.construction_costs_indoor(year, volume) + self.maintenance_costs()
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_total_costs_outdoor_fun(self, year, volume):
        try:
            return self.construction_costs_outdoor(year, volume) + self.maintenance_costs()
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_non_potable_saving_fun(self, annual_water_savings, price):
        indoor_water_price = []
        # points = np.array([(2005, 1.17), (2008,  1.62), (2009,  1.85), (2010, 2.1), (2011, 2.36), (2012, 2.11), (2013, 2.59), (2014, 2.55), (2015, 2.62)])
        # # get x and y vectors
        # x = points[:,0]
        # y = points[:,1]
        # # calculate polynomial
        # z = np.polyfit(x, y,3)
        # f = np.poly1d(z)

        for y in self.__years:
            # indoor_water_price.append(2.5)
            indoor_water_price.append(price)

        discount_non_potable_savings = [d * m * annual_water_savings for d, m in
                                        zip(self.__discount_factor, indoor_water_price)]

        return sum(discount_non_potable_savings)

    def pv_outdoor_saving_fun(self, outdoor_water_savings, price):
        indoor_water_price = []

        for y in self.__years:
            # indoor_water_price.append(2.5)
            indoor_water_price.append(price)

        discount_outdoor_savings = [d * m * outdoor_water_savings for d, m in
                                    zip(self.__discount_factor, indoor_water_price)]

        return sum(discount_outdoor_savings)

    def run(self):
        # Data Stream Manipulation


        self.__rwht_option.reset_reading()

        for r in self.__rwht_option:
            year = r.GetFieldAsInteger("year")
            volume = r.GetFieldAsDouble("volume")
            price = r.GetFieldAsDouble("price")
            # f = r.GetFieldAsDouble("cost_factor")

            # out_factor = r.GetFieldAsDouble("outdoor_factor")
            # in_factor = r.GetFieldAsDouble("indoor_factor")

            # Calculate PV for indoor use
            # print 'year is: ',y
            pv_total_costs_indoor = self.pv_total_costs_indoor_fun(year, volume)
            # pv_non_potable_saving = pv_non_potable_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")*out_factor+r.GetFieldAsDouble("non_potable_savings")*in_factor), p)
            pv_non_potable_saving = self.pv_non_potable_saving_fun(
                (r.GetFieldAsDouble("outdoor_water_savings") + r.GetFieldAsDouble("non_potable_savings")), price)
            pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
            r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
            r.SetField("pv_non_potable_saving", pv_non_potable_saving)
            r.SetField("pv_indoor", pv_indoor)

            # Calculate PV for outdoor use
            pv_total_costs_outdoor = self.pv_total_costs_outdoor_fun(year, volume)
            # pv_outdoor_saving = pv_outdoor_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")*out_factor), p)
            pv_outdoor_saving = self.pv_outdoor_saving_fun(r.GetFieldAsDouble("outdoor_water_savings"), price)
            pv_outdoor = pv_outdoor_saving - pv_total_costs_outdoor
            r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
            r.SetField("pv_outdoor_saving", pv_outdoor_saving)
            r.SetField("pv_outdoor", pv_outdoor)

        self.__rwht_option.finalise()
