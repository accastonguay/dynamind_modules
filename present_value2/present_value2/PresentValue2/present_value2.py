from pydynamind import *
from osgeo import ogr

class PresentValue2(Module):
    display_name = "Present Value2"
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
        # self.createParameter("quartile", INT)
        # self.quartile = 2


    def init(self):

        # self.__rwht_option = ViewContainer("rwht_option", COMPONENT, READ)
        self.rwht_option = ViewContainer("rwht_option", COMPONENT, READ)

        self.rwht_option.addAttribute("year", Attribute.INT, READ)
        self.rwht_option.addAttribute("volume", Attribute.DOUBLE, READ)
        self.rwht_option.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
        # self.rwht_option.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
        self.rwht_option.addAttribute("price", Attribute.DOUBLE, READ)
        self.rwht_option.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)

        # self.rwht_option.addAttribute("cost_factor", Attribute.DOUBLE, READ)

        self.rwht_option.addAttribute("pv_total_costs_indoor", Attribute.DOUBLE, WRITE)
        self.rwht_option.addAttribute("pv_total_costs_outdoor", Attribute.DOUBLE, WRITE)

        self.rwht_option.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
        self.rwht_option.addAttribute("pv_outdoor_saving", Attribute.DOUBLE, WRITE)

        self.rwht_option.addAttribute("pv_indoor", Attribute.DOUBLE, WRITE)
        self.rwht_option.addAttribute("pv_outdoor", Attribute.DOUBLE, WRITE)

        # self.__rwht.addAttribute("quartile", Attribute.INT, WRITE)

        self.registerViewContainers([self.rwht_option])

    """
    Data Manipulation Process (DMP)
    """

    def run(self):
        # Data Stream Manipulation

        self.rwht_option.reset_reading()

        for r in self.rwht_option:

            construction_cost_indoor_db = {
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
            construction_cost_outdoor_db = {
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
            years = []

            discount_factor = []
            for y in xrange(1, 21, 1):
                years.append(y)
                discount_factor.append(1. / (1. + discount_rate) ** (y - 1))

            # year = r.GetFieldAsInteger("year")
            # volume = r.GetFieldAsDouble("volume")
            # price = r.GetFieldAsDouble("price")
            # f = r.GetFieldAsDouble("cost_factor")
            def construction_costs_indoor(year, size):
                """
                Returns construction costs based on the tank size
                :param size:
                :return:
                """

                try:
                    return construction_cost_indoor_db[year][int(size)]
                except:
                    raise LookupError("No such tank found")

            def construction_costs_outdoor(year, size):
                """
                Returns construction costs based on the tank size
                :param size:
                :return:
                """
                try:
                    return construction_cost_outdoor_db[year][int(size)]
                except:
                    raise LookupError("No such tank found")

            def maintenance_costs():
                maintenance_cost = []
                for y in years:
                    maintenance_cost.append(20.)

                discount_maintenance_cost = [d * m for d, m in zip(discount_factor, maintenance_cost)]

                return sum(discount_maintenance_cost)

            def pv_total_costs_indoor_fun(year, volume):

                try:
                    return construction_costs_indoor(year, volume) + maintenance_costs()
                except (LookupError):
                    raise ValueError("can't calculate total costs")

            def pv_total_costs_outdoor_fun(year, volume):
                try:
                    return construction_costs_outdoor(year, volume) + maintenance_costs()
                except (LookupError):
                    raise ValueError("can't calculate total costs")

            def pv_non_potable_saving_fun(annual_water_savings, price):
                indoor_water_price = []

                for y in years:
                    indoor_water_price.append(price)

                discount_non_potable_savings = [d * m * annual_water_savings for d, m in
                                                zip(discount_factor, indoor_water_price)]

                return sum(discount_non_potable_savings)

            def pv_outdoor_saving_fun(outdoor_water_savings, price):
                indoor_water_price = []

                for y in years:
                    # indoor_water_price.append(2.5)
                    indoor_water_price.append(price)

                discount_outdoor_savings = [d * m * outdoor_water_savings for d, m in
                                            zip(discount_factor, indoor_water_price)]

                return sum(discount_outdoor_savings)
            # Calculate PV for indoor use
            pv_total_costs_indoor = pv_total_costs_indoor_fun(r.GetFieldAsInteger("year"), r.GetFieldAsDouble("volume"))
            # pv_non_potable_saving = pv_non_potable_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")*out_factor+r.GetFieldAsDouble("non_potable_savings")*in_factor), p)
            pv_non_potable_saving = pv_non_potable_saving_fun(
                r.GetFieldAsDouble("annual_water_savings"), r.GetFieldAsDouble("price"))
            pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
            r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
            r.SetField("pv_non_potable_saving", pv_non_potable_saving)
            r.SetField("pv_indoor", pv_indoor)

            # Calculate PV for outdoor use
            pv_total_costs_outdoor = pv_total_costs_outdoor_fun(r.GetFieldAsInteger("year"), r.GetFieldAsDouble("volume"))
            # pv_outdoor_saving = pv_outdoor_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")*out_factor), p)
            pv_outdoor_saving = pv_outdoor_saving_fun(r.GetFieldAsDouble("outdoor_water_savings"), r.GetFieldAsDouble("price"))
            pv_outdoor = pv_outdoor_saving - pv_total_costs_outdoor
            r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
            r.SetField("pv_outdoor_saving", pv_outdoor_saving)
            r.SetField("pv_outdoor", pv_outdoor)


        self.rwht_option.finalise()
