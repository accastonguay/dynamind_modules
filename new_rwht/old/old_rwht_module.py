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
            self.rwht_option.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("price", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)

            # self.rwht_option.addAttribute("cost_factor", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("indoor_factor", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("outdoor_factor", Attribute.DOUBLE, READ)

            self.rwht_option.addAttribute("pv_total_costs_indoor", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_total_costs_outdoor", Attribute.DOUBLE, WRITE)

            self.rwht_option.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_outdoor_saving", Attribute.DOUBLE, WRITE)

            self.rwht_option.addAttribute("pv_indoor", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_outdoor", Attribute.DOUBLE, WRITE)



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


            self.rwht_option.reset_reading()

            for r in self.rwht_option:

                y = r.GetFieldAsInteger("year")
                v = r.GetFieldAsDouble("volume")
                p = r.GetFieldAsDouble("price")
                # f = r.GetFieldAsDouble("cost_factor")

                # print 'factor ' + str(f)
                # print 'type ' + str(type(f))
                # print 'year ' + str(y)
                # print 'type ' + str(type(y))
                # print 'volume ' + str(v)
                # print 'type ' + str(type(v))
                # print 'price ' + str(p)
                # print 'type ' + str(type(p))
                # print 'quartile ' + str(self.quartile)
                # print 'type ' + str(type(self.quartile))

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
                    # print 'factor' + str(f)
                    # print 'type' + str(type(f))

                    # if f == 0.2:
                    #
                    #     construction_cost_outdoor_db = {
                    #         2000: {2: 818, 10: 1263, 5: 1226},
                    #         2001: {2: 854, 10: 1319, 5: 1280},
                    #         2002: {2: 880, 10: 1359, 5: 1319},
                    #         2003: {2: 905, 10: 1398, 5: 1356},
                    #         2004: {2: 923, 10: 1426, 5: 1383},
                    #         2005: {2: 946, 10: 1461, 5: 1417},
                    #         2006: {2: 976, 10: 1508, 5: 1463},
                    #         2007: {2: 999, 10: 1543, 5: 1497},
                    #         2008: {2: 1041, 10: 1608, 5: 1560},
                    #         2009: {2: 1055, 10: 1631, 5: 1582},
                    #         2010: {2: 1088, 10: 1681, 5: 1631},
                    #         2011: {2: 1126, 10: 1739, 5: 1687},
                    #         2012: {2: 1144, 10: 1767, 5: 1714},
                    #         2013: {2: 1172, 10: 1811, 5: 1757},
                    #         2014: {2: 1199, 10: 1853, 5: 1798},
                    #         2015: {2: 1216, 10: 1879, 5: 1823}}
                    #
                    #
                    # elif f == 0.4:
                    #     construction_cost_outdoor_db = {
                    #         2000: {2: 1010, 10: 1456, 5: 1418},
                    #         2001: {2: 1055, 10: 1520, 5: 1481},
                    #         2002: {2: 1087, 10: 1566, 5: 1526},
                    #         2003: {2: 1118, 10: 1611, 5: 1569},
                    #         2004: {2: 1140, 10: 1643, 5: 1601},
                    #         2005: {2: 1168, 10: 1683, 5: 1640},
                    #         2006: {2: 1206, 10: 1738, 5: 1693},
                    #         2007: {2: 1234, 10: 1778, 5: 1732},
                    #         2008: {2: 1285, 10: 1853, 5: 1805},
                    #         2009: {2: 1304, 10: 1879, 5: 1830},
                    #         2010: {2: 1344, 10: 1937, 5: 1887},
                    #         2011: {2: 1390, 10: 2004, 5: 1952},
                    #         2012: {2: 1413, 10: 2036, 5: 1984},
                    #         2013: {2: 1448, 10: 2087, 5: 2033},
                    #         2014: {2: 1481, 10: 2135, 5: 2080},
                    #         2015: {2: 1502, 10: 2165, 5: 2109}}
                    #
                    #
                    # elif f == 0.6:
                    #     construction_cost_outdoor_db = {
                    #         2000: {2: 1202, 10: 1648, 5: 1610},
                    #         2001: {2: 1256, 10: 1721, 5: 1682},
                    #         2002: {2: 1294, 10: 1773, 5: 1733},
                    #         2003: {2: 1330, 10: 1824, 5: 1782},
                    #         2004: {2: 1357, 10: 1860, 5: 1818},
                    #         2005: {2: 1390, 10: 1906, 5: 1862},
                    #         2006: {2: 1435, 10: 1967, 5: 1922},
                    #         2007: {2: 1469, 10: 2013, 5: 1967},
                    #         2008: {2: 1530, 10: 2098, 5: 2050},
                    #         2009: {2: 1552, 10: 2127, 5: 2079},
                    #         2010: {2: 1600, 10: 2193, 5: 2143},
                    #         2011: {2: 1655, 10: 2269, 5: 2217},
                    #         2012: {2: 1682, 10: 2305, 5: 2253},
                    #         2013: {2: 1723, 10: 2362, 5: 2308},
                    #         2014: {2: 1763, 10: 2417, 5: 2362},
                    #         2015: {2: 1788, 10: 2451, 5: 2395}}
                    #
                    #
                    # elif f == 0.8:
                    #     construction_cost_outdoor_db = {
                    #         2000: {2: 1395, 10: 1840, 5: 1803},
                    #         2001: {2: 1456, 10: 1922, 5: 1882},
                    #         2002: {2: 1501, 10: 1980, 5: 1940},
                    #         2003: {2: 1543, 10: 2036, 5: 1995},
                    #         2004: {2: 1574, 10: 2077, 5: 2035},
                    #         2005: {2: 1613, 10: 2128, 5: 2085},
                    #         2006: {2: 1665, 10: 2197, 5: 2152},
                    #         2007: {2: 1704, 10: 2248, 5: 2202},
                    #         2008: {2: 1775, 10: 2342, 5: 2294},
                    #         2009: {2: 1800, 10: 2375, 5: 2327},
                    #         2010: {2: 1856, 10: 2449, 5: 2399},
                    #         2011: {2: 1920, 10: 2534, 5: 2482},
                    #         2012: {2: 1951, 10: 2574, 5: 2522},
                    #         2013: {2: 1999, 10: 2638, 5: 2584},
                    #         2014: {2: 2046, 10: 2699, 5: 2644},
                    #         2015: {2: 2075, 10: 2737, 5: 2681}}




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
                for yr in xrange(1, 21, 1):
                    years.append(yr)
                    discount_factor.append(1. / (1. + discount_rate) ** (yr - 1))

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
                    for yrs in years:
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

                def pv_outdoor_saving_fun(outdoor_water_savings, price):
                    indoor_water_price = []

                    for y in years:
                        # indoor_water_price.append(2.5)
                        indoor_water_price.append(price)

                    discount_outdoor_savings = [d * m * outdoor_water_savings for d, m in
                                                zip(discount_factor, indoor_water_price)]

                    return sum(discount_outdoor_savings)

                # out_factor = r.GetFieldAsDouble("outdoor_factor")
                # in_factor = r.GetFieldAsDouble("indoor_factor")

                # Calculate PV for indoor use
                # print 'year is: ',y
                pv_total_costs_indoor = pv_total_costs_indoor_fun(y, v)
                # pv_non_potable_saving = pv_non_potable_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")*out_factor+r.GetFieldAsDouble("non_potable_savings")*in_factor), p)
                pv_non_potable_saving = pv_non_potable_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")+r.GetFieldAsDouble("non_potable_savings")), p)
                pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
                r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
                r.SetField("pv_non_potable_saving", pv_non_potable_saving)
                r.SetField("pv_indoor", pv_indoor)

                # Calculate PV for outdoor use
                pv_total_costs_outdoor = pv_total_costs_outdoor_fun(y, v)
                # pv_outdoor_saving = pv_outdoor_saving_fun((r.GetFieldAsDouble("outdoor_water_savings")*out_factor), p)
                pv_outdoor_saving = pv_outdoor_saving_fun(r.GetFieldAsDouble("outdoor_water_savings"), p)
                pv_outdoor = pv_outdoor_saving - pv_total_costs_outdoor
                r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
                r.SetField("pv_outdoor_saving", pv_outdoor_saving)
                r.SetField("pv_outdoor", pv_outdoor)




            self.rwht_option.finalise()
