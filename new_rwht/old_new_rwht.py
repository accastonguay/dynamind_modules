"""
@file
@author  Chrisitan Urich <christian.urich@gmail.com>
@version 1.0
@section LICENSE

This file is part of DynaMind
Copyright (C) 2014 Christian Urich

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from pydynamind import *
import numpy as np

class new_rwht(Module):
    display_name = "New rwht"
    group_name = "Economic Evaluation"

    def __init__(self):
        Module.__init__(self)
        self.setIsGDALModule(True)

        self.createParameter("rwht_view_name", STRING)
        self.rwht_view_name = "rwht"

        self.__construction_cost_db = {
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
            # {"melbourne": {2: 2525, 5: 2985, 10: 3560}}
        discount_rate = 0.05
        self.__years = []

        self.__discount_factor = []
        for y in xrange(1, 21, 1):
            self.__years.append(y)
            self.__discount_factor.append(1. / (1. + discount_rate) ** (y - 1))



    def init(self):
        self.__rwht = ViewContainer(self.rwht_view_name, COMPONENT, READ)
        self.__rwht.addAttribute("volume", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("non_potable_savings", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("year", Attribute.INT, READ)
        self.__rwht.addAttribute("pv_total_costs", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv", Attribute.DOUBLE, WRITE)

        self.registerViewContainers([self.__rwht])

    ''' Replace location by year '''

    # def construction_costs(self, location, size):
    #     """
    #     Returns construction costs based on the tank size
    #     :param size:
    #     :return:
    #     """
    #     try:
    #         return self.__construction_cost_db[location][int(size)]
    #     except:
    #         raise LookupError("No such tank found")
    def construction_costs(self, year, size):
        """
        Returns construction costs based on the tank size
        :param size:
        :return:
        """
        try:
            return self.__construction_cost_db[year][int(size)]
        except:
            raise LookupError("No such tank found")

    def maintenance_costs(self):
        maintenance_cost = []
        for y in self.__years:
            maintenance_cost.append(20.)

        discount_maintenance_cost = [d * m for d, m in zip(self.__discount_factor, maintenance_cost)]

        return sum(discount_maintenance_cost)

    ''' Replace location by year '''

    # def pv_total_costs(self, location, volume):
    #     try:
    #         return self.construction_costs(location, volume) + self.maintenance_costs()
    #     except (LookupError):
    #         raise ValueError("can't calculate total costs")

    def pv_total_costs(self, year, volume):
        try:
            return self.construction_costs(year, volume) + self.maintenance_costs()
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_non_potable_saving(self, annual_water_savings, year):
        indoor_water_price = []
        points = np.array([(2005, 1.17), (2008,  1.62), (2009,  1.85), (2010, 2.1), (2011, 2.36), (2012, 2.11), (2013, 2.59), (2014, 2.55), (2015, 2.62)])
        # get x and y vectors
        x = points[:,0]
        y = points[:,1]
        # calculate polynomial
        z = np.polyfit(x, y,3)
        f = np.poly1d(z)

        for y in self.__years:
            # indoor_water_price.append(2.5)
            indoor_water_price.append(f(year))

        discount_non_potable_savings = [d * m * annual_water_savings for d, m in
                                        zip(self.__discount_factor, indoor_water_price)]

        return sum(discount_non_potable_savings)

    def run(self):
        self.__rwht.reset_reading()

        for r in self.__rwht:
            pv_total_costs = self.pv_total_costs(r.GetFieldAsInteger("year"), r.GetFieldAsDouble("volume"))
            pv_non_potable_saving = self.pv_non_potable_saving(r.GetFieldAsDouble("annual_water_savings"), r.GetFieldAsInteger("year"))

            pv = pv_non_potable_saving - pv_total_costs
            r.SetField("pv_total_costs", pv_total_costs)
            r.SetField("pv_non_potable_saving", pv_non_potable_saving)
            r.SetField("pv", pv)

        self.__rwht.finalise()

# if __name__ == "__main__":
#     r = new_rwht()
#     r.init()
#
#     print r.pv_total_costs("melbourne", 2), r.pv_non_potable_saving(50), r.pv_outdoor_savings(31, 1, 4, 20, 40)
#     print r.pv_total_costs("melbourne", 5), r.pv_non_potable_saving(100), r.pv_outdoor_savings(31, 1, 4, 20, 10)
#     print r.pv_total_costs("melbourne", 10), r.pv_non_potable_saving(150), r.pv_outdoor_savings(31, 0, 4, 20, 20)
