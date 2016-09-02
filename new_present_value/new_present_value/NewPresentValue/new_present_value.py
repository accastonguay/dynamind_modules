from pydynamind import *


class NewPresentValue(Module):
    display_name = "New Present Value"
    group_name = "ABM"
    """
    Module Initialisation
    """

    def __init__(self):
        Module.__init__(self)

        # To use the GDAL API
        self.setIsGDALModule(True)
        # Parameter Definition

        self.createParameter("rwht_view_name", STRING)
        self.rwht_view_name = "rwht"


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

    def init(self):

        self.__rwht = ViewContainer(self.rwht_view_name, COMPONENT, READ)

        self.__rwht.addAttribute("year", Attribute.INT, READ)
        self.__rwht.addAttribute("volume", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("price", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("wtp", Attribute.DOUBLE, READ)

        self.__rwht.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)


        self.__rwht.addAttribute("pv_total_costs_indoor", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_total_costs_outdoor", Attribute.DOUBLE, WRITE)

        self.__rwht.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_outdoor_saving", Attribute.DOUBLE, WRITE)

        self.__rwht.addAttribute("pv_indoor", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_outdoor", Attribute.DOUBLE, WRITE)


        self.registerViewContainers([self.__rwht])



    """
    Data Manipulation Process (DMP)
    """



    def construction_costs_indoor(self,year, size):
        """
        Returns construction costs based on the tank size
        :param size:
        :return:
        """

        try:
            return self.__construction_cost_indoor_db[year][int(size)]
        except:
            raise LookupError("No such tank found")

    def construction_costs_outdoor(self,year, size):
        """
        Returns construction costs based on the tank size
        :param size:
        :return:
        """
        try:
            return self.__construction_cost_outdoor_db[year][int(size)]
        except:
            raise LookupError("No such tank found")

    def maintenance_costs_indoor(self, annual_savings):
        maintenance_cost = []
        savings = []
        for y in self.__years:
            maintenance_cost.append(20.)
            savings.append(annual_savings)


        discount_maintenance_cost = [(d * m)+(s * 0.05 * d) for d, m, s in zip(self.__discount_factor, maintenance_cost, savings)]

        return sum(discount_maintenance_cost)

    def maintenance_costs_outdoor(self, outdoor_savings):
        maintenance_cost = []
        savings = []
        for y in self.__years:
            maintenance_cost.append(20.)
            savings.append(outdoor_savings)

        discount_maintenance_cost = [(d * m)+(s * 0.05 * d) for d, m, s in zip(self.__discount_factor, maintenance_cost, savings)]

        return sum(discount_maintenance_cost)

    def pv_total_costs_indoor_fun(self, year, volume, annual_savings):
        pump_future_value = 355 * 1. / (1. + 0.05) ** (10)
        try:
            return self.construction_costs_indoor(year, volume) + self.maintenance_costs_indoor(annual_savings)+pump_future_value
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_total_costs_outdoor_fun(self, year, volume, outdoor_savings):
        try:
            return self.construction_costs_outdoor(year, volume) + self.maintenance_costs_outdoor(outdoor_savings)
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_non_potable_saving_fun(self, annual_water_savings, price):
        indoor_water_price = []

        for y in self.__years:
            indoor_water_price.append(price)

        discount_non_potable_savings = [d * m * annual_water_savings for d, m in
                                        zip(self.__discount_factor, indoor_water_price)]

        return sum(discount_non_potable_savings)

    def pv_outdoor_saving_fun(self, outdoor_water_savings, price, wtp):
        indoor_water_price = []
        wtp_list = []
        for y in self.__years:
            indoor_water_price.append(price)
            wtp_list.append(wtp)

        discount_outdoor_savings = [(d * m * outdoor_water_savings) + (w*d) for d, m, w in
                                    zip(self.__discount_factor, indoor_water_price, wtp_list)]

        return sum(discount_outdoor_savings)

    def run(self):
        # Data Stream Manipulation


        self.__rwht.reset_reading()

        for r in self.__rwht:


            # Calculate PV for indoor use
            pv_total_costs_indoor = self.pv_total_costs_indoor_fun(r.GetFieldAsInteger("year"), r.GetFieldAsDouble("volume"),r.GetFieldAsDouble("annual_water_savings"))
            pv_non_potable_saving = self.pv_non_potable_saving_fun(
                r.GetFieldAsDouble("annual_water_savings"), r.GetFieldAsDouble("price"))
            pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
            r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
            r.SetField("pv_non_potable_saving", pv_non_potable_saving)
            r.SetField("pv_indoor", pv_indoor)

            # Calculate PV for outdoor use
            pv_total_costs_outdoor = self.pv_total_costs_outdoor_fun(r.GetFieldAsInteger("year"), r.GetFieldAsDouble("volume"),r.GetFieldAsDouble("outdoor_water_savings"))
            pv_outdoor_saving = self.pv_outdoor_saving_fun(r.GetFieldAsDouble("outdoor_water_savings"), r.GetFieldAsDouble("price"),r.GetFieldAsDouble("wtp"))
            pv_outdoor = pv_outdoor_saving - pv_total_costs_outdoor
            r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
            r.SetField("pv_outdoor_saving", pv_outdoor_saving)
            r.SetField("pv_outdoor", pv_outdoor)


        self.__rwht.finalise()
