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
             2012: 101.85}

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

            self.__totalCost = 0
            self.__totalBenefit = 0

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

            # self.__totalCost = {"BAYSIDE" : 0,
            #                    "MONASH" : 0,
            #                    "PORT PHILLIP": 0,
            #                    "KINGSTON": 0,
            #                    "GLEN EIRA": 0,
            #                    "STONNINGTON": 0
            #                    }
            # self.__totalBenefit = {"BAYSIDE" : 0,
            #                    "MONASH" : 0,
            #                    "PORT PHILLIP": 0,
            #                    "KINGSTON": 0,
            #                    "GLEN EIRA": 0,
            #                    "STONNINGTON": 0
            #                    }

            self.__minArea = {"wetland": 200,
                                  "pond": 100,
                                  "raingarden": 5}


            self.__lifespan = {"wetland": 40,
                                  "pond": 50,
                                  "raingarden": 37}



            self.parcel = ViewContainer("parcel", COMPONENT, READ)
            self.parcel.addAttribute("original_landuse", Attribute.STRING, READ)
            self.parcel.addAttribute("convertible_area", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("zone_lu", Attribute.STRING, READ)
            self.parcel.addAttribute("max_prob_technology", Attribute.STRING, READ)
            self.parcel.addAttribute("new_impervious_catchment", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("roof_area", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("block_id", Attribute.INT, READ)

            self.parcel.addAttribute("new_landuse", Attribute.STRING, WRITE)
            self.parcel.addAttribute("council", Attribute.STRING, READ)

            self.parcel.addAttribute("N_removed", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("nrem_benefit", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("private_cost", Attribute.DOUBLE, WRITE)
            # self.parcel.addAttribute("avg_wtp_stream", Attribute.DOUBLE, READ)
            # self.parcel.addAttribute("decision_rule", Attribute.INT, READ)

            # self.parcel.addAttribute("random", Attribute.DOUBLE, READ)
            # self.parcel.addAttribute("year", Attribute.INT, READ)
            # self.parcel.addAttribute("budget", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("released", Attribute.INT, READ)

            self.parcel.addAttribute("prob_rg", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_pond", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_wetland", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("conv_area", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("basin_percent_treated", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("basin_eia_treated", Attribute.DOUBLE, WRITE)

            self.parcel.addAttribute("installation_year", Attribute.INT, WRITE)
            self.parcel.addAttribute("OPEX", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("temp_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_nrem", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_irri", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_total", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("ownership", Attribute.STRING, WRITE)

            self.parcel.addAttribute("npv", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("random_nmr", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("rainfall", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("irrigation_demand", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("irrigation_supply", Attribute.DOUBLE, WRITE)


            self.council = ViewContainer("council", COMPONENT, READ)
            self.council.addAttribute("const_cost_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("maint_cost_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("budget_source", Attribute.STRING, READ)
            self.council.addAttribute("budget_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("rf_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("private_contribution", Attribute.DOUBLE, READ)
            # self.council.addAttribute("budget", Attribute.DOUBLE, READ)
            self.council.addAttribute("year", Attribute.INT, READ)
            self.council.addAttribute("decision_rule", Attribute.INT, READ)
            self.council.addAttribute("discount_rate", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("expected_removal", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("offset_source", Attribute.STRING, WRITE)
            self.council.addAttribute("offset_scenario", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("lifespan_rg", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("lifespan_wetland", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("lifespan_pond", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("budget", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("budget_source", Attribute.STRING, WRITE)
            self.council.addAttribute("cost_source", Attribute.STRING, WRITE)



            #Compile views
            views = [self.parcel, self.council]

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition
        """
        Data Manipulation Process (DMP)
        """

        ''' Costs assessment '''

        def const_cost(self, technology, area, year, source):
            ### Costs from Parson Brickerhoff, 2013 ###
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



            ### Costs from Music manual, 2013 ###
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
                    offset_dict={2005: 800, 2006: 800, 2007: 800, 2008: 800, 2009: 1100, 2010: 1100, 2011: 2225, 2012: 2225, 2013: 2225}
                    offset = offset_dict[year]

            elif source == "scenario":
                offset = scenario_offset
            return offset

        def run(self):
            #Data Stream Manipulation

            self.council.reset_reading()
            for c in self.council:
                decision_rule = c.GetFieldAsInteger("decision_rule")
                const_cost_factor= c.GetFieldAsDouble("const_cost_factor")
                maint_cost_factor= c.GetFieldAsDouble("maint_cost_factor")
                budget_factor= c.GetFieldAsDouble("budget_factor")
                # budget_source = c.GetFieldAsString("budget_source")
                rf_factor = c.GetFieldAsDouble("rf_factor")
                offset_paid = c.GetFieldAsDouble("private_contribution")
                year = c.GetFieldAsInteger("year")


                # council_name = c.GetFieldAsString("lga_name")

                if self.budget_source == "budget":
                    # print year, type(year), council, type(council)
                    budget = self.__dict_budget[year]
                    c.SetField("budget", budget)
                elif self.budget_source == "costs":
                    budget = self.__dict_costs[year]
                    c.SetField("budget", budget)
                elif self.budget_source == "pvcosts":
                    budget = self.__dict_pvcosts[year]
                    c.SetField("budget", budget)
                elif self.budget_source == "budget1":
                    budget = 250000
                    c.SetField("budget", budget)
                elif self.budget_source == "budget2":
                    budget = 500000
                    c.SetField("budget", budget)
                elif self.budget_source == "budget3":
                    budget = 1000000
                    c.SetField("budget", budget)
                # elif budget_source == "scenario":
                #     c.SetField("budget", self.amount)
                else:
                    print "***Source chosen not in choices***"

                budget+=offset_paid

                c.SetField("discount_rate", self.discount_rate)
                c.SetField("expected_removal", self.expected_removal)
                c.SetField("offset_source", self.offset_source)
                c.SetField("offset_scenario", self.offset_scenario)
                c.SetField("budget_source", self.budget_source)
                c.SetField("cost_source", self.cost_source)

                c.SetField("lifespan_rg", self.lifespan_rg)
                c.SetField("lifespan_wetland", self.lifespan_wetland)
                c.SetField("lifespan_pond", self.lifespan_pond)


                budget = budget*budget_factor

            self.council.finalise()

            self.parcel.reset_reading()

            # Dictionary with {block_id: percentage of eia in the catchment treated}
            blocks = {}

            for p in self.parcel:

                # Load full annual budget and all other values
                # full_budget = p.GetFieldAsDouble("budget")
                council = p.GetFieldAsString("council")

                # year = p.GetFieldAsInteger("year")
                # decision_rule = p.GetFieldAsInteger("decision_rule")

                landuse = p.GetFieldAsString("original_landuse")
                newlanduse = p.GetFieldAsString("new_landuse")
                zone_lu = p.GetFieldAsString("zone_lu")
                imperviousCatchment = p.GetFieldAsDouble("new_impervious_catchment")
                block_id = p.GetFieldAsInteger("block_id")
                roof_area = p.GetFieldAsDouble("roof_area")

                area = p.GetFieldAsDouble("convertible_area")
                # loss_aversion = p.GetFieldAsDouble("loss_aversion")
                prob_rg = p.GetFieldAsDouble("prob_rg")
                prob_wl = p.GetFieldAsDouble("prob_wetland")
                prob_pd = p.GetFieldAsDouble("prob_pond")
                max_prob_technology = p.GetFieldAsString("max_prob_technology")
                rainfall = p.GetFieldAsDouble("rainfall")
                released = p.GetFieldAsInteger("released")
                irrigation_demand = p.GetFieldAsDouble("irrigation_demand")


                # Substract current cumulative costs from full budget

                # full_budget  self.__totalCost
                remaining_budget = budget - self.__totalCost
                # Estimate runoff for current year
                # runoff = self.__rainfall[year] * rf_factor * 0.9 * 0.20
                rainfall = rainfall/1000.
                # runoff = rainfall * rf_factor * 0.9 * 0.20
                runoff = rainfall * rf_factor * 0.9
                offset_rate = self.offset(year, self.offset_source, self.offset_scenario)

                # print 'Budget: ', str(full_budget), "Rule: ", str(decision_rule)
                # print 'Area: ', str(area)

                ### Strategy 1: Chose technology with highest probability ###
                if decision_rule == 1 and released < 2000:
                    # print "Enter decision process"

                    technology = max_prob_technology

                    # If a a parcel in this block has already been converted
                    if block_id in blocks:
                        # The required area equals the % from design curves * the total basin eia - the basin eia already treated
                        requiredArea = self.design_curves(self.expected_removal,technology) * (imperviousCatchment - blocks[block_id])
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.design_curves(self.expected_removal, technology) * area
                    else:
                        requiredArea = self.design_curves(self.expected_removal, technology) * imperviousCatchment

                    if requiredArea > area:
                        conArea = area
                    else:
                        conArea = requiredArea
                    # print max_prob_technology,landuse,newlanduse, conArea,self.__minArea[technology], zone_lu
                    # if landuse has not yet been converted AND available area is larger than minimum area AND landuse is suitable
                    if landuse == newlanduse and conArea >= self.__minArea[technology] and zone_lu in self.__suitable_zoneLu[technology]:
                        # print 'Criteria are met'
                        # define the area


                        cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                        opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                        if cost <= remaining_budget:
                            # print 'cost is within budget'
                            # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}

                            # b = self.benefitdic[self.technologies[self.tech]]

                            eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                            percent_treated = eia_treated / imperviousCatchment
                            p.SetField("basin_percent_treated", percent_treated)
                            p.SetField("basin_eia_treated", eia_treated)

                            # removal = self.__removalRate[technology]
                            N_removed = self.n_removed(eia_treated, runoff)
                            b = self.benefit_fun(offset_rate, N_removed)

                            p.SetField("new_landuse", technology)
                            p.SetField("N_removed", N_removed)
                            p.SetField("nrem_benefit", b)
                            p.SetField("cost", cost)
                            p.SetField("temp_cost", cost)
                            p.SetField("OPEX", opex)
                            p.SetField("installation_year", year)
                            p.SetField("conv_area", conArea)
                            p.SetField("ownership", "public")

                            if technology in ["pond", "wetland"]:
                                irri_supply = min(irrigation_demand, runoff * eia_treated)
                                irri_benefit = irri_supply * 2.66
                            else:
                                irri_benefit = 0
                                irri_supply = 0
                            p.SetField("irrigation_supply", irri_supply)

                            pvb_nrem = self.pv_benefit(b, technology)
                            pvb_irri= self.pv_benefit(irri_benefit, technology)
                            pvb_total = pvb_nrem + pvb_irri

                            if self.budget_source == "pvcosts":
                                self.__totalCost += pvc
                            else:
                                self.__totalCost += cost

                            self.__totalBenefit += b
                            pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)

                            npv = pvb_total - pvc


                            p.SetField("pv_cost", pvc)
                            p.SetField("pv_benefit_nrem", pvb_nrem)
                            p.SetField("pv_benefit_irri", pvb_irri)
                            p.SetField("pv_benefit_total", pvb_total)

                            p.SetField("npv", npv)

                            print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                            print 'Council: ', council, 'Year: ' ,str(year), ' area: ' , str(area) ,'conArea: ' , str(conArea)
                            print ' cost: ',str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(b)+' budget: ', str(remaining_budget)
                            # print str(self.technologies[self.tech])
                            # print random_number
                            # full_budget -= cost
                            # if a pracel in this block has had a wsud, add eia_treated to existing eia_treated,
                            # otherwise add the to the new eia_treated
                            if block_id in blocks:
                                blocks[block_id] += eia_treated
                            else:
                                blocks[block_id] = eia_treated

                            # blocks[block_id] = eia_treated
                        # else:
                        #     print "criteria not met"


                ### Strategy 2: Whole budget is spent on most likely parcel
                if decision_rule == 2 and released < 2000 and remaining_budget > 0:

                    technology = max_prob_technology

                    # If a parcel within this block has already been converted, the impervious catchment already treated
                    # from the previous technology is substracted from the total impervious catchment
                    if block_id in blocks:
                        requiredArea = self.design_curves(self.expected_removal, technology) * (imperviousCatchment - blocks[block_id])


                    # if no existing wsud in the block, the required area is according to design curves
                    else:
                        requiredArea = self.design_curves(self.expected_removal, technology) * imperviousCatchment

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
                        # percent_treated = conArea / requiredArea

                        cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                        opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                        if cost <= remaining_budget:
                            # print 'cost is within budget'
                            # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}

                            eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                            percent_treated = eia_treated / imperviousCatchment
                            # blocks[block_id] = percent_treated
                            # b = self.benefitdic[self.technologies[self.tech]]
                            # removal = self.__removalRate[technology]

                            N_removed = self.n_removed(eia_treated, runoff)
                            b = self.benefit_fun(offset_rate, N_removed)

                            p.SetField("new_landuse", technology)
                            p.SetField("N_removed", N_removed)
                            p.SetField("nrem_benefit", b)
                            p.SetField("cost", cost)
                            p.SetField("temp_cost", cost)
                            p.SetField("OPEX", opex)
                            p.SetField("installation_year", year)
                            p.SetField("conv_area", conArea)
                            p.SetField("ownership", "public")

                            p.SetField("basin_percent_treated", percent_treated)
                            p.SetField("basin_eia_treated", eia_treated)

                            pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)
                            pvb = self.pv_benefit(b, technology)
                            npv = pvb - pvc

                            p.SetField("pv_cost", pvc)
                            p.SetField("pv_benefit", pvb)
                            p.SetField("npv", npv)

                            if self.budget_source == "pvcosts":
                                self.__totalCost += pvc
                            else:
                                self.__totalCost += cost

                            self.__totalBenefit += b
                            print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                            print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                conArea)
                            print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                b) + ' budget: ', str(remaining_budget)
                            # print str(self.technologies[self.tech])
                            # print random_number
                            # full_budget -= cost
                            # if a pracel in this block has had a wsud, add eia_treated to existing eia_treated,
                            # otherwise add the to the new eia_treated
                            if block_id in blocks:
                                blocks[block_id] += eia_treated
                            else:
                                blocks[block_id] = eia_treated

                            # blocks[block_id] = eia_treated

                if decision_rule == 3 and released < 2000:
                    bmps = ["raingarden", "wetland", "pond"]
                    dict_required_area = {}
                    if block_id in blocks:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * (
                        imperviousCatchment - blocks[block_id])
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.design_curves(self.expected_removal, technology) * area
                    else:
                        for i in bmps:
                            dict_required_area[i] =  self.design_curves(self.expected_removal, i) * imperviousCatchment

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
                                N_removed = self.n_removed(dict_conv_area[i]/self.design_curves(self.expected_removal, i), runoff)
                                b = self.benefit_fun(offset_rate, N_removed)
                                pvb = self.pv_benefit(b, i)
                                benefits[i]= pvb-pvc
                            technology = max(benefits)
                        # Otherwise select the only option available
                            conArea = dict_conv_area[technology]
                            # percent_treated = conArea / dict_required_area[technology]

                            cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                            opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                            if cost <= remaining_budget:
                                # print 'cost is within budget'
                                # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}
                                eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                                percent_treated = eia_treated / imperviousCatchment
                                # b = self.benefitdic[self.technologies[self.tech]]
                                # removal = self.__removalRate[technology]

                                N_removed = self.n_removed(eia_treated, runoff)
                                b = self.benefit_fun(offset_rate, N_removed)

                                p.SetField("new_landuse", technology)
                                p.SetField("N_removed", N_removed)
                                p.SetField("nrem_benefit", b)
                                p.SetField("cost", cost)
                                p.SetField("temp_cost", cost)
                                p.SetField("OPEX", opex)
                                p.SetField("installation_year", year)
                                p.SetField("conv_area", conArea)
                                p.SetField("ownership", "public")
                                p.SetField("random_nmr", random_nmr)
                                p.SetField("basin_percent_treated", percent_treated)
                                p.SetField("basin_eia_treated", eia_treated)

                                if technology in ["pond", "wetland"]:
                                    irri_supply = min(irrigation_demand, runoff * eia_treated)
                                    irri_benefit = irri_supply * 2.66
                                else:
                                    irri_supply = 0
                                    irri_benefit = 0
                                p.SetField("irrigation_supply", irri_supply)

                                pvb_nrem = self.pv_benefit(b, technology)
                                pvb_irri = self.pv_benefit(irri_benefit, technology)
                                pvb_total = pvb_nrem + pvb_irri
                                pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)

                                npv = pvb_total - pvc

                                p.SetField("pv_cost", pvc)
                                p.SetField("pv_benefit_nrem", pvb_nrem)
                                p.SetField("pv_benefit_irri", pvb_irri)
                                p.SetField("pv_benefit_total", pvb_total)
                                p.SetField("npv", npv)

                                # blocks[block_id] = percent_treated
                                if self.budget_source == "pvcosts":
                                    self.__totalCost += pvc
                                else:
                                    self.__totalCost += cost
                                self.__totalBenefit += b
                                print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                    conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                    b) + ' budget: ', str(remaining_budget)

                                # full_budget -= cost
                                # if a pracel in this block has had a wsud, add eia_treated to existing eia_treated,
                                # otherwise add the to the new eia_treated
                                if block_id in blocks:
                                    blocks[block_id] += eia_treated
                                else:
                                    blocks[block_id] = eia_treated

                                # blocks[block_id] = eia_treated

                if decision_rule == 4 and released < 2000:
                    bmps = ["raingarden", "wetland", "pond"]
                    dict_required_area = {}
                    if block_id in blocks:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * (
                        imperviousCatchment - blocks[block_id])
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.design_curves(self.expected_removal, technology) * area
                    else:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * imperviousCatchment

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
                                # print 'cost is within budget'
                                # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}
                                eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                                percent_treated = eia_treated / imperviousCatchment
                                # b = self.benefitdic[self.technologies[self.tech]]
                                # removal = self.__removalRate[technology]

                                N_removed = self.n_removed(eia_treated, runoff)
                                b = self.benefit_fun(offset_rate, N_removed)

                                p.SetField("new_landuse", technology)
                                p.SetField("N_removed", N_removed)
                                p.SetField("nrem_benefit", b)
                                p.SetField("cost", cost)
                                p.SetField("temp_cost", cost)
                                p.SetField("OPEX", opex)
                                p.SetField("installation_year", year)
                                p.SetField("conv_area", conArea)
                                p.SetField("ownership", "public")

                                p.SetField("basin_percent_treated", percent_treated)
                                p.SetField("basin_eia_treated", eia_treated)

                                pvb = self.pv_benefit(b, technology)
                                npv = pvb - pvc

                                p.SetField("pv_cost", pvc)
                                p.SetField("pv_benefit", pvb)
                                p.SetField("npv", npv)

                                # blocks[block_id] = percent_treated
                                if self.budget_source == "pvcosts":
                                    self.__totalCost += pvc
                                else:
                                    self.__totalCost += cost
                                self.__totalBenefit += b
                                print technology, 'PVB, PVC, NPV: ', str(pvb), str(pvc), str(npv)
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                    conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                    b) + ' budget: ', str(remaining_budget)

                                # full_budget -= cost
                                # if a pracel in this block has had a wsud, add eia_treated to existing eia_treated,
                                # otherwise add the to the new eia_treated
                                if block_id in blocks:
                                    blocks[block_id] += eia_treated
                                else:
                                    blocks[block_id] = eia_treated

                                # blocks[block_id] = eia_treated

                if decision_rule == 5 and released < 2000:
                    bmps = ["raingarden", "wetland", "pond"]
                    dict_required_area = {}
                    if block_id in blocks:
                        for i in bmps:
                            dict_required_area[i] = self.design_curves(self.expected_removal, i) * (
                        imperviousCatchment - blocks[block_id])
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.design_curves(self.expected_removal, technology) * area
                    else:
                        for i in bmps:
                            dict_required_area[i] =  self.design_curves(self.expected_removal, i) * imperviousCatchment

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
                                N_removed = self.n_removed(dict_conv_area[i]/self.design_curves(self.expected_removal, i), runoff)
                                b = self.benefit_fun(offset_rate, N_removed)
                                if i in ["pond", "wetland"]:
                                    irri_supply = min(irrigation_demand,runoff*dict_conv_area[i]/self.design_curves(self.expected_removal, i))
                                    tb = b + irri_supply*2.66
                                else:
                                    irri_supply = 0
                                    tb = b
                                pvb = self.pv_benefit(tb, i)
                                benefits[i]= pvb-pvc
                            technology = max(benefits)
                        # Otherwise select the only option available
                            conArea = dict_conv_area[technology]
                            # percent_treated = conArea / dict_required_area[technology]

                            cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                            opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                            if cost <= remaining_budget:
                                # print 'cost is within budget'
                                # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}
                                eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                                percent_treated = eia_treated / imperviousCatchment
                                # b = self.benefitdic[self.technologies[self.tech]]
                                # removal = self.__removalRate[technology]

                                N_removed = self.n_removed(eia_treated, runoff)
                                b = self.benefit_fun(offset_rate, N_removed)

                                p.SetField("new_landuse", technology)
                                p.SetField("N_removed", N_removed)
                                p.SetField("nrem_benefit", b)
                                p.SetField("cost", cost)
                                p.SetField("temp_cost", cost)
                                p.SetField("OPEX", opex)
                                p.SetField("installation_year", year)
                                p.SetField("conv_area", conArea)
                                p.SetField("ownership", "public")
                                p.SetField("random_nmr", random_nmr)

                                p.SetField("basin_percent_treated", percent_treated)
                                p.SetField("basin_eia_treated", eia_treated)
                                p.SetField("irrigation_supply", irri_supply)

                                if technology in ["pond", "wetland"]:
                                    irri_supply = min(irrigation_demand, runoff * eia_treated)
                                    irri_benefit = irri_supply * 2.66
                                else:
                                    irri_benefit = 0

                                pvb_nrem = self.pv_benefit(b, technology)
                                pvb_irri = self.pv_benefit(irri_benefit, technology)
                                pvb_total = pvb_nrem + pvb_irri

                                p.SetField("pv_benefit_nrem", pvb_nrem)
                                p.SetField("pv_benefit_irri", pvb_irri)
                                p.SetField("pv_benefit_total", pvb_total)

                                pvc =  self.pv_total_costs(year, technology, conArea, self.cost_source)

                                npv = pvb_total - pvc

                                p.SetField("pv_cost", pvc)
                                p.SetField("npv", npv)

                                # blocks[block_id] = percent_treated
                                if self.budget_source == "pvcosts":
                                    self.__totalCost += pvc
                                else:
                                    self.__totalCost += cost
                                self.__totalBenefit += b
                                print technology, 'PVB, PVC, NPV: ', str(pvb_total), str(pvc), str(npv)
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                    conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                    b) + ' budget: ', str(remaining_budget)

                                # full_budget -= cost
                                # if a pracel in this block has had a wsud, add eia_treated to existing eia_treated,
                                # otherwise add the to the new eia_treated
                                if block_id in blocks:
                                    blocks[block_id] += eia_treated
                                else:
                                    blocks[block_id] = eia_treated


            self.__totalCost = 0
            self.__totalBenefit = 0
            self.parcel.finalise()
