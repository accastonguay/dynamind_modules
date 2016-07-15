__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
import numpy as np

class NewRwhtModule(Module):
        display_name = "rwht choice"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("quartile", INT)
            self.quartile = 2


            self.rwht_option = ViewContainer("rwht_option", COMPONENT, READ)
            # self.rwht_option.addAttribute("plumbed", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("year", Attribute.INT, READ)
            self.rwht_option.addAttribute("volume", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("price", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)

            self.rwht_option.addAttribute("pv_total_costs_indoor", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_total_costs_outdoor", Attribute.DOUBLE, WRITE)

            self.rwht_option.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_outdoor_potable_saving", Attribute.DOUBLE, WRITE)

            self.rwht_option.addAttribute("pv_indoor", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_outdoor", Attribute.DOUBLE, WRITE)


        #
        # self.__rwht = ViewContainer(self.rwht_view_name, COMPONENT, READ)
        # self.__rwht.addAttribute("volume", Attribute.DOUBLE, READ)
        # self.__rwht.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
        # self.__rwht.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
        # self.__rwht.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)
        # self.__rwht.addAttribute("pv_total_costs", Attribute.DOUBLE, WRITE)
        # self.__rwht.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
        # self.__rwht.addAttribute("pv", Attribute.DOUBLE, WRITE)
        #
        # self.registerViewContainers([self.__rwht])

            #Compile views
            views = []
            views.append(self.rwht_option)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """


        def run(self):
            #Data Stream Manipulation

            if self.quartile == 1:
                construction_cost_indoor_db = {
                    2000: {2: 1707, 10: 2203, 5: 1894},
                    2001: {2: 1783, 10: 2301, 5: 1906},
                    2002: {2: 1822, 10: 2371, 5: 2038},
                    2003: {2: 1889, 10: 2438, 5: 2046},
                    2004: {2: 1927, 10: 2487, 5: 2138},
                    2005: {2: 1961, 10: 2548, 5: 2145},
                    2006: {2: 2038, 10: 2630, 5: 2261},
                    2007: {2: 2086, 10: 2691, 5: 2269},
                    2008: {2: 2149, 10: 2804, 5: 2411},
                    2009: {2: 2204, 10: 2844, 5: 2415},
                    2010: {2: 2273, 10: 2932, 5: 2521},
                    2011: {2: 2329, 10: 3033, 5: 2533},
                    2012: {2: 2388, 10: 3082, 5: 2649},
                    2013: {2: 2448, 10: 3158, 5: 2659},
                    2014: {2: 2488, 10: 3231, 5: 2778},
                    2015: {2: 2540, 10: 3277, 5: 2783}}


                construction_cost_outdoor_db = {
                    2000: {2: 1441, 10: 1936, 5: 1627},
                    2001: {2: 1504, 10: 2022, 5: 1699},
                    2002: {2: 1535, 10: 2084, 5: 1751},
                    2003: {2: 1594, 10: 2143, 5: 1801},
                    2004: {2: 1626, 10: 2186, 5: 1837},
                    2005: {2: 1653, 10: 2240, 5: 1882},
                    2006: {2: 1720, 10: 2312, 5: 1943},
                    2007: {2: 1760, 10: 2366, 5: 1988},
                    2008: {2: 1809, 10: 2465, 5: 2071},
                    2009: {2: 1860, 10: 2500, 5: 2100},
                    2010: {2: 1918, 10: 2577, 5: 2166},
                    2011: {2: 1961, 10: 2666, 5: 2240},
                    2012: {2: 2015, 10: 2709, 5: 2276},
                    2013: {2: 2065, 10: 2776, 5: 2333},
                    2014: {2: 2097, 10: 2840, 5: 2387},
                    2015: {2: 2143, 10: 2881, 5: 2421}}

            elif self.quartile == 2:
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
                    2000: {2: 1587, 10: 2033, 5: 1995},
                    2001: {2: 1657, 10: 2123, 5: 2083},
                    2002: {2: 1708, 10: 2187, 5: 2147},
                    2003: {2: 1756, 10: 2249, 5: 2208},
                    2004: {2: 1791, 10: 2294, 5: 2252},
                    2005: {2: 1835, 10: 2351, 5: 2307},
                    2006: {2: 1895, 10: 2427, 5: 2382},
                    2007: {2: 1939, 10: 2483, 5: 2437},
                    2008: {2: 2020, 10: 2587, 5: 2539},
                    2009: {2: 2048, 10: 2624, 5: 2575},
                    2010: {2: 2112, 10: 2705, 5: 2655},
                    2011: {2: 2185, 10: 2798, 5: 2746},
                    2012: {2: 2220, 10: 2843, 5: 2791},
                    2013: {2: 2275, 10: 2914, 5: 2860},
                    2014: {2: 2328, 10: 2981, 5: 2926},
                    2015: {2: 2361, 10: 3024, 5: 2968}}


            elif self.quartile == 3:
                construction_cost_indoor_db = {
                    2000: {2: 2056, 10: 2394, 5: 2559},
                    2001: {2: 2147, 10: 2500, 5: 2673},
                    2002: {2: 2213, 10: 2576, 5: 2754},
                    2003: {2: 2276, 10: 2649, 5: 2832},
                    2004: {2: 2321, 10: 2702, 5: 2889},
                    2005: {2: 2378, 10: 2769, 5: 2960},
                    2006: {2: 2455, 10: 2858, 5: 3056},
                    2007: {2: 2512, 10: 2925, 5: 3127},
                    2008: {2: 2617, 10: 3047, 5: 3258},
                    2009: {2: 2654, 10: 3090, 5: 3304},
                    2010: {2: 2737, 10: 3187, 5: 3407},
                    2011: {2: 2831, 10: 3296, 5: 3524},
                    2012: {2: 2876, 10: 3349, 5: 3580},
                    2013: {2: 2948, 10: 3432, 5: 3669},
                    2014: {2: 3016, 10: 3512, 5: 3754},
                    2015: {2: 3059, 10: 3561, 5: 3807}}

                construction_cost_outdoor_db = {
                    2000: {2: 1790, 10: 2127, 5: 2293},
                    2001: {2: 1869, 10: 2222, 5: 2394},
                    2002: {2: 1926, 10: 2289, 5: 2467},
                    2003: {2: 1980, 10: 2354, 5: 2537},
                    2004: {2: 2020, 10: 2401, 5: 2588},
                    2005: {2: 2070, 10: 2460, 5: 2652},
                    2006: {2: 2137, 10: 2540, 5: 2737},
                    2007: {2: 2186, 10: 2599, 5: 2801},
                    2008: {2: 2278, 10: 2708, 5: 2918},
                    2009: {2: 2310, 10: 2746, 5: 2960},
                    2010: {2: 2382, 10: 2832, 5: 3052},
                    2011: {2: 2464, 10: 2929, 5: 3156},
                    2012: {2: 2503, 10: 2976, 5: 3207},
                    2013: {2: 2565, 10: 3050, 5: 3287},
                    2014: {2: 2625, 10: 3120, 5: 3363},
                    2015: {2: 2662, 10: 3165, 5: 3411}}


    
            discount_rate = 0.05
            years = []

            discount_factor = []
            for y in xrange(1, 21, 1):
                years.append(y)
                discount_factor.append(1. / (1. + discount_rate) ** (y - 1))

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
                # points = np.array([(2005, 1.17), (2008,  1.62), (2009,  1.85), (2010, 2.1), (2011, 2.36), (2012, 2.11), (2013, 2.59), (2014, 2.55), (2015, 2.62)])
                # # get x and y vectors
                # x = points[:,0]
                # y = points[:,1]
                # # calculate polynomial
                # z = np.polyfit(x, y,3)
                # f = np.poly1d(z)

                for y in years:
                    # indoor_water_price.append(2.5)
                    indoor_water_price.append(price)

                discount_non_potable_savings = [d * m * annual_water_savings for d, m in
                                                zip(discount_factor, indoor_water_price)]

                return sum(discount_non_potable_savings)

            def pv_outdoor_potable_saving_fun(outdoor_water_savings, price):
                indoor_water_price = []

                for y in years:
                    # indoor_water_price.append(2.5)
                    indoor_water_price.append(price)

                discount_outdoor_savings = [d * m * outdoor_water_savings for d, m in
                                                zip(discount_factor, indoor_water_price)]

                return sum(discount_outdoor_savings)

            self.rwht_option.reset_reading()

            for r in self.rwht_option:

                # Calculate PV for indoor use
                y = r.GetFieldAsInteger("year")
                v = r.GetFieldAsDouble("volume")
                p = r.GetFieldAsDouble("price")
                # print "Type is : ", type(v), type(y), type(pv_total_costs)
                pv_total_costs_indoor = pv_total_costs_indoor_fun(y, v)
                pv_non_potable_saving = pv_non_potable_saving_fun(r.GetFieldAsDouble("annual_water_savings"), p)

                pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
                r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
                r.SetField("pv_non_potable_saving", pv_non_potable_saving)
                r.SetField("pv_indoor", pv_indoor)

                # Calculate PV for outdoor use

                pv_total_costs_outdoor = pv_total_costs_outdoor_fun(y, v)
                pv_outdoor_potable_saving = pv_outdoor_potable_saving_fun(r.GetFieldAsDouble("outdoor_water_savings"), p)

                pv_outdoor = pv_outdoor_potable_saving - pv_total_costs_outdoor
                r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
                r.SetField("pv_outdoor_potable_saving", pv_outdoor_potable_saving)
                r.SetField("pv_outdoor", pv_outdoor)




            self.rwht_option.finalise()
