__author__ = 'acharett'

from pydynamind import *
from osgeo import ogr
import random
import numpy as np

class test_Heuristics(Module):
        display_name = "test_Heuristics"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)

            self.createParameter("rule", INT)
            self.rule = 1

            self.parcel = ViewContainer("parcel", COMPONENT, READ)
            self.parcel.addAttribute("original_landuse", Attribute.STRING, READ)
            self.parcel.addAttribute("area", Attribute.INT, READ)
            # self.parcel.addAttribute("flooded", Attribute.INT, READ)
            self.parcel.addAttribute("new_landuse", Attribute.STRING, WRITE)
            self.parcel.addAttribute("council", Attribute.STRING, WRITE)

            self.parcel.addAttribute("benefit", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("cost", Attribute.DOUBLE, WRITE)
            # self.parcel.addAttribute("avg_wtp_stream", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("decision_rule", Attribute.INT, READ)

            self.parcel.addAttribute("random", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("year", Attribute.INT, READ)
            self.parcel.addAttribute("budget", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("loss_aversion", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("prob_sedimentation", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_raingarden", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("prob_wetland", Attribute.DOUBLE, READ)

            self.parcel.addAttribute("installation_year", Attribute.INT, WRITE)
            self.parcel.addAttribute("OPEX", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("temp_cost", Attribute.DOUBLE, WRITE)

            self.total_cost = 0
            self.total_benefit = 0

            #Compile views
            views = []
            views.append(self.parcel)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            suitable_zoneLu = {"wetland": ["GRZ1_Unclassified Private Land", "GRZ2_Unclassified Private Land",
                                         "PCRZ_Nature Reserve","PCRZ_Unclassified Private Land",
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
                                            "GRZ1_Vacant Residential Home Site / Surveyed Lot", "GRZ2_Road Void",
                                            "GRZ2_Unclassified Private Land", "GRZ3_Road Void",
                                            "GRZ3_Unclassified Private Land",
                                            "GWAZ1_Detached Home", "GWAZ1_Road Void", "LDRZ_Road Void",
                                            "LDRZ_Unclassified Private Land",
                                            "MUZ_Road Void", "MUZ_Unclassified Private Land", "NRZ3_Road Void",
                                            "NRZ3_Unclassified Private Land",
                                            "PPRZ_Community Service Facilities or Other", "PPRZ_Member Club Facility",
                                            "PPRZ_Protected Seascape - Public", "PPRZ_Reserved Land",
                                            "PPRZ_Unclassified Private Land", "PUZ1_Unclassified Private Land",
                                            "PUZ4_Road Void",
                                            "PUZ6_Community Service Facilities or Other", "PUZ6_Road Void",
                                            "PUZ6_Unclassified Private Land",
                                            "R1Z_Community Service Facilities or Other", "R1Z_Road Void",
                                            "RDZ1_Road Void", "RDZ2_Road Void", "RGZ1_Road Void",
                                            "SUZ1_Road Void", "SUZ2_Unclassified Private Land", "UFZ_Road Void",
                                            "UFZ_Unclassified Private Land"],
                               "pond": ["GRZ1_Vacant Residential Home Site / Surveyed Lot",
                                      "GRZ2_Unclassified Private Land", "GRZ2_Vacant Land mining unspecified",
                                      "IN1Z_Unclassified Private Land", "NA_Reserved Land", "PCRZ_Nature Reserve",
                                      "PCRZ_Reserved Land",
                                      "PPRZ_Community Service Facilities or Other", "PPRZ_Unclassified Private Land"]}
            # Nitrogen removal benefit function
            rainfall={2000: 882.5,
                      2001: 758,
                      2002: 668.7,
                      2003: 822.6,
                      2004: 820,
                      2005: 800.9,
                      2006: 643.2,
                      2007: 728,
                      2008: 608.2,
                      2009: 718.4,
                      2010: 1051.9,
                      2011: 1163.4,
                      2012: 907.2,
                      2013: 878.2,
                      2014: 695.5,
                      2015: 628,
                      2016: 896.6}

            offset={  2004: 800,
                      2005: 800,
                      2006: 6645,
                      2007: 6645,
                      2008: 6645,
                      2009: 6645,
                      2010: 6645,
                      2011: 6645,
                      2012: 6645,
                      2013: 6645,
                      2014: 6645,
                      2015: 6645,
                      2016: 6645}

            removal_rate = {'wetland': 0.61, 'sedimentation': 0.32, 'raingarden': 0.65}
            def benefit_fun(area,rem_rate, runoff):
                b = 6645* rem_rate*runoff*0.002*area
                return b


            # self.total_cost = 0
            self.total_cost = {"BAYSIDE" : 0,
                               "MONASH" : 0,
                               "PORT PHILLIP": 0,
                               "KINGSTON": 0,
                               "GLEN EIRA": 0,
                               "STONNINGTON": 0
                               }
            self.total_benefit = {"BAYSIDE" : 0,
                               "MONASH" : 0,
                               "PORT PHILLIP": 0,
                               "KINGSTON": 0,
                               "GLEN EIRA": 0,
                               "STONNINGTON": 0
                               }

            self.parcel.reset_reading()
            for p in self.parcel:

                # Load full annual budget
                full_budget = p.GetFieldAsDouble("budget")
                council = p.GetFieldAsString("council")

                # Substract current costs from full budget
                full_budget -= self.total_cost[council]

                year = p.GetFieldAsInteger("year")
                decision_rule = p.GetFieldAsInteger("decision_rule")
                runoff = rainfall[year] * 0.9 * 0.20

                landuse = p.GetFieldAsString("original_landuse")
                newlanduse = p.GetFieldAsString("new_landuse")
                area = p.GetFieldAsDouble("area")
                loss_aversion = p.GetFieldAsDouble("loss_aversion")
                prob_rg = p.GetFieldAsDouble("prob_raingarden")
                prob_wl = p.GetFieldAsDouble("prob_wetland")
                prob_sd = p.GetFieldAsDouble("prob_sedimentation")




                # Set of suitable landuses
                landuses = ["PPRZ","PCRZ","PDZ2","PUZ1", "PUZ2", "PUZ4" ,"PUZ6","PUZ7"]

                # if landuse is suitable and if the parcel has not yet been coverted
                if landuse in landuses and landuse == newlanduse:

                    ## Strategy 1: randomly chosen with random area and random budget ###
                    if decision_rule == 1:

                        # Choose a random technology

                        con_area= area





                        if int(area) > 2300:
                            self.tech = random.randrange(1,3)
                            self.technologies = {1:'wetland', 2:'sedimentation'}

                            # If technology is wetland
                            if self.tech == 1:
                                if 10000 > con_area > 500:
                                    self.cost= (100*con_area)
                                    opex= 2*con_area
                                elif con_area > 10000:
                                    self.cost= (75*con_area)
                                    opex= 0.5*con_area

                            # If technology is Sedimentation pond
                            elif self.tech == 2:
                                self.cost= (150*con_area)
                                opex= 5*con_area

                        elif 2300 >= int(area) > 80:
                            # Choose a random area to be converted, from min 25 m2 to max total area of parcel
                            con_area= area

                            # Calculate capital cost
                            self.tech = random.randrange(1,4)
                            self.technologies = {1:'wetland', 2:'sedimentation', 3:'raingarden'}

                            ### If technology is wetland
                            if self.tech == 1:
                                if 500 > con_area >= 300:
                                    self.cost= 150*con_area
                                    opex= 10*con_area
                                elif 10000 > con_area > 500:
                                    self.cost= (100*con_area)
                                    opex= 2*con_area
                                elif con_area > 10000:
                                    self.cost= (75*con_area)
                                    opex= 0.5*con_area

                            ### If technology is Sedimentation Pond
                            elif self.tech == 2:
                                if 250 > con_area >= 25:
                                    self.cost= (250*con_area)
                                    opex= 20*con_area

                                elif 1000 > con_area > 250:
                                    self.cost= (200*con_area)
                                    opex= 10*con_area
                                elif con_area > 1000:
                                    self.cost= (150*con_area)
                                    opex= 5*con_area

                            ### If technology is raingarden
                            elif self.tech == 3:
                                if 100 > con_area >= 25:
                                    self.cost= (1000*con_area)
                                elif 500 > con_area > 100:
                                    self.cost= (350*con_area)
                                elif con_area > 500:
                                    self.cost= (250*con_area)
                                opex= 5*con_area


                        elif 80 >= int(area) > 56:
                            self.tech = random.randrange(1,3)
                            self.technologies = {1:'sedimentation', 2:'raingarden'}

                             ### If technology is Sedimentation Pond
                            if self.tech == 1:
                                if 250 > con_area >= 25:
                                    self.cost= (250*con_area)
                                    opex= 20*con_area

                             ### If technology is raingarden
                            elif self.tech == 2:
                                if 100 > con_area >= 2:
                                    self.cost= (1000*con_area)
                                    opex= 5*con_area

                        elif 56 >= int(area) >= 2:
                            self.tech = random.randrange(1,2)
                            self.technologies = {1:'raingarden'}
                            self.cost= (1000*con_area)
                            opex= 5*con_area
                        # print self.cost, full_budget
                        if self.cost <= full_budget:

                            # self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}
                            test = self.technologies[self.tech]

                            # b = self.benefitdic[self.technologies[self.tech]]
                            removal = removal_rate[self.technologies[self.tech]]
                            b = benefit_fun(area,removal, runoff)


                            p.SetField("new_landuse", test)
                            p.SetField("benefit", b)
                            p.SetField("cost", self.cost)
                            p.SetField("temp_cost", self.cost)
                            p.SetField("OPEX", opex)
                            p.SetField("installation_year", year)
                            self.total_cost[council] += self.cost
                            self.total_benefit[council] += b
                            print 'Council: ', council, 'Year: ' ,str(year), ' area: ' , str(con_area) ,' cost: ',str(self.cost), ' total cost: ', str(self.total_cost[council]), ' benefit: ', str(b)+' budget: ', str(full_budget)
                            print str(self.technologies[self.tech])
                            # print random_number
                            full_budget -= self.cost
                            # p.SetField("budget_remaining", full_budget)

                        # else:
                        #     print 'The cost is above budget', full_budget, random_number
                            # p.SetField("budget_remaining", full_budget)
                    #
                    elif decision_rule == 2:



                        if area >10000:
                            # wetland_area = np.random.triangular(9, 250, 2630)
                            # raingarden_area = np.random.triangular(2, 176, 506)
                            # sedimentation_area = np.random.triangular(9, 230, 469)

                            ann_cost_wetland = (75*area)/(1*(1/(1+0.07)**20)/0.07)+0.5*area
                            cost_wetland = (75*area)

                            ann_cost_sedimentation = (150*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_sedimentation = (150*area)

                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland, 'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 0.5, 'sedimentation': 5}
                            OPEX = opex_dict[best_option]*area


                        elif 10000 >= area > 2300:
                            ann_cost_wetland = (100*area)/(1*(1/(1+0.07)**20)/0.07)+2*area
                            cost_wetland = (100*area)

                            ann_cost_sedimentation = (150*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_sedimentation = (150*area)

                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland, 'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 5}
                            OPEX = opex_dict[best_option]*area


                        elif 2300 >= area > 1000:
                            ann_cost_wetland = (100*area)/(1*(1/(1+0.07)**20)/0.07)+2*area
                            cost_wetland = (100*area)

                            ann_cost_sedimentation = (150*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_sedimentation = (150*area)

                            ann_cost_raingarden = (250*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (250*area)


                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland,
                                       'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation,
                                       'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 5, 'raingarden': 5}
                            OPEX = opex_dict[best_option]*area


                        elif 1000 >= area > 500:
                            ann_cost_wetland = (100*area)/(1*(1/(1+0.07)**20)/0.07)+2*area
                            cost_wetland = (100*area)

                            ann_cost_sedimentation = (200*area)/(1*(1/(1+0.07)**20)/0.07)+10*area
                            cost_sedimentation = (200*area)

                            ann_cost_raingarden = (250*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (250*area)


                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland,
                                       'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation,
                                       'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 10, 'raingarden': 5}
                            OPEX = opex_dict[best_option]*area

                        elif 500 >= area > 250:
                            ann_cost_wetland = (150*area)/(1*(1/(1+0.07)**20)/0.07)+10*area
                            cost_wetland = (150*area)

                            ann_cost_sedimentation = (200*area)/(1*(1/(1+0.07)**20)/0.07)+10*area
                            cost_sedimentation = (200*area)

                            ann_cost_raingarden = (350*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (350*area)

                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland,
                                       'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation,
                                       'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 10, 'raingarden': 5}
                            OPEX = opex_dict[best_option]*area

                        elif 250 >= area > 100:
                            ann_cost_wetland = (150*area)/(1*(1/(1+0.07)**20)/0.07)+10*area
                            cost_wetland = (150*area)

                            ann_cost_sedimentation = (250*area)/(1*(1/(1+0.07)**20)/0.07)+20*area
                            cost_sedimentation = (250*area)

                            ann_cost_raingarden = (350*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (350*area)

                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland,
                                       'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation,
                                       'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option]*area

                        elif 100 >= area > 80:
                            ann_cost_wetland = (150*area)/(1*(1/(1+0.07)**20)/0.07)+10*area
                            cost_wetland = (150*area)

                            ann_cost_sedimentation = (250*area)/(1*(1/(1+0.07)**20)/0.07)+20*area
                            cost_sedimentation = (250*area)

                            ann_cost_raingarden = (1000*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (1000*area)

                            all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland':benefit_fun(area,removal_rate['wetland'],runoff)/ann_cost_wetland,
                                       'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation,
                                       'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option]*area

                        elif 80 >= area > 56:

                            ann_cost_sedimentation = (250*area)/(1*(1/(1+0.07)**20)/0.07)+20*area
                            cost_sedimentation = (250*area)

                            ann_cost_raingarden = (1000*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (1000*area)

                            all_ann_costs = {'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'sedimentation':benefit_fun(area,removal_rate['sedimentation'],runoff)/ann_cost_sedimentation,
                                       'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option]*area

                        elif 56 >= area > 2:

                            ann_cost_raingarden = (1000*area)/(1*(1/(1+0.07)**20)/0.07)+5*area
                            cost_raingarden = (1000*area)

                            all_ann_costs = {'raingarden':ann_cost_raingarden}
                            all_cap_costs = {'raingarden':cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'raingarden':benefit_fun(area,removal_rate['raingarden'],runoff)/ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area,removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'raingarden': 5}
                            OPEX = opex_dict[best_option]*area

                        '''If the cost is too high, there is no investment'''

                        if cost_best_option <= full_budget:
                            p.SetField("new_landuse", best_option)
                            p.SetField("benefit", benefit)
                            p.SetField("cost", cost_best_option)
                            p.SetField("temp_cost", cost_best_option)
                            p.SetField("installation_year", year)

                            p.SetField("OPEX", OPEX)
                            self.total_cost[council] += cost_best_option
                            self.total_benefit[council] += benefit
                            # print 'Year: ' + str(year)+ ' ; Converted area is: ' + str(area) +' and cost is: '+str(cost_best_option) + 'the benefit is: ' + str(b)+'the budget is: ' + str(full_budget)

                            print 'Year: ' + str(year)+ str(best_option) + ' installed for a cost of '  + str(cost_best_option)+' and total cost of ' + str(self.total_cost[council]) + ' and a benefit of '+str(benefit)
                            print 'area: '+str(area) + ' opex: ' + str(OPEX)
                            full_budget -= cost_best_option

                    elif decision_rule == 3:

                        if area > 10000:
                            # wetland_area = np.random.triangular(9, 250, 2630)
                            # raingarden_area = np.random.triangular(2, 176, 506)
                            # sedimentation_area = np.random.triangular(9, 230, 469)

                            ann_cost_wetland = (75 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 0.5 * area
                            cost_wetland = (75 * area)**loss_aversion

                            ann_cost_sedimentation = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_sedimentation = (150 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 0.5, 'sedimentation': 5}
                            OPEX = opex_dict[best_option] * area


                        elif 10000 >= area > 2300:
                            ann_cost_wetland = (100 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 2 * area
                            cost_wetland = (100 * area)**loss_aversion

                            ann_cost_sedimentation = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_sedimentation = (150 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 5}
                            OPEX = opex_dict[best_option] * area


                        elif 2300 >= area > 1000:
                            ann_cost_wetland = (100 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 2 * area
                            cost_wetland = (100 * area)**loss_aversion

                            ann_cost_sedimentation = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_sedimentation = (150 * area)**loss_aversion

                            ann_cost_raingarden = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (250 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 5, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area


                        elif 1000 >= area > 500:
                            ann_cost_wetland = (100 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 2 * area
                            cost_wetland = (100 * area)**loss_aversion

                            ann_cost_sedimentation = (200 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_sedimentation = (200 * area)**loss_aversion

                            ann_cost_raingarden = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (250 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 10, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 500 >= area > 250:
                            ann_cost_wetland = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_wetland = (150 * area)**loss_aversion

                            ann_cost_sedimentation = (200 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_sedimentation = (200 * area)**loss_aversion

                            ann_cost_raingarden = (350 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (350 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 10, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 250 >= area > 100:
                            ann_cost_wetland = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_wetland = (150 * area)**loss_aversion

                            ann_cost_sedimentation = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 20 * area
                            cost_sedimentation = (250 * area)**loss_aversion

                            ann_cost_raingarden = (350 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (350 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 100 >= area > 80:
                            ann_cost_wetland = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_wetland = (150 * area)**loss_aversion

                            ann_cost_sedimentation = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 20 * area
                            cost_sedimentation = (250 * area)**loss_aversion

                            ann_cost_raingarden = (1000 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (1000 * area)**loss_aversion

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff) / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate['sedimentation'],runoff) / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 80 >= area > 56:

                            ann_cost_sedimentation = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 20 * area
                            cost_sedimentation = (250 * area)**loss_aversion

                            ann_cost_raingarden = (1000 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (1000 * area)**loss_aversion

                            all_ann_costs = {'sedimentation': ann_cost_sedimentation, 'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'sedimentation': cost_sedimentation, 'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {
                                'sedimentation': benefit_fun(area, removal_rate['sedimentation'],runoff) / ann_cost_sedimentation,
                                'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 56 >= area > 2:

                            ann_cost_raingarden = (1000 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (1000 * area)**loss_aversion

                            all_ann_costs = {'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        '''If the cost is too high, there is no investment'''

                        if cost_best_option <= full_budget:
                            p.SetField("new_landuse", best_option)
                            p.SetField("benefit", benefit)
                            p.SetField("cost", cost_best_option)
                            p.SetField("temp_cost", cost_best_option)
                            p.SetField("installation_year", year)

                            p.SetField("OPEX", OPEX)
                            self.total_cost[council] += cost_best_option
                            self.total_benefit[council] += benefit
                            # print 'Year: ' + str(year)+ ' ; Converted area is: ' + str(area) +' and cost is: '+str(cost_best_option) + 'the benefit is: ' + str(b)+'the budget is: ' + str(full_budget)

                            print 'Year: ' + str(year) + str(best_option) + ' installed for a cost of ' + str(
                                cost_best_option) + ' and total cost of ' + str(
                                self.total_cost[council]) + ' and a benefit of ' + str(benefit)
                            print 'area: ' + str(area) + ' opex: ' + str(OPEX)
                            full_budget -= cost_best_option

                    elif decision_rule == 4:

                        if area > 10000:
                            # wetland_area = np.random.triangular(9, 250, 2630)
                            # raingarden_area = np.random.triangular(2, 176, 506)
                            # sedimentation_area = np.random.triangular(9, 230, 469)

                            ann_cost_wetland = (75 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 0.5 * area
                            cost_wetland = (75 * area)

                            ann_cost_sedimentation = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_sedimentation = (150 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 0.5, 'sedimentation': 5}
                            OPEX = opex_dict[best_option] * area


                        elif 10000 >= area > 2300:
                            ann_cost_wetland = (100 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 2 * area
                            cost_wetland = (100 * area)

                            ann_cost_sedimentation = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_sedimentation = (150 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 5}
                            OPEX = opex_dict[best_option] * area


                        elif 2300 >= area > 1000:
                            ann_cost_wetland = (100 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 2 * area
                            cost_wetland = (100 * area)

                            ann_cost_sedimentation = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_sedimentation = (150 * area)

                            ann_cost_raingarden = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (250 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area,
                                                                 removal_rate['raingarden'],runoff)*prob_rg / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 5, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area


                        elif 1000 >= area > 500:
                            ann_cost_wetland = (100 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 2 * area
                            cost_wetland = (100 * area)

                            ann_cost_sedimentation = (200 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_sedimentation = (200 * area)

                            ann_cost_raingarden = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (250 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area,
                                                                 removal_rate['raingarden'],runoff)*prob_rg / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 2, 'sedimentation': 10, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 500 >= area > 250:
                            ann_cost_wetland = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_wetland = (150 * area)

                            ann_cost_sedimentation = (200 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_sedimentation = (200 * area)

                            ann_cost_raingarden = (350 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (350 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area,
                                                                 removal_rate['raingarden'],runoff)*prob_rg / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 10, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 250 >= area > 100:
                            ann_cost_wetland = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_wetland = (150 * area)

                            ann_cost_sedimentation = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 20 * area
                            cost_sedimentation = (250 * area)

                            ann_cost_raingarden = (350 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (350 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area,
                                                                 removal_rate['raingarden'],runoff)*prob_rg / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 100 >= area > 80:
                            ann_cost_wetland = (150 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 10 * area
                            cost_wetland = (150 * area)

                            ann_cost_sedimentation = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 20 * area
                            cost_sedimentation = (250 * area)

                            ann_cost_raingarden = (1000 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (1000 * area)

                            all_ann_costs = {'wetland': ann_cost_wetland, 'sedimentation': ann_cost_sedimentation,
                                             'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'wetland': cost_wetland, 'sedimentation': cost_sedimentation,
                                             'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {'wetland': benefit_fun(area, removal_rate['wetland'],runoff)*prob_wl / ann_cost_wetland,
                                       'sedimentation': benefit_fun(area,
                                                                    removal_rate[
                                                                        'sedimentation'],runoff)*prob_sd / ann_cost_sedimentation,
                                       'raingarden': benefit_fun(area,
                                                                 removal_rate['raingarden'],runoff)*prob_rg / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'wetland': 10, 'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 80 >= area > 56:

                            ann_cost_sedimentation = (250 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 20 * area
                            cost_sedimentation = (250 * area)

                            ann_cost_raingarden = (1000 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (1000 * area)

                            all_ann_costs = {'sedimentation': ann_cost_sedimentation, 'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'sedimentation': cost_sedimentation, 'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {
                                'sedimentation': benefit_fun(area,
                                                             removal_rate['sedimentation'],runoff)*prob_sd / ann_cost_sedimentation,
                                'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff)*prob_rg / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'sedimentation': 20, 'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        elif 56 >= area > 2:

                            ann_cost_raingarden = (1000 * area) / (1 * (1 / (1 + 0.07) ** 20) / 0.07) + 5 * area
                            cost_raingarden = (1000 * area)

                            all_ann_costs = {'raingarden': ann_cost_raingarden}
                            all_cap_costs = {'raingarden': cost_raingarden}

                            ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
                            options = {
                                'raingarden': benefit_fun(area, removal_rate['raingarden'],runoff) / ann_cost_raingarden}
                            best_option = max(options)
                            # print 'The best option is: ' + str(best_option)
                            cost_best_option = all_cap_costs[best_option]
                            removal = removal_rate[best_option]
                            benefit = benefit_fun(area, removal,runoff)

                            # Measure maintenance costs
                            opex_dict = {'raingarden': 5}
                            OPEX = opex_dict[best_option] * area

                        '''If the cost is too high, there is no investment'''
                        print full_budget, cost_best_option
                        if cost_best_option <= full_budget:
                            p.SetField("new_landuse", best_option)
                            p.SetField("benefit", benefit)
                            p.SetField("cost", cost_best_option)
                            p.SetField("temp_cost", cost_best_option)
                            p.SetField("installation_year", year)

                            p.SetField("OPEX", OPEX)
                            self.total_cost[council] += cost_best_option
                            self.total_benefit[council] += benefit
                            # print 'Year: ' + str(year)+ ' ; Converted area is: ' + str(area) +' and cost is: '+str(cost_best_option) + 'the benefit is: ' + str(b)+'the budget is: ' + str(full_budget)

                            print 'Year: ' + str(year) + str(best_option) + ' installed for a cost of ' + str(
                                cost_best_option) + ' and total cost of ' + str(
                                self.total_cost[council]) + ' and a benefit of ' + str(benefit)
                            print 'area: ' + str(area) + ' opex: ' + str(OPEX)
                            full_budget -= cost_best_option


            # print 'Total benefits: ',str(self.total_benefit[council])
            # print 'Total costs: ', str(self.total_cost[council])
            # print 'Budget remaining: ', str(full_budget)

            self.parcel.finalise()