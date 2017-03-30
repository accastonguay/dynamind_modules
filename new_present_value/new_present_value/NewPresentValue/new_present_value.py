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
        self.rwht_view_name = "rwht_option"

        self.createParameter("source_costs", STRING)
        self.source_costs = "tam"

        self.createParameter("source_wtp", STRING)
        self.source_wtp = "hensher"



        self.createParameter("tank_life", DOUBLE)
        self.tank_life = 20

        self.createParameter("discount_rate", DOUBLE)
        self.discount_rate = 0.05

        self.__years = []
        self.__discount_factor = []
        for y in xrange(1, int(self.tank_life) + 1, 1):
            self.__years.append(y)
            self.__discount_factor.append(1. / (1. + self.discount_rate) ** (y - 1))

        self.__cpi = {2005: 83.8, 2006: 86.6, 2007: 89.1, 2008: 92.4, 2009: 94.3, 2010: 96.9, 2011: 99.8, 2012: 102.0, 2013: 104.8,
         2014: 106.6}
        self.__cpi_energy = {2005: 56.2, 2006: 56.2, 2007: 57.6, 2008: 67.1, 2009: 73.9, 2010: 88.9, 2011: 98.7, 2012: 104.0, 2013: 125.4,
         2014: 128.5}

        self.__fixed_water_charge = {2005: 56.865, 2006: 59.395, 2007: 61.895, 2008: 69.335, 2009: 82.47, 2010: 114.7, 2011: 130.13, 2012: 120.26,
                      2013: 148.08, 2014: 171.49}

        self.__fixed_sewer_charge = {2005: 138.895,
                                     2006: 145.085,
                                     2007: 151.195,
                                     2008:  169.375,
                                     2009: 205.72,
                                     2010: 250.55,
                                     2011:  297.85,
                                     2012: 321.5,
                                     2013: 332.7,
                                     2014: 346.19}

        self.__fixed_drainage_charge = {2005: 51,
                                        2006: 53.18,
                                        2007: 55.38,
                                        2008: 59.24,
                                        2009: 64.58,
                                        2010: 69.955,
                                        2011: 73.42875,
                                        2012: 77.50125,
                                        2013: 85.0475,
                                        2014: 91.06}

        self.__park_charge = {2005: 48,
                              2006: 50,
                              2007: 52.42,
                              2008: 54.65,
                              2009: 58.90,
                              2010: 63.03,
                              2011: 64.42,
                              2012: 65.93,
                              2013: 67.61,
                              2014: 69.54}

        self.createParameter("maintenance_cost", DOUBLE)
        self.maintenance_cost = 20

        self.createParameter("pump_cost", DOUBLE)
        self.pump_cost = 355

        self.createParameter("plumbing_cost", DOUBLE)
        self.plumbing_cost = 730

        self.createParameter("installation_cost", DOUBLE)
        self.installation_cost = 550

        self.createParameter("energy_use", DOUBLE)
        self.energy_use = 1.4

        # self.__maintenance_costs={2005: 17.3, 2006: 17.87, 2007: 18.39, 2008: 19.07, 2009: 19.46, 2010: 20.0,
        # 2011: 20.6, 2012: 21.05, 2013: 21.63, 2014: 22.0}

        self.createParameter("energy_cost", DOUBLE)
        self.energy_cost = 0.12

        self.createParameter("add_cost_coeff", DOUBLE)
        self.add_cost_coeff = 1

        self.createParameter("const_cost2", DOUBLE)
        self.const_cost2 = 890

        self.createParameter("const_cost5", DOUBLE)
        self.const_cost5 = 1350

        self.createParameter("const_cost10", DOUBLE)
        self.const_cost10 = 1925
        # self.__energy_cost = {2005: 0.12, 2006: 0.12, 2007: 0.12, 2008: 0.14, 2009: 0.16, 2010: 0.19, 2011: 0.21, 2012: 0.22, 2013: 0.27, 2014: 0.28, 2015: 0.26}

        # construction costs from internet as of 2010
        if self.source_costs == "internet":
            self.__construction_cost_db = {2: 832, 10: 1425, 5: 1375}
        # construction costs from Tam et al 2010 as of 2010
        elif self.source_costs == "tam":
            self.__construction_cost_db = {2: self.const_cost2, 10: self.const_cost10, 5: self.const_cost5}

    def init(self):

        self.__rwht = ViewContainer(self.rwht_view_name, COMPONENT, READ)

        self.__rwht.addAttribute("year", Attribute.INT, READ)
        self.__rwht.addAttribute("volume", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("price", Attribute.DOUBLE, READ)
        # self.__rwht.addAttribute("wtp_lata", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("garden", Attribute.INT, READ)
        self.__rwht.addAttribute("wtp_hensher", Attribute.INT, READ)
        self.__rwht.addAttribute("water_usage_charge", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("sewer_usage_charge", Attribute.DOUBLE, READ)


        self.__rwht.addAttribute("outdoor_water_savings", Attribute.DOUBLE, READ)
        self.__rwht.addAttribute("annual_water_savings", Attribute.DOUBLE, READ)

        self.__rwht.addAttribute("const_cost_indoor", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("const_cost_outdoor", Attribute.DOUBLE, WRITE)

        self.__rwht.addAttribute("pv_total_costs_indoor", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_total_costs_outdoor", Attribute.DOUBLE, WRITE)

        self.__rwht.addAttribute("pv_non_potable_saving", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_outdoor_saving", Attribute.DOUBLE, WRITE)

        self.__rwht.addAttribute("pv_indoor", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pv_outdoor", Attribute.DOUBLE, WRITE)
        # self.__rwht.addAttribute("source_costs", Attribute.STRING, WRITE)
        self.__rwht.addAttribute("source_wtp", Attribute.STRING, WRITE)
        self.__rwht.addAttribute("discount_rate", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("tank_life", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("plumbing_cost", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("installation_cost", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("pump_cost", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("maintenance_cost", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("add_cost_coeff", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("wtp", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("water_supply_bill", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("sewer_bill", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("drainage_bill", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("park_bill", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("total_water_bill", Attribute.DOUBLE, WRITE)

        self.__rwht.addAttribute("const_cost2", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("const_cost5", Attribute.DOUBLE, WRITE)
        self.__rwht.addAttribute("const_cost10", Attribute.DOUBLE, WRITE)

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
            initial_cost = self.__construction_cost_db[int(size)] + self.installation_cost + self.plumbing_cost + self.pump_cost
            return initial_cost*self.__cpi[year]/self.__cpi[2010]
        except:
            raise LookupError("No such tank found")

    def construction_costs_outdoor(self,year, size):
        """
        Returns construction costs based on the tank size
        :param size:
        :return:
        """
        try:
            initial_cost = self.__construction_cost_db[int(size)] + (self.installation_cost + self.plumbing_cost)*self.add_cost_coeff
            return initial_cost * self.__cpi[year] / self.__cpi[2010]
        except:
            raise LookupError("No such tank found")

    def maintenance_costs_indoor(self, annual_savings, year):
        mcost = self.maintenance_cost* self.__cpi[year] / self.__cpi[2010]
        ecost = self.energy_cost* self.__cpi_energy[year] / self.__cpi_energy[2005]
        maintenance_cost = []
        opex = []
        savings = []
        for y in self.__years:
            maintenance_cost.append(mcost)
            opex.append(ecost)
            savings.append(annual_savings)

        discount_maintenance_cost = [(d * m)+(s * self.energy_use * o * d) for d, m, s, o in zip(self.__discount_factor, maintenance_cost, savings, opex)]

        return sum(discount_maintenance_cost)

    def maintenance_costs_outdoor(self, year):
        mcost = self.maintenance_cost * self.__cpi[year] / self.__cpi[2010]
        # opex = []
        # savings = []
        maintenance_cost = []
        for y in self.__years:
            maintenance_cost.append(mcost)
            # opex.append(self.__operation_costs[year])
            # savings.append(outdoor_savings)

        # discount_maintenance_cost = [(d * m)+(s * o * d) for d, m, s, o in zip(self.__discount_factor, maintenance_cost, savings,opex)]
        discount_maintenance_cost = [(d * m) for d, m in zip(self.__discount_factor, maintenance_cost)]

        return sum(discount_maintenance_cost)

    def pv_total_costs_indoor_fun(self, year, volume, annual_savings):
        pump_future_value = self.pump_cost * 1. / (1. + self.discount_rate) ** (10)
        try:
            return self.construction_costs_indoor(year, volume) + self.maintenance_costs_indoor(annual_savings, year)+pump_future_value
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_total_costs_outdoor_fun(self, year, volume):
        try:
            return self.construction_costs_outdoor(year, volume) + self.maintenance_costs_outdoor(year)
        except (LookupError):
            raise ValueError("can't calculate total costs")

    def pv_non_potable_saving_fun(self, annual_water_savings, price,wtp, garden):
        indoor_water_price = []
        wtp_list = []
        for y in self.__years:
            indoor_water_price.append(price)
            wtp_list.append(wtp)

        if garden == 1:

            discount_non_potable_savings = [(d * p * annual_water_savings) + (w*d)  for d, p, w in
                                            zip(self.__discount_factor, indoor_water_price,wtp_list)]

            return sum(discount_non_potable_savings)
        else:
            discount_non_potable_savings = [(d * p * annual_water_savings) for d, p in
                                            zip(self.__discount_factor, indoor_water_price)]

            return sum(discount_non_potable_savings)

    def pv_outdoor_saving_fun(self, outdoor_water_savings, price, wtp):
        indoor_water_price = []
        wtp_list = []
        for y in self.__years:
            indoor_water_price.append(price)
            wtp_list.append(wtp)

        discount_outdoor_savings = [(d * p * outdoor_water_savings) + (w*d) for d, p, w in
                                    zip(self.__discount_factor, indoor_water_price, wtp_list)]

        return sum(discount_outdoor_savings)

    def run(self):
        # Data Stream Manipulation

        self.__rwht.reset_reading()

        for r in self.__rwht:

            year = r.GetFieldAsInteger("year")
            volume = r.GetFieldAsDouble("volume")
            price = r.GetFieldAsDouble("price")
            annual_water_savings = r.GetFieldAsDouble("annual_water_savings")
            outdoor_water_savings = r.GetFieldAsDouble("outdoor_water_savings")
            # wtp = r.GetFieldAsDouble("wtp")
            garden = r.GetFieldAsInteger("garden")

            if self.source_wtp == "hensher":
                new_wtp = r.GetFieldAsDouble("wtp_hensher")
                water_supply_bill = r.GetFieldAsDouble("water_usage_charge")+self.__fixed_water_charge[year]
                sewer_bill=  r.GetFieldAsDouble("sewer_usage_charge") + self.__fixed_sewer_charge[year]
                drainage_bill = self.__fixed_drainage_charge[year]
                park_bill = self.__park_charge[year]
                total_water_bill = water_supply_bill + sewer_bill + drainage_bill + park_bill
                wtp = new_wtp*total_water_bill
            # elif self.source_wtp == "lata":
            #     wtp = r.GetFieldAsDouble("wtp_lata")



            # Calculate PV for indoor use
            pv_total_costs_indoor = self.pv_total_costs_indoor_fun(year, volume, annual_water_savings)
            pv_non_potable_saving = self.pv_non_potable_saving_fun(annual_water_savings, price, wtp, garden)
            pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
            r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
            r.SetField("pv_non_potable_saving", pv_non_potable_saving)
            r.SetField("pv_indoor", pv_indoor)
            r.SetField("const_cost_indoor", self.construction_costs_indoor(year, volume))

            # Calculate PV for outdoor use
            pv_total_costs_outdoor = self.pv_total_costs_outdoor_fun(year, volume)
            pv_outdoor_saving = self.pv_outdoor_saving_fun(outdoor_water_savings, price, wtp)
            pv_outdoor = pv_outdoor_saving - pv_total_costs_outdoor
            r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
            r.SetField("pv_outdoor_saving", pv_outdoor_saving)
            r.SetField("pv_outdoor", pv_outdoor)
            r.SetField("const_cost_outdoor", self.construction_costs_outdoor(year, volume))

            r.SetField("source_wtp", self.source_wtp)

            r.SetField("discount_rate", self.discount_rate)
            r.SetField("tank_life", self.tank_life)
            r.SetField("plumbing_cost", self.plumbing_cost)
            r.SetField("installation_cost", self.installation_cost)
            r.SetField("pump_cost", self.pump_cost)
            r.SetField("maintenance_cost", self.maintenance_cost)
            r.SetField("add_cost_coeff", self.add_cost_coeff)
            r.SetField("wtp", wtp)
            r.SetField("water_supply_bill", water_supply_bill)
            r.SetField("sewer_bill", sewer_bill)
            r.SetField("drainage_bill", drainage_bill)
            r.SetField("park_bill", park_bill)
            r.SetField("total_water_bill", total_water_bill)
            r.SetField("const_cost2", self.const_cost2)
            r.SetField("const_cost5", self.const_cost5)
            r.SetField("const_cost10", self.const_cost10)


        self.__rwht.finalise()
