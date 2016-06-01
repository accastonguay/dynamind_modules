__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
import numpy as np

class NewRwhtModule(Module):
        display_name = "New rwht module"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("rule", INT)
            self.rule = 1


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

            #print self.my_parameter

            #Data Stream Manipulation

            #print self.my_parameter

            # construction_cost_db = {
            # 1999: {2: 1674.02, 5: 2002.05, 10: 2347.90},
            # 2000: {2: 1770.92, 5: 2117.94, 10: 2483.82},
            # 2001: {2: 1826.64, 5: 2184.58, 10: 2561.97},
            # 2002: {2: 1879.94, 5: 2248.32, 10: 2636.72},
            # 2003: {2: 1925.97, 5: 2303.37, 10: 2701.28},
            # 2004: {2: 1974.42, 5: 2361.31, 10: 2769.23},
            # 2005: {2: 2030.14, 5: 2427.95, 10: 2847.38},
            # 2006: {2: 2097.97, 5: 2509.08, 10: 2942.52},
            # 2007: {2: 2158.54, 5: 2581.51, 10: 3027.47},
            # 2008: {2: 2238.48, 5: 2677.12, 10: 3139.60},
            # 2009: {2: 2284.51, 5: 2732.17, 10: 3204.16},
            # 2010: {2: 2347.50, 5: 2807.50, 10: 3292.50},
            # 2011: {2: 2417.76, 5: 2891.52, 10: 3391.04},
            # 2012: {2: 2418.68, 5: 2892.62, 10: 3392.33},
            # 2013: {2: 2538.89, 5: 3036.39, 10: 3560.93},
            # 2014: {2: 2582.49, 5: 3088.54, 10: 3622.09},
            # 2015: {2: 2626.10, 5: 3140.69, 10: 3683.25}}

            construction_cost_indoor_db = {
            1999 :{2: 1800.59, 10: 2538.66, 5: 2128.62},
            2000 :{2: 1904.82, 10: 2685.61, 5: 2251.84},
            2001 :{2: 1964.76, 10: 2770.11, 5: 2322.69},
            2002 :{2: 2022.08, 10: 2850.94, 5: 2390.46},
            2003 :{2: 2071.59, 10: 2920.74, 5: 2448.99},
            2004 :{2: 2123.71, 10: 2994.22, 5: 2510.6},
            2005 :{2: 2183.64, 10: 3078.72, 5: 2581.46},
            2006 :{2: 2256.6, 10: 3181.59, 5: 2667.71},
            2007 :{2: 2321.75, 10: 3273.44, 5: 2744.72},
            2008 :{2: 2407.74, 10: 3394.67, 5: 2846.38},
            2009 :{2: 2457.25, 10: 3464.48, 5: 2904.91},
            2010 :{2: 2525.0, 10: 3560.0, 5: 2985.0},
            2011 :{2: 2600.57, 10: 3666.54, 5: 3074.33},
            2012 :{2: 2657.89, 10: 3747.37, 5: 3142.11},
            2013 :{2: 2730.86, 10: 3850.24, 5: 3228.36},
            2014 :{2: 2777.76, 10: 3916.37, 5: 3283.81},
            2015 :{2: 2824.66, 10: 3982.5, 5: 3339.26}}


            construction_cost_outdoor_db = {
            1999 :{2: 1547.44, 10: 2157.15, 5: 1875.47},
            2000 :{2: 1637.02, 10: 2282.02, 5: 1984.04},
            2001 :{2: 1688.52, 10: 2353.82, 5: 2046.46},
            2002 :{2: 1737.79, 10: 2422.5, 5: 2106.17},
            2003 :{2: 1780.34, 10: 2481.81, 5: 2157.74},
            2004 :{2: 1825.13, 10: 2544.25, 5: 2212.02},
            2005 :{2: 1876.64, 10: 2616.05, 5: 2274.45},
            2006 :{2: 1939.34, 10: 2703.46, 5: 2350.44},
            2007 :{2: 1995.33, 10: 2781.5, 5: 2418.3},
            2008 :{2: 2069.23, 10: 2884.52, 5: 2507.86},
            2009 :{2: 2111.78, 10: 2943.83, 5: 2559.43},
            2010 :{2: 2170.0, 10: 3025.0, 5: 2630.0},
            2011 :{2: 2234.94, 10: 3115.53, 5: 2708.71},
            2012 :{2: 2284.21, 10: 3184.21, 5: 2768.42},
            2013 :{2: 2346.91, 10: 3271.62, 5: 2844.42},
            2014 :{2: 2387.22, 10: 3327.81, 5: 2893.27},
            2015 :{2: 2427.53, 10: 3384.0, 5: 2942.13}}

    
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
