__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
import numpy as np

class NewRwhtModule(Module):
        display_name = "New rwht module"
        group_name = "test"
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

            self.rwht_option.addAttribute("year", Attribute.INT, READ)
            self.rwht_option.addAttribute("volume", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("price", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("pv_total_costs", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("pv", Attribute.DOUBLE, WRITE)


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
            # views.append(self.city_council)
            views.append(self.rwht_option)
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

            construction_cost_db = {
            1999: {2: 1674.02, 5: 2002.05, 10: 2347.90},
            2000: {2: 1770.92, 5: 2117.94, 10: 2483.82},
            2001: {2: 1826.64, 5: 2184.58, 10: 2561.97},
            2002: {2: 1879.94, 5: 2248.32, 10: 2636.72},
            2003: {2: 1925.97, 5: 2303.37, 10: 2701.28},
            2004: {2: 1974.42, 5: 2361.31, 10: 2769.23},
            2005: {2: 2030.14, 5: 2427.95, 10: 2847.38},
            2006: {2: 2097.97, 5: 2509.08, 10: 2942.52},
            2007: {2: 2158.54, 5: 2581.51, 10: 3027.47},
            2008: {2: 2238.48, 5: 2677.12, 10: 3139.60},
            2009: {2: 2284.51, 5: 2732.17, 10: 3204.16},
            2010: {2: 2347.50, 5: 2807.50, 10: 3292.50},
            2011: {2: 2417.76, 5: 2891.52, 10: 3391.04},
            2012: {2: 2418.68, 5: 2892.62, 10: 3392.33},
            2013: {2: 2538.89, 5: 3036.39, 10: 3560.93},
            2014: {2: 2582.49, 5: 3088.54, 10: 3622.09},
            2015: {2: 2626.10, 5: 3140.69, 10: 3683.25}}
            discount_rate = 0.05
            years = []

            discount_factor = []
            for y in xrange(1, 21, 1):
                years.append(y)
                discount_factor.append(1. / (1. + discount_rate) ** (y - 1))

            def construction_costs(year, size):
                """
                Returns construction costs based on the tank size
                :param size:
                :return:
                """
                try:
                    return construction_cost_db[year][int(size)]
                except:
                    raise LookupError("No such tank found")

            def maintenance_costs():
                maintenance_cost = []
                for y in years:
                    maintenance_cost.append(20.)

                discount_maintenance_cost = [d * m for d, m in zip(discount_factor, maintenance_cost)]

                return sum(discount_maintenance_cost)

            def pv_total_costs_fun(year, volume):
                try:
                    return construction_costs(year, volume) + maintenance_costs()
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

            self.rwht_option.reset_reading()
            for r in self.rwht_option:
                y = r.GetFieldAsInteger("year")
                v = r.GetFieldAsDouble("volume")
                p = r.GetFieldAsDouble("price")
                # print "Type is : ", type(v), type(y), type(pv_total_costs)
                pv_total_costs = pv_total_costs_fun(y, v)
                pv_non_potable_saving = pv_non_potable_saving_fun(r.GetFieldAsDouble("annual_water_savings"), p)

                pv = pv_non_potable_saving - pv_total_costs
                r.SetField("pv_total_costs", pv_total_costs)
                r.SetField("pv_non_potable_saving", pv_non_potable_saving)
                r.SetField("pv", pv)



            self.rwht_option.finalise()
            # self.city.finalise()