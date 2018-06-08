__author__ = 'acharett'

from pydynamind import *
from osgeo import ogr
import random
import math

class Heuristics(Module):
        display_name = "Heuristics"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)

            self.createParameter("lifespan_rg", DOUBLE)
            self.lifespan_rg = 37

            self.createParameter("lifespan_wetland", DOUBLE)
            self.lifespan_wetland = 40

            self.createParameter("lifespan_pond", DOUBLE)
            self.lifespan_pond = 50

            self.createParameter("discount_rate", DOUBLE)
            self.discount_rate = 0.06

            self.createParameter("expected_removal", DOUBLE)
            self.expected_removal = 0.45

            self.createParameter("offset_source", STRING)
            self.offset_source = "observed"

            self.createParameter("budget_source", STRING)
            self.budget_source = "costs"

            self.createParameter("cost_source", STRING)
            self.cost_source = "melbourne_water"

            self.createParameter("offset_scenario", DOUBLE)
            self.offset_scenario = 0

            self.__years = {'raingarden' : [], 'wetland' : [], 'pond': []}
            self.__discount_factor = {'raingarden' : [], 'wetland' : [], 'pond': []}

            self.__lifespans = {'wetland': self.lifespan_wetland, 'raingarden': self.lifespan_rg, 'pond': self.lifespan_pond}

            self.__decomissioning = {'wetland': 0.42, 'raingarden': 0.39, 'pond': 0.38}
            self.__annualised_renewal = {'wetland': 0.0052, 'raingarden': 0.02, 'pond': 0.014}

            for t in self.__lifespans:
                for y in range(1, int(self.__lifespans[t]) + 1, 1):
                    self.__years[t].append(y)
                    self.__discount_factor[t].append(1. / (1. + self.discount_rate) ** (y - 1))

            # for y in xrange(1, int(self.lifespan_rg) + 1, 1):
            #     self.__years['raingarden'].append(y)
            #     self.__discount_factor.append(1. / (1. + self.discount_rate) ** (y - 1))

            '''Producer price index Victoria, roads & bridges, Table 17, index 3101'''
            # self.__cpi = {2005: 73.425, 2006: 77.325, 2007: 80.175, 2008: 85.55,
            #               2009: 88.65, 2010: 90.875, 2011: 97.325, 2012: 102.25}

            '''Index Numbers ;  All groups CPI ;  Melbourne'''

            # self.__cpi = {2004: 81.5, 2005: 83.475, 2006: 86.175, 2007: 88.225, 2008: 91.925, 2009: 93.225, 2010: 96.05,
            #        2011: 99.35, 2012: 100.975, 2013: 103.45}

            '''Index Numbers ;  Non-tradables ;  Melbourne'''

            self.__cpi = {2004: 77, 2005: 79.425, 2006: 81.675, 2007: 84.5, 2008: 88.95, 2009: 90.9, 2010: 94.775, 2011: 98.425,
             2012: 101.85, 2013: 101.85,2014: 101.85, 2015: 101.85}

            self.__suitable_zoneLu = {"wetland": ["GRZ1_Unclassified Private Land", "GRZ2_Unclassified Private Land",
                                                  "PCRZ_Nature Reserve", "PCRZ_Unclassified Private Land",
                                                  "PPRZ_Community Service Facilities or Other",
                                                  "PPRZ_Unclassified Private Land",
                                                  "SUZ2_Outdoor Sports - Extended Areas / Cross Country",
                                                  "UFZ_Nature Reserve",
                                                  "UFZ_Unclassified Private Land"],
                                      "raingarden": ["B1Z_Road Void", "B2Z_Road Void", "B3Z_Road Void", "C1Z_Road Void",
                                                     "C1Z_Unclassified Private Land",
                                                     "C1Z_Unspecified - Transport, Storage, Utilities and Communication",
                                                     "C2Z_Plant / Tree Nursery",
                                                     "CDZ1_Road Void", "CDZ1_Unclassified Private Land",
                                                     "GRZ1_Residential Development Site",
                                                     "GRZ1_Road Void", "GRZ1_Unclassified Private Land",
                                                     "GRZ1_Vacant Englobo Residential Subdivisional Land",
                                                     "GRZ1_Vacant Residential Home Site / Surveyed Lot",
                                                     "GRZ2_Road Void",
                                                     "GRZ2_Unclassified Private Land", "GRZ3_Road Void",
                                                     "GRZ3_Unclassified Private Land",
                                                     "GWAZ1_Detached Home", "GWAZ1_Road Void", "LDRZ_Road Void",
                                                     "LDRZ_Unclassified Private Land",
                                                     "MUZ_Road Void", "MUZ_Unclassified Private Land", "NRZ3_Road Void",
                                                     "NRZ3_Unclassified Private Land",
                                                     "PPRZ_Community Service Facilities or Other",
                                                     "PPRZ_Member Club Facility",
                                                     "PPRZ_Protected Seascape - Public", "PPRZ_Reserved Land",
                                                     "PPRZ_Unclassified Private Land", "PUZ1_Unclassified Private Land",
                                                     "PUZ4_Road Void",
                                                     "PUZ6_Community Service Facilities or Other", "PUZ6_Road Void",
                                                     "PUZ6_Unclassified Private Land",
                                                     "R1Z_Community Service Facilities or Other", "R1Z_Road Void",
                                                     "RDZ1_Road Void", "RDZ2_Road Void", "RGZ1_Road Void",
                                                     "SUZ1_Road Void", "SUZ2_Unclassified Private Land",
                                                     "UFZ_Road Void",
                                                     "UFZ_Unclassified Private Land"],
                                      "pond": ["GRZ1_Vacant Residential Home Site / Surveyed Lot",
                                               "GRZ2_Unclassified Private Land", "GRZ2_Vacant Land mining unspecified",
                                               "IN1Z_Unclassified Private Land", "NA_Reserved Land",
                                               "PCRZ_Nature Reserve",
                                               "PCRZ_Reserved Land",
                                               "PPRZ_Community Service Facilities or Other",
                                               "PPRZ_Unclassified Private Land"]}



            ######## Budget ##########
            self.__dict_budget = {
                2005: 50000,
                2006:  50000,
                2007:  50000,
                2008:  50000,
                2009:  160000,
                2010: 106000,
                2011: 150000,
                2012: 246000}

            self.__dict_costs = {2005: 20000,
                                 2006: 123000,
                                 2007: 647684,
                                 2008: 70000,
                                 2009: 210000,
                                 2010: 0,
                                 2011: 0,
                                 2012: 130000}

            # Outliers removed
            self.__budget_elwood = {"KINGSTON": {2005: 16786, 2006: 0, 2007: 160814, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0,
                          2014: 0},
             "STONNINGTON": {2005: 0, 2006: 12844, 2007: 0, 2008: 0, 2009: 13133, 2010: 6969, 2011: 0, 2012: 292971,
                             2013: 0, 2014: 0},
             "MONASH": {2005: 0, 2006: 0, 2007: 0, 2008: 0, 2009: 13995, 2010: 7955, 2011: 0, 2012: 0, 2013: 0,
                        2014: 0},
             "PORT PHILLIP": {2005: 0, 2006: 0, 2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 233987, 2013: 0,
                              2014: 0},
             "BAYSIDE": {2005: 0, 2006: 0, 2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0},
             "GLEN EIRA": {2005: 164736, 2006: 0, 2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 211553, 2012: 51661,
                           2013: 0, 2014: 0}}



            """Pv costs from Parson Brickerhoff"""
            # self.__dict_pvcosts = {2005: {'KINGSTON':  34113},
            #                      2006: {'KINGSTON': 151164},
            #                      2007: {'KINGSTON': 748486},
            #                      2008: {'KINGSTON': 92064},
            #                      2009: {'KINGSTON': 251926},
            #                      2010: {'KINGSTON': 0},
            #                      2011: {'KINGSTON': 0},
            #                      2012: {'KINGSTON': 182791}}

            """Pv costs from ewater"""

            self.__dict_pvcosts = {2005: 50751.42883533268,
                                   2006: 97300.06141108162,
                                   2007: 410233.28178161825,
                                   2008: 77844.36137145657,
                                   2009: 146530.1345269238,
                                   2010: 0,
                                   2011: 0,
                                   2012: 186431.65982646588}

            # self.__removalRate = {'wetland': 0.61, 'pond': 0.32, 'raingarden': 0.65}
            # self.__adjustmentFactor = {'wetland': 1.2, 'pond': 1.6, 'raingarden': 1.1}
            # self.__requiredSize = {'wetland': 0.024*1.2, 'pond': 0.04*1.6, 'raingarden': 0.014*1.1}

            self.__totalCost = {"BAYSIDE" : 0,
                               "MONASH" : 0,
                               "PORT PHILLIP": 0,
                               "KINGSTON": 0,
                               "GLEN EIRA": 0,
                               "STONNINGTON": 0
                               }
            self.__totalBenefit = {"BAYSIDE" : 0,
                               "MONASH" : 0,
                               "PORT PHILLIP": 0,
                               "KINGSTON": 0,
                               "GLEN EIRA": 0,
                               "STONNINGTON": 0
                               }

            self.__minArea = {"wetland": 200,
                                  "pond": 100,
                                  "raingarden": 5}

            self.__lifespan = {"wetland": 40,
                                  "pond": 50,
                                  "raingarden": 37}
            self.parcel = ViewContainer("parcel", COMPONENT, READ)

            self.parcel.addAttribute("basin_percent_treated", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("basin_eia_treated", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("block_id", Attribute.INT, READ)
            self.parcel.addAttribute("conv_area", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("convertible_area", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("council", Attribute.STRING, READ)
            self.parcel.addAttribute("installation_year", Attribute.INT, WRITE)
            self.parcel.addAttribute("irrigation_demand", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("irrigation_supply", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("lga", Attribute.STRING, READ)
            self.parcel.addAttribute("max_prob_technology", Attribute.STRING, READ)
            self.parcel.addAttribute("tn_removed", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("new_impervious_catchment", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("new_landuse", Attribute.STRING, WRITE)
            self.parcel.addAttribute("npv", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("nrem_benefit", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("OPEX", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("original_landuse", Attribute.STRING, READ)
            self.parcel.addAttribute("ownership", Attribute.STRING, WRITE)
            self.parcel.addAttribute("private_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("prob_rg", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_pond", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_wetland", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("pv_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_nrem", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_irri", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_total", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("rainfall", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("random_nmr", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("released", Attribute.INT, READ)
            self.parcel.addAttribute("temp_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("zone_lu", Attribute.STRING, READ)

            self.city = ViewContainer("city", COMPONENT, READ)

            self.city.addAttribute("budget", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("budget_factor", Attribute.DOUBLE, READ)
            self.city.addAttribute("budget_source", Attribute.STRING, WRITE)
            self.city.addAttribute("const_cost_factor", Attribute.DOUBLE, READ)
            self.city.addAttribute("cost_source", Attribute.STRING, WRITE)
            self.city.addAttribute("decision_rule", Attribute.INT, READ)
            self.city.addAttribute("discount_rate", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("expected_removal", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("lifespan_pond", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("lifespan_rg", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("lifespan_wetland", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("maint_cost_factor", Attribute.DOUBLE, READ)
            self.city.addAttribute("offset_scenario", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("offset_source", Attribute.STRING, WRITE)
            self.city.addAttribute("private_contribution", Attribute.DOUBLE, READ)
            self.city.addAttribute("rf_factor", Attribute.DOUBLE, READ)
            self.city.addAttribute("year", Attribute.INT, READ)

            #Compile views
            views = [self.parcel, self.city]
            self.registerViewContainers(views)

        """
        Data Manipulation Process (DMP)
        """

        ''' Costs assessment '''

        def const_cost(self, technology, area, year, source):
            # Costs from Parson Brickerhoff, 2013
            if source == "melbourne_water":
                if technology == 'wetland':
                    cost = 1911 * area ** 0.6435
                elif technology == 'raingarden':
                    cost = (area * 6023.1 * area ** -0.46)
                elif technology == 'pond':
                    cost = 685.1 * area ** 0.7893
                if year <= 2012:
                    return cost* self.__cpi[year] / self.__cpi[2012]
                else:
                    return cost*(3.15 * year - 6236.6)/ self.__cpi[2012]



            # Costs from Music manual, 2013
            elif source == "music":
                if technology == 'wetland':
                    cost = 1911 * area ** 0.6435
                elif technology == 'raingarden':
                    cost = 387.4 * area ** 0.7673
                    # cost = (area * 6023.1 * area ** -0.46)
                elif technology == 'pond':
                    cost = 685.1 * area ** 0.7893
                if year <= 2012:
                    return cost* self.__cpi[year] / self.__cpi[2012]
                else:
                    return cost*(3.15 * year - 6236.6)/ self.__cpi[2012]

        def inv_cost(self, technology, budget):
            if technology == 'wetland':
                area = 0.00000796*(budget ** 1.554001554)
            elif technology == 'raingarden':
                area = 0.0000001*(budget**1.85185185185)
            elif technology == 'pond':
                area = 0.00025546 * (budget ** 1.266945394653)
            return area

        def maint_cost(self, technology, area, year, source):
            ### Maintenance costs from Parson Brickerhoff, 2013 ###
            if source == "melbourne_water":
                if technology == 'wetland':
                    cost = area * 1289.7 * area ** -0.794
                elif technology == 'raingarden':
                    cost = area * 199.19 * area ** -0.551
                elif technology == 'pond':
                    cost = 185.4 * area ** 0.4780
                    # if area < 250:
                    #     cost = 18 * area
                    # elif 250 <= area < 500:
                    #     cost = 12 * area
                    # elif 500 <= area < 1500:
                    #     cost = 5 * area
                    # elif 1500 <= area:
                    #     cost = 2 * area
                if year <= 2012:
                    mcost = cost* self.__cpi[year] / self.__cpi[2012]
                    renewal = self.__annualised_renewal[technology] * self.__cpi[year] / self.__cpi[2004]

                else:
                    mcost = cost*(3.15 * year - 6236.6)/ self.__cpi[2012]
                    renewal = self.__annualised_renewal[technology] * (3.15 * year - 6236.6) / self.__cpi[2004]

                # mcost = cost* self.__cpi[year] / self.__cpi[2012]
                # renewal = self.__annualised_renewal[technology] * self.__cpi[year] / self.__cpi[2004]
                maintenance_cost = []
                renewal_cost = []
                for y in self.__years[technology]:
                    maintenance_cost.append(mcost)
                    renewal_cost.append(renewal)
                discount_maintenance_cost = [(d * m) + (d*r) for d, m, r in zip(self.__discount_factor[technology], maintenance_cost,renewal_cost)]
                return sum(discount_maintenance_cost)

            ### Maintenance costs from Music manual, 2013 ###
            elif source == "music":
                if technology == 'wetland':
                    cost = 6.831 * area **0.8634
                elif technology == 'raingarden':
                    cost = 48.87*self.const_cost(technology, area, year, source)**0.4410
                elif technology == 'pond':
                    cost = 185.4 * area ** 0.4780
                if year <= 2012:
                    mcost = cost* self.__cpi[year] / self.__cpi[2012]
                    renewal = self.__annualised_renewal[technology] * self.__cpi[year] / self.__cpi[2004]
                else:
                    mcost = cost*(3.15 * year - 6236.6)/ self.__cpi[2012]
                    renewal = self.__annualised_renewal[technology] * (3.15 * year - 6236.6) / self.__cpi[2004]
                # mcost = cost* self.__cpi[year] / self.__cpi[2004]
                # renewal = self.__annualised_renewal[technology] * self.__cpi[year] / self.__cpi[2004]
                maintenance_cost = []
                renewal_cost = []
                for y in self.__years[technology]:
                    maintenance_cost.append(mcost)
                    renewal_cost.append(renewal)
                discount_maintenance_cost = [(d * m) + (d*r) for d, m, r in zip(self.__discount_factor[technology], maintenance_cost,renewal_cost)]
                return sum(discount_maintenance_cost)

        """ Total PV costs function for Parson Brickerhoff"""
        # def pv_total_costs(self, year, technology, area):
        #     reset = 75 * area * 1. / (1. + self.discount_rate) ** (12.5)
        #     try:
        #         if technology in ['wetland', 'pond']:
        #             return self.const_cost(technology, area, year) + self.maint_cost(technology, area,year)
        #         elif technology == 'raingarden':
        #             return self.const_cost(technology, area, year) + self.maint_cost(technology, area,year)+reset
        #     except (LookupError):
        #         raise ValueError("can't calculate total costs")

        """Function for Music"""
        def pv_total_costs(self, year, technology, area, source):
            decomissioning_cost = (self.const_cost(technology, area, year, source)*self.__decomissioning[technology])
            disc_decom_cost = decomissioning_cost* 1. / (1. + self.discount_rate) ** (self.__lifespans[technology])

            try:
                return self.const_cost(technology, area, year, source) + self.maint_cost(technology, area,year, source)+disc_decom_cost
            except (LookupError):
                raise ValueError("can't calculate total costs")

        ########## Benefit assessment #############

        def n_removed(self, area, runoff):
            n = runoff * 0.0021 * area
            return n

        def benefit_fun(self, rate, n_removed):
            b = rate * n_removed
            return b

        def pv_benefit(self, b, technology):
            benefit_list = []
            for y in self.__years:
                benefit_list.append(b)
            discount_n_removal = [(d * b) for d, b in zip(self.__discount_factor[technology], benefit_list)]

            return sum(discount_n_removal)

        def design_curves(self, expected_removal, technology):
            if technology == 'wetland':
                adjustment_factor = 1.2
                # For 500 mm extended detention
                area_needed =  0.0016*math.exp(6.1343*expected_removal)*adjustment_factor
            elif technology == 'pond':
                adjustment_factor = 1.6
                area_needed =  0.0011*math.exp(8.249*expected_removal)*adjustment_factor
            elif technology == 'raingarden':
                adjustment_factor = 1.1
                # For 100 mm extended detention
                area_needed =  0.000661*math.exp(7.5786*expected_removal)*adjustment_factor
            return min(1, area_needed)

        def offset(self, year, source, scenario_offset):
            if source == "observed":
                if year < 2005:
                    offset = 0
                elif year > 2013:
                    offset = 7236
                else:
                    offset_dict={2005: 51, 2006: 51, 2007: 51, 2008: 51, 2009: 70, 2010: 70, 2011: 141, 2012: 141, 2013: 141}
                    offset = offset_dict[year]
            elif source == "scenario":
                offset = scenario_offset
            return offset

        def run(self):
            #Data Stream Manipulation

            self.city.reset_reading()
            for c in self.city:
                const_cost_factor= c.GetFieldAsDouble("const_cost_factor")
                decision_rule = c.GetFieldAsInteger("decision_rule")
                maint_cost_factor= c.GetFieldAsDouble("maint_cost_factor")
                rf_factor = c.GetFieldAsDouble("rf_factor")
                year = c.GetFieldAsInteger("year")

                c.SetField("budget_source", self.budget_source)
                c.SetField("cost_source", self.cost_source)
                c.SetField("discount_rate", self.discount_rate)
                c.SetField("expected_removal", self.expected_removal)
                c.SetField("lifespan_rg", self.lifespan_rg)
                c.SetField("lifespan_wetland", self.lifespan_wetland)
                c.SetField("lifespan_pond", self.lifespan_pond)
                c.SetField("offset_scenario", self.offset_scenario)
                c.SetField("offset_source", self.offset_source)

            self.city.finalise()

            self.parcel.reset_reading()

            # Dictionary with {block_id: percentage of eia in the catchment treated}
            blocks = {}

            for p in self.parcel:

                area = p.GetFieldAsDouble("convertible_area")
                block_id = p.GetFieldAsInteger("block_id")
                council = p.GetFieldAsString("council")
                impervious_catchment = p.GetFieldAsDouble("new_impervious_catchment")
                irrigation_demand = p.GetFieldAsDouble("irrigation_demand")
                landuse = p.GetFieldAsString("original_landuse")
                lga = p.GetFieldAsString("lga")
                max_prob_technology = p.GetFieldAsString("max_prob_technology")
                newlanduse = p.GetFieldAsString("new_landuse")
                prob_rg = p.GetFieldAsDouble("prob_rg")
                prob_wl = p.GetFieldAsDouble("prob_wetland")
                prob_pd = p.GetFieldAsDouble("prob_pond")
                rainfall = p.GetFieldAsDouble("rainfall")
                released = p.GetFieldAsInteger("released")
                zone_lu = p.GetFieldAsString("zone_lu")

                if self.budget_source == "budget":
                    remaining_budget = self.__dict_budget[year]- self.__totalCost[lga]
                    c.SetField("budget", remaining_budget)
                elif self.budget_source == "costs":
                    # print lga, self.__totalCost, year, self.__dict_costs
                    remaining_budget = self.__dict_costs[year]- self.__totalCost[lga]
                    c.SetField("budget", remaining_budget)
                elif self.budget_source == "pvcosts":
                    remaining_budget = self.__dict_pvcosts[year]- self.__totalCost[lga]
                    c.SetField("budget", remaining_budget)
                elif self.budget_source == "Elwood":
                    if lga in self.__budget_elwood.keys():
                        budget = self.__budget_elwood[lga][year]
                        remaining_budget = budget - self.__totalCost[lga]
                        c.SetField("budget", budget)
                    else:
                        remaining_budget = 0
                elif self.budget_source == "budget1":
                    budget = 250000
                    c.SetField("budget", budget)
                elif self.budget_source == "budget2":
                    budget = 500000
                    c.SetField("budget", budget)
                elif self.budget_source == "budget3":
                    budget = 1000000
                    c.SetField("budget", budget)
                else:
                    print "***Source chosen not in choices***"
                # Estimate runoff for current year
                rainfall /= 1000.
                runoff = rainfall * rf_factor * 0.9
                offset_rate = self.offset(year, self.offset_source, self.offset_scenario)

                # Strategy 1: Chose technology with highest probability
                if decision_rule == 1 and released < 2000:
                    # print "Enter decision process"

                    technology = max_prob_technology

                    # If a a parcel in this block has already been converted
                    if block_id in blocks:
                        # The required area equals the % from design curves * the total basin eia - the basin eia already treated
                        requiredArea = self.design_curves(self.expected_removal,
                                                          technology) * (impervious_catchment - blocks[block_id])
                    else:
                        requiredArea = self.design_curves(self.expected_removal, technology) * impervious_catchment

                    if requiredArea > area:
                        conArea = area
                    else:
                        conArea = requiredArea

                    # if landuse has not yet been converted AND available area is larger than minimum area AND landuse is suitable
                    if landuse == newlanduse and conArea >= self.__minArea[technology] and zone_lu in self.__suitable_zoneLu[technology]:
                        # define the area

                        cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                        opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                        if cost <= remaining_budget:
                            eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                            percent_treated = eia_treated / impervious_catchment

                            tn_removed = self.n_removed(eia_treated, runoff)
                            b = self.benefit_fun(offset_rate, tn_removed)

                            if technology in ["pond", "wetland"]:
                                irri_supply = min(irrigation_demand, runoff * eia_treated)
                                irri_benefit = irri_supply * 2.66
                            else:
                                irri_benefit = 0
                                irri_supply = 0

                            pvb_nrem = self.pv_benefit(b, technology)
                            pvb_irri = self.pv_benefit(irri_benefit, technology)
                            pvb_total = pvb_nrem + pvb_irri
                            pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)
                            npv = pvb_total - pvc

                            p.SetField("basin_percent_treated", percent_treated)
                            p.SetField("basin_eia_treated", eia_treated)
                            p.SetField("conv_area", conArea)
                            p.SetField("cost", cost)
                            p.SetField("installation_year", year)
                            p.SetField("irrigation_supply", irri_supply)
                            p.SetField("new_landuse", technology)
                            p.SetField("npv", npv)
                            p.SetField("nrem_benefit", b)
                            p.SetField("OPEX", opex)
                            p.SetField("ownership", "public")
                            p.SetField("pv_benefit_irri", pvb_irri)
                            p.SetField("pv_benefit_nrem", pvb_nrem)
                            p.SetField("pv_benefit_total", pvb_total)
                            p.SetField("pv_cost", pvc)
                            p.SetField("temp_cost", cost)
                            p.SetField("tn_removed", tn_removed)


                            if self.budget_source == "pvcosts":
                                self.__totalCost[lga] += pvc
                            else:
                                self.__totalCost[lga] += cost
                            self.__totalBenefit[lga] += b

                            print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                            print 'Council: ', council, 'Year: ' ,str(year), ' area: ' , str(area) ,'conArea: ' , str(conArea)
                            print ' cost: ',str(cost), ' total cost: ', str(self.__totalCost[lga]), ' benefit: ', str(b)+' budget: ', str(remaining_budget)

                            # if a parcel in this block has had a wsud, add eia_treated to existing eia_treated,
                            # otherwise add the to the new eia_treated
                            if block_id in blocks:
                                blocks[block_id] += eia_treated
                            else:
                                blocks[block_id] = eia_treated

                # Strategy 2: Whole budget is spent on most likely parcel
                if decision_rule == 2 and released < 2000 and remaining_budget > 0:

                    technology = max_prob_technology

                    # If a parcel within this block has already been converted, the impervious catchment already treated
                    # from the previous technology is substracted from the total impervious catchment
                    if block_id in blocks:
                        requiredArea = self.design_curves(self.expected_removal, technology) * (impervious_catchment - blocks[block_id])


                    # if no existing wsud in the block, the required area is according to design curves
                    else:
                        requiredArea = self.design_curves(self.expected_removal, technology) * impervious_catchment

                    if self.inv_cost(technology, remaining_budget) < area and self.inv_cost(technology, remaining_budget) < requiredArea:
                        conArea = self.inv_cost(technology, remaining_budget)
                    elif requiredArea > area:
                        conArea = area
                    else:
                        conArea = requiredArea

                    # if landuse has not yet been converted AND available area is larger than minimum area and landuse is suitable
                    if landuse == newlanduse and conArea >= self.__minArea[technology] and zone_lu in \
                            self.__suitable_zoneLu[technology]:
                        'Criteria are met'
                        # define the area
                        conArea = round(conArea,2)

                        cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                        opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                        if cost <= remaining_budget:
                            eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                            percent_treated = eia_treated / impervious_catchment

                            tn_removed = self.n_removed(eia_treated, runoff)
                            b = self.benefit_fun(offset_rate, tn_removed)

                            if technology in ["pond", "wetland"]:
                                irri_supply = min(irrigation_demand, runoff * eia_treated)
                                irri_benefit = irri_supply * 2.66
                            else:
                                irri_benefit = 0
                                irri_supply = 0

                            pvb_nrem = self.pv_benefit(b, technology)
                            pvb_irri = self.pv_benefit(irri_benefit, technology)
                            pvb_total = pvb_nrem + pvb_irri
                            pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)
                            npv = pvb_total - pvc

                            p.SetField("basin_percent_treated", percent_treated)
                            p.SetField("basin_eia_treated", eia_treated)
                            p.SetField("conv_area", conArea)
                            p.SetField("cost", cost)
                            p.SetField("installation_year", year)
                            p.SetField("irrigation_supply", irri_supply)
                            p.SetField("new_landuse", technology)
                            p.SetField("npv", npv)
                            p.SetField("nrem_benefit", b)
                            p.SetField("OPEX", opex)
                            p.SetField("ownership", "public")
                            p.SetField("pv_benefit_irri", pvb_irri)
                            p.SetField("pv_benefit_nrem", pvb_nrem)
                            p.SetField("pv_benefit_total", pvb_total)
                            p.SetField("pv_cost", pvc)
                            p.SetField("temp_cost", cost)
                            p.SetField("tn_removed", tn_removed)

                            # Substract cost of WSUD from remaining budget
                            if self.budget_source == "pvcosts":
                                self.__totalCost[lga] += pvc
                            else:
                                self.__totalCost[lga] += cost

                            self.__totalBenefit[lga] += b
                            print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                            print 'Council: ', lga, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                conArea)
                            print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost[lga]), ' benefit: ', str(
                                b) + ' budget: ', str(remaining_budget)

                            # if a parcel in this block has had a wsud, add eia_treated to existing eia_treated,
                            # otherwise add the to the new eia_treated
                            if block_id in blocks:
                                blocks[block_id] += eia_treated
                            else:
                                blocks[block_id] = eia_treated

                if decision_rule == 3 and released < 2000:
                    bmps = ["raingarden", "wetland", "pond"]
                    dict_required_area = {}
                    if block_id in blocks:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * (
                        impervious_catchment - blocks[block_id])
                    # elif impervious_catchment == 0:
                    #     requiredArea = self.design_curves(self.expected_removal, technology) * area
                    else:
                        for i in bmps:
                            dict_required_area[i] =  self.design_curves(self.expected_removal, i) * impervious_catchment

                    dict_conv_area = {}

                    for i in dict_required_area:
                        if dict_required_area[i] > area:
                            dict_conv_area[i] = area
                        else:
                            dict_conv_area[i] = dict_required_area[i]

                    # if landuse has not yet been converted AND available area is larger than minimum area
                    if landuse == newlanduse:

                        # Criteria are met
                        list_suitable_parcels = []
                        list_installed_tech = []
                        # define the area

                        # Dictionary of technologies and probabilities
                        d_probs = {'wetland': prob_wl, 'pond': prob_pd, "raingarden": prob_rg}

                        # Select potential technologies based on land use
                        for i in self.__suitable_zoneLu.iterkeys():
                            if zone_lu in self.__suitable_zoneLu[i] and dict_conv_area[i] > self.__minArea[i]:
                                list_suitable_parcels.append(i)

                        # Select technologies based on probability and landuse suitability
                        for i in list_suitable_parcels:
                            random_nmr = random.random()
                            if random_nmr < d_probs[i]:
                                list_installed_tech.append(i)

                        # List chosen technologies
                        # list_installed_tech = [x for x in list_suitable_parcels if random.random() < d_probs[x]]

                        # Create dictionary of benefits for cost-benefit analysis if more than one option
                        benefits = {}
                        if len(list_installed_tech) >= 1:
                            # print "More than one option available"
                            for i in list_installed_tech:
                                pvc = self.pv_total_costs(year, i, dict_conv_area[i], self.cost_source)

                                # removal = self.__removalRate[i]
                                tn_removed = self.n_removed(dict_conv_area[i]/self.design_curves(self.expected_removal, i), runoff)
                                b = self.benefit_fun(offset_rate, tn_removed)
                                pvb = self.pv_benefit(b, i)
                                benefits[i]= pvb-pvc
                            technology = max(benefits)
                        # Otherwise select the only option available
                            conArea = dict_conv_area[technology]
                            # percent_treated = conArea / dict_required_area[technology]

                            cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                            opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                            if cost <= remaining_budget:
                                eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                                percent_treated = eia_treated / impervious_catchment

                                tn_removed = self.n_removed(eia_treated, runoff)
                                b = self.benefit_fun(offset_rate, tn_removed)

                                if technology in ["pond", "wetland"]:
                                    irri_supply = min(irrigation_demand, runoff * eia_treated)
                                    irri_benefit = irri_supply * 2.66
                                else:
                                    irri_supply = 0
                                    irri_benefit = 0

                                pvb_nrem = self.pv_benefit(b, technology)
                                pvb_irri = self.pv_benefit(irri_benefit, technology)
                                pvb_total = pvb_nrem + pvb_irri
                                pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)
                                npv = pvb_total - pvc

                                p.SetField("basin_percent_treated", percent_treated)
                                p.SetField("basin_eia_treated", eia_treated)
                                p.SetField("conv_area", conArea)
                                p.SetField("cost", cost)
                                p.SetField("installation_year", year)
                                p.SetField("irrigation_supply", irri_supply)
                                p.SetField("new_landuse", technology)
                                p.SetField("npv", npv)
                                p.SetField("nrem_benefit", b)
                                p.SetField("OPEX", opex)
                                p.SetField("ownership", "public")
                                p.SetField("pv_benefit_irri", pvb_irri)
                                p.SetField("pv_benefit_nrem", pvb_nrem)
                                p.SetField("pv_benefit_total", pvb_total)
                                p.SetField("pv_cost", pvc)
                                p.SetField("random_nmr", random_nmr)
                                p.SetField("temp_cost", cost)
                                p.SetField("tn_removed", tn_removed)


                                if self.budget_source == "pvcosts":
                                    self.__totalCost[lga] += pvc
                                else:
                                    self.__totalCost[lga] += cost
                                self.__totalBenefit[lga] += b
                                print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost[lga]), ' benefit: ', str(b) + ' budget: ', str(remaining_budget)
                                # if a parcel in this block has had a wsud, add eia_treated to existing eia_treated,
                                # otherwise add the to the new eia_treated
                                if block_id in blocks:
                                    blocks[block_id] += eia_treated
                                else:
                                    blocks[block_id] = eia_treated


                if decision_rule == 4 and released < 2000:
                    bmps = ["raingarden", "wetland", "pond"]
                    dict_required_area = {}
                    if block_id in blocks:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * (
                        impervious_catchment - blocks[block_id])
                    # elif impervious_catchment == 0:
                    #     requiredArea = self.design_curves(self.expected_removal, technology) * area
                    else:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * impervious_catchment

                    dict_conv_area = {}

                    for i in dict_required_area:
                        if dict_required_area[i] > area:
                            dict_conv_area[i] = area
                        else:
                            dict_conv_area[i] = dict_required_area[i]

                    # if landuse has not yet been converted AND available area is larger than minimum area
                    if landuse == newlanduse:

                        # Criteria are met
                        list_suitable_parcels = []
                        list_installed_tech = []
                        # define the area

                        # Dictionary of technologies and probabilities
                        d_probs = {'wetland': prob_wl, 'pond': prob_pd, "raingarden": prob_rg}

                        # Select potential technologies based on land use
                        for i in self.__suitable_zoneLu.iterkeys():
                            if zone_lu in self.__suitable_zoneLu[i] and dict_conv_area[i] > self.__minArea[i]:
                                list_suitable_parcels.append(i)

                        # Select technologies based on probability and landuse suitability
                        for i in list_suitable_parcels:
                            if random.random() < d_probs[i]:
                                list_installed_tech.append(i)

                        # List chosen technologies
                        # list_installed_tech = [x for x in list_suitable_parcels if random.random() < d_probs[x]]

                        # Create dictionary of benefits for cost-benefit analysis if more than one option
                        costs = {}
                        if len(list_installed_tech) >= 1:
                            # print "More than one option available"
                            for i in list_installed_tech:
                                pvc = self.pv_total_costs(year, i, dict_conv_area[i], self.cost_source)
                                costs[i] = pvc
                            technology = min(costs)
                        # Otherwise select the only option available
                            conArea = dict_conv_area[technology]
                            # percent_treated = conArea / dict_required_area[technology]

                            cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                            opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                            if cost <= remaining_budget:
                                eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                                percent_treated = eia_treated / impervious_catchment

                                tn_removed = self.n_removed(eia_treated, runoff)
                                b = self.benefit_fun(offset_rate, tn_removed)


                                if technology in ["pond", "wetland"]:
                                    irri_supply = min(irrigation_demand, runoff * eia_treated)
                                    irri_benefit = irri_supply * 2.66
                                else:
                                    irri_supply = 0
                                    irri_benefit = 0

                                pvb_nrem = self.pv_benefit(b, technology)
                                pvb_irri = self.pv_benefit(irri_benefit, technology)
                                pvb_total = pvb_nrem + pvb_irri
                                npv = pvb_total - pvc

                                p.SetField("basin_percent_treated", percent_treated)
                                p.SetField("basin_eia_treated", eia_treated)
                                p.SetField("conv_area", conArea)
                                p.SetField("cost", cost)
                                p.SetField("installation_year", year)
                                p.SetField("irrigation_supply", irri_supply)
                                p.SetField("new_landuse", technology)
                                p.SetField("npv", npv)
                                p.SetField("nrem_benefit", b)
                                p.SetField("OPEX", opex)
                                p.SetField("ownership", "public")
                                p.SetField("pv_benefit_irri", pvb_irri)
                                p.SetField("pv_benefit_nrem", pvb_nrem)
                                p.SetField("pv_benefit_total", pvb_total)
                                p.SetField("pv_cost", pvc)
                                p.SetField("temp_cost", cost)
                                p.SetField("tn_removed", tn_removed)

                                if self.budget_source == "pvcosts":
                                    self.__totalCost[lga] += pvc
                                else:
                                    self.__totalCost[lga] += cost
                                self.__totalBenefit[lga] += b
                                print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                    conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost[lga]), ' benefit: ', str(
                                    b) + ' budget: ', str(remaining_budget)

                                # full_budget -= cost
                                # if a pracel in this block has had a wsud, add eia_treated to existing eia_treated,
                                # otherwise add the to the new eia_treated
                                if block_id in blocks:
                                    blocks[block_id] += eia_treated
                                else:
                                    blocks[block_id] = eia_treated

                # self.__totalCost[lga] = 0
                # self.__totalBenefit[lga] = 0
            self.parcel.finalise()
