__author__ = 'acharett'

from pydynamind import *
from osgeo import ogr
import random
import numpy as np

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

            self.createParameter("service_life", DOUBLE)
            self.service_life = 50

            self.createParameter("discount_rate", DOUBLE)
            self.discount_rate = 0.05

            self.__years = []
            self.__discount_factor = []
            for y in xrange(1, int(self.service_life) + 1, 1):
                self.__years.append(y)
                self.__discount_factor.append(1. / (1. + self.discount_rate) ** (y - 1))

            self.__cpi = {2005: 73.425, 2006: 77.325, 2007: 80.175, 2008: 85.55,
                          2009: 88.65, 2010: 90.875, 2011: 97.325, 2012: 102.25}

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
            self.__rainfall = {2000: 882.5, 2001: 758, 2002: 668.7, 2003: 822.6, 2004: 820, 2005: 800.9, 2006: 643.2,
                               2007: 728, 2008: 608.2,  2009: 718.4,  2010: 1051.9, 2011: 1163.4, 2012: 907.2,
                               2013: 878.2, 2014: 695.5, 2015: 628,  2016: 896.6}

            self.__offset={2004: 800, 2005: 800, 2006: 6645, 2007: 6645, 2008: 6645, 2009: 6645, 2010: 6645,
                    2011: 6645, 2012: 6645, 2013: 6645, 2014: 6645,  2015: 6645, 2016: 6645}

            self.__totalCost = 0
            self.__totalBenefit = 0

            self.__removalRate = {'wetland': 0.61, 'pond': 0.32, 'raingarden': 0.65}
            # self.__adjustmentFactor = {'wetland': 1.2, 'pond': 1.6, 'raingarden': 1.1}

            self.__requiredSize = {'wetland': 0.024*1.2, 'pond': 0.04*1.6, 'raingarden': 0.014*1.1}

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

            self.__minArea = {"wetland": 80,
                                  "pond": 7,
                                  "raingarden": 2}



            self.parcel = ViewContainer("parcel", COMPONENT, READ)
            self.parcel.addAttribute("original_landuse", Attribute.STRING, READ)
            self.parcel.addAttribute("area", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("zone_lu", Attribute.STRING, READ)
            self.parcel.addAttribute("max_prob_technology", Attribute.STRING, READ)
            self.parcel.addAttribute("new_impervious_catchment", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("grid_id", Attribute.INT, READ)

            self.parcel.addAttribute("new_landuse", Attribute.STRING, WRITE)
            self.parcel.addAttribute("council", Attribute.STRING, READ)

            self.parcel.addAttribute("N_removed", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("benefit", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("cost", Attribute.DOUBLE, WRITE)
            # self.parcel.addAttribute("avg_wtp_stream", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("decision_rule", Attribute.INT, READ)

            # self.parcel.addAttribute("random", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("year", Attribute.INT, READ)
            self.parcel.addAttribute("budget", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("prob_rg", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_pond", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_wetland", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("convArea", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("percent_treated", Attribute.DOUBLE, WRITE)

            self.parcel.addAttribute("installation_year", Attribute.INT, WRITE)
            self.parcel.addAttribute("OPEX", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("temp_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("npv", Attribute.DOUBLE, WRITE)


            #Compile views
            views = []
            views.append(self.parcel)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def const_cost(self, technology, area, year):
            if technology == 'wetland':
                cost = 1911 * area ** 0.6435
            elif technology == 'raingarden':
                cost = area * 6023.1 * area ** -0.46
            elif technology == 'pond':
                cost = 685.1 * area ** 0.7893
            return cost* self.__cpi[year] / self.__cpi[2012]

        def inv_cost(self, technology, budget):
            if technology == 'wetland':
                area = 0.00000796*(budget ** 1.554001554)
            elif technology == 'raingarden':
                area = 0.0000001*(budget**1.85185185185)
            elif technology == 'pond':
                area = 0.00025546 * (budget ** 1.266945394653)
            return area

        def maint_cost(self, technology, area, year):
            if technology == 'wetland':
                cost = area * 1289.7 * area ** -0.794
            elif technology == 'raingarden':
                cost = area * 199.19 * area ** -0.551
            elif technology == 'pond':
                if area < 250:
                    cost = 18 * area
                elif 250 <= area < 500:
                    cost = 12 * area
                elif 500 <= area < 1500:
                    cost = 5 * area
                elif 1500 <= area:
                    cost = 2 * area

            mcost = cost* self.__cpi[year] / self.__cpi[2012]

            maintenance_cost = []
            for y in self.__years:
                maintenance_cost.append(mcost)

            discount_maintenance_cost = [(d * m) for d, m in zip(self.__discount_factor, maintenance_cost)]

            return sum(discount_maintenance_cost)



        def n_removed(self, area, rem_rate, runoff):
            n = rem_rate * runoff * 0.002 * area
            return n

        def benefit_fun(self, n_removed):
            b = 6645 * n_removed
            return b

        def pv_total_costs(self, year, technology, area):
            try:
                return self.const_cost(technology, area, year) + self.maint_cost(technology, area,year)
            except (LookupError):
                raise ValueError("can't calculate total costs")

        def pv_benefit(self, n_removed):
            b = self.benefit_fun(n_removed)
            benefit_list = []
            for y in self.__years:
                benefit_list.append(b)
            discount_n_removal = [(d * b) for d, b in zip(self.__discount_factor, benefit_list)]

            return sum(discount_n_removal)


        def run(self):
            #Data Stream Manipulation
            self.parcel.reset_reading()

            grids = {}
            for p in self.parcel:

                # Load full annual budget and all other values
                full_budget = p.GetFieldAsDouble("budget")
                council = p.GetFieldAsString("council")

                year = p.GetFieldAsInteger("year")
                decision_rule = p.GetFieldAsInteger("decision_rule")

                landuse = p.GetFieldAsString("original_landuse")
                newlanduse = p.GetFieldAsString("new_landuse")
                zone_lu = p.GetFieldAsString("zone_lu")
                imperviousCatchment = p.GetFieldAsDouble("new_impervious_catchment")
                grid_id = p.GetFieldAsInteger("grid_id")


                area = p.GetFieldAsDouble("area")
                # loss_aversion = p.GetFieldAsDouble("loss_aversion")
                prob_rg = p.GetFieldAsDouble("prob_rg")
                prob_wl = p.GetFieldAsDouble("prob_wetland")
                prob_pd = p.GetFieldAsDouble("prob_pond")
                max_prob_technology = p.GetFieldAsString("max_prob_technology")

                # Substract current cumulative costs from full budget
                full_budget -= self.__totalCost

                # Estimate runoff for current year
                runoff = self.__rainfall[year] * 0.9 * 0.20

                ### Strategy 1: Chose technology with highest probability ###
                if decision_rule == 1:

                    technology = max_prob_technology

                    if grid_id in grids:
                        requiredArea = self.__requiredSize[technology] * (imperviousCatchment - grids[grid_id]*imperviousCatchment)
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.__requiredSize[technology] * area
                    else:
                        requiredArea = self.__requiredSize[technology] * imperviousCatchment

                    if requiredArea > area:
                        conArea = area
                    else:
                        conArea = requiredArea

                    # if landuse has not yet been converted AND available area is larger than minimum area and landuse is suitable
                    if landuse == newlanduse and conArea >= self.__minArea[technology] and zone_lu in self.__suitable_zoneLu[technology]:
                        'Criteria are met'
                        # define the area

                        percent_treated = conArea / requiredArea

                        cost = self.const_cost(technology, conArea, year)
                        opex = self.maint_cost(technology, conArea, year)

                        if cost <= full_budget:
                            # print 'cost is within budget'
                            # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}

                            # b = self.benefitdic[self.technologies[self.tech]]
                            removal = self.__removalRate[technology]
                            N_removed = self.n_removed(conArea,removal, runoff)
                            b = self.benefit_fun(N_removed)

                            p.SetField("new_landuse", technology)
                            p.SetField("N_removed", N_removed)
                            p.SetField("benefit", b)
                            p.SetField("cost", cost)
                            p.SetField("temp_cost", cost)
                            p.SetField("OPEX", opex)
                            p.SetField("installation_year", year)
                            p.SetField("convArea", conArea)
                            p.SetField("percent_treated", percent_treated)
                            grids[grid_id] = percent_treated
                            self.__totalCost += cost
                            self.__totalBenefit += b

                            pvc = self.pv_total_costs(year, technology, conArea)
                            pvb = self.pv_benefit(b)
                            npv = pvb - pvc

                            p.SetField("pv_cost", pvc)
                            p.SetField("pv_benefit", pvb)
                            p.SetField("npv", npv)

                            print technology
                            print 'Council: ', council, 'Year: ' ,str(year), ' area: ' , str(area) ,'conArea: ' , str(conArea)
                            print ' cost: ',str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(b)+' budget: ', str(full_budget)
                            # print str(self.technologies[self.tech])
                            # print random_number
                            full_budget -= cost
                            # p.SetField("budget_remaining", full_budget)

                        # else:
                        #     print 'The cost is above budget', full_budget, random_number
                        #     p.SetField("budget_remaining", full_budget
                    #     else:
                    #         print 'cost is over the budget'
                    #         print 'Total cost: ', str(self.__totalCost), ' cost= ', str(cost), ' budget: ', str(full_budget)
                    # else:
                    #     print 'Criteria are not met'
                    #     print landuse, newlanduse
                    #     print "Area: ", str(area), " Min. area: ", str(self.__minArea[technology])
                    #     print zone_lu, str(zone_lu in self.__suitable_zoneLu[technology])

                ### Strategy 2: Whole budget is spent on most likely parcel
                if decision_rule == 2:

                    technology = max_prob_technology

                    # If a parcel within this grid has already been converted, the impervious catchment already treated
                    # from the previous technology is substracted from the total impervious catchment
                    if grid_id in grids:
                        requiredArea = self.__requiredSize[technology] * (
                        imperviousCatchment - grids[grid_id] * imperviousCatchment)

                    # if no existing wsud in the grid, the required area is according to design curves
                    else:
                        requiredArea = self.__requiredSize[technology] * imperviousCatchment

                    if self.inv_cost(technology, full_budget) < area and self.inv_cost(technology, full_budget) < requiredArea:
                        conArea = self.inv_cost(technology, full_budget)
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
                        percent_treated = conArea / requiredArea

                        cost = self.const_cost(technology, conArea, year)
                        opex = self.maint_cost(technology, conArea, year)

                        if cost <= full_budget:
                            # print 'cost is within budget'
                            # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}

                            # b = self.benefitdic[self.technologies[self.tech]]
                            removal = self.__removalRate[technology]
                            N_removed = self.n_removed(conArea, removal, runoff)
                            b = self.benefit_fun(N_removed)

                            p.SetField("new_landuse", technology)
                            p.SetField("N_removed", N_removed)
                            p.SetField("benefit", b)
                            p.SetField("cost", cost)
                            p.SetField("temp_cost", cost)
                            p.SetField("OPEX", opex)
                            p.SetField("installation_year", year)
                            p.SetField("convArea", conArea)
                            p.SetField("percent_treated", percent_treated)
                            grids[grid_id] = percent_treated
                            pvc = self.pv_total_costs(year, technology, conArea)
                            pvb = self.pv_benefit(b)
                            npv = pvb - pvc

                            p.SetField("pv_cost", pvc)
                            p.SetField("pv_benefit", pvb)
                            p.SetField("npv", npv)

                            self.__totalCost += cost
                            self.__totalBenefit += b
                            print technology
                            print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                conArea)
                            print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                b) + ' budget: ', str(full_budget)
                            # print str(self.technologies[self.tech])
                            # print random_number
                            full_budget -= cost

                if decision_rule == 3:

                    dict_required_area = {}
                    if grid_id in grids:
                        for i in self.__requiredSize:
                            dict_required_area[i] = self.__requiredSize[i] * (
                        imperviousCatchment - grids[grid_id] * imperviousCatchment)
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.__requiredSize[technology] * area
                    else:
                        for i in self.__requiredSize:
                            dict_required_area[i] = self.__requiredSize[i] * imperviousCatchment

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
                        benefits = {}
                        if len(list_installed_tech) >= 1:
                            print "More than one option available"
                            for i in list_installed_tech:
                                pvc = self.pv_total_costs(year, i, dict_conv_area[i])

                                removal = self.__removalRate[i]
                                N_removed = self.n_removed(dict_conv_area[i], removal, runoff)
                                b = self.benefit_fun(N_removed)
                                pvb = self.pv_benefit(b)
                                benefits[i]= pvb-pvc
                            technology = max(benefits)
                        # Otherwise select the only option available
                            conArea = dict_conv_area[technology]
                            percent_treated = conArea / dict_required_area[technology]

                            cost = self.const_cost(technology, conArea, year)
                            opex = self.maint_cost(technology, conArea, year)

                            if cost <= full_budget:
                                # print 'cost is within budget'
                                # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}

                                # b = self.benefitdic[self.technologies[self.tech]]
                                removal = self.__removalRate[technology]
                                N_removed = self.n_removed(conArea, removal, runoff)
                                b = self.benefit_fun(N_removed)

                                p.SetField("new_landuse", technology)
                                p.SetField("N_removed", N_removed)
                                p.SetField("benefit", b)
                                p.SetField("cost", cost)
                                p.SetField("temp_cost", cost)
                                p.SetField("OPEX", opex)
                                p.SetField("installation_year", year)
                                p.SetField("convArea", conArea)
                                p.SetField("percent_treated", percent_treated)

                                npv = pvb - pvc

                                p.SetField("pv_cost", pvc)
                                p.SetField("pv_benefit", pvb)
                                p.SetField("npv", npv)
                                grids[grid_id] = percent_treated
                                self.__totalCost += cost
                                self.__totalBenefit += b
                                print technology
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                    conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                    b) + ' budget: ', str(full_budget)

                                full_budget -= cost

                if decision_rule == 4:

                    dict_required_area = {}
                    if grid_id in grids:
                        for i in self.__requiredSize:
                            dict_required_area[i] = self.__requiredSize[i] * (
                        imperviousCatchment - grids[grid_id] * imperviousCatchment)
                    # elif imperviousCatchment == 0:
                    #     requiredArea = self.__requiredSize[technology] * area
                    else:
                        for i in self.__requiredSize:
                            dict_required_area[i] = self.__requiredSize[i] * imperviousCatchment

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
                            print "More than one option available"
                            for i in list_installed_tech:
                                pvc = self.pv_total_costs(year, i, dict_conv_area[i])
                                costs[i] = pvc
                            technology = min(costs)
                        # Otherwise select the only option available
                            conArea = dict_conv_area[technology]
                            percent_treated = conArea / requiredArea

                            cost = self.const_cost(technology, conArea, year)
                            opex = self.maint_cost(technology, conArea, year)

                            if cost <= full_budget:
                                # print 'cost is within budget'
                                # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}

                                # b = self.benefitdic[self.technologies[self.tech]]
                                removal = self.__removalRate[technology]
                                N_removed = self.n_removed(conArea, removal, runoff)
                                b = self.benefit_fun(N_removed)

                                p.SetField("new_landuse", technology)
                                p.SetField("N_removed", N_removed)
                                p.SetField("benefit", b)
                                p.SetField("cost", cost)
                                p.SetField("temp_cost", cost)
                                p.SetField("OPEX", opex)
                                p.SetField("installation_year", year)
                                p.SetField("convArea", conArea)
                                p.SetField("percent_treated", percent_treated)

                                pvb = self.pv_benefit(b)
                                npv = pvb - pvc

                                p.SetField("pv_cost", pvc)
                                p.SetField("pv_benefit", pvb)
                                p.SetField("npv", npv)

                                grids[grid_id] = percent_treated
                                self.__totalCost += cost
                                self.__totalBenefit += b
                                print technology
                                print 'Council: ', council, 'Year: ', str(year), ' area: ', str(area), 'conArea: ', str(
                                    conArea)
                                print ' cost: ', str(cost), ' total cost: ', str(self.__totalCost), ' benefit: ', str(
                                    b) + ' budget: ', str(full_budget)

                                full_budget -= cost


            self.__totalCost = 0
            self.__totalBenefit = 0
            self.parcel.finalise()