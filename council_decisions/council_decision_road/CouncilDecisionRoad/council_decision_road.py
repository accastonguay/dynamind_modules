__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
import random



class CouncilDecisionRoad(Module):
        display_name = "Council_road"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            '''Choose among different rules:
            1: Random technology with random budget
            2: Placed on 10y flooded parcels with random budget
            3: Placed on roads with random budget
            4: Placed on 10y flooded parcels with whole budget
            5: Placed on roads with whole budget
            '''

            self.createParameter("rule", INT)
            self.rule = 1

            self.createParameter("budget", INT)
            self.budget = 200000


            # self.parcel = ViewContainer("parcel", COMPONENT, READ)
            # self.parcel.addAttribute("original_landuse", Attribute.STRING, READ)
            # self.parcel.addAttribute("area", Attribute.INT, READ)
            # self.parcel.addAttribute("flooded", Attribute.INT, READ)
            # self.parcel.addAttribute("new_landuse", Attribute.STRING, WRITE)
            # self.parcel.addAttribute("benefit", Attribute.DOUBLE, WRITE)
            # self.parcel.addAttribute("cost", Attribute.DOUBLE, WRITE)
            # self.parcel.addAttribute("OPEX", Attribute.DOUBLE, WRITE)
            # self.parcel.addAttribute("avg_wtp_stream", Attribute.DOUBLE, READ)


            self.district = ViewContainer("district", COMPONENT, READ)
            # self.district.addAttribute("original_landuse", Attribute.STRING, READ)
            self.district.addAttribute("road_area", Attribute.INT, READ)
            # self.district.addAttribute("new_landuse", Attribute.STRING, WRITE)
            # self.district.addAttribute("benefit", Attribute.INT, WRITE)
            self.district.addAttribute("pcgreened", Attribute.INT, WRITE)
            self.district.addAttribute("flooded", Attribute.INT, READ)
            self.district.addAttribute("technology", Attribute.STRING, WRITE)
            self.district.addAttribute("cost", Attribute.INT, WRITE)
            self.district.addAttribute("area_greened", Attribute.DOUBLE, WRITE)




            # self.cost = {}
            # self.cost["wetland"] = 0.
            # self.cost["basin"] = 0.
            # self.cost["biofiltration"] = 0.
            # self.benefit["wetland"] = 1.
            # self.benefit["basin"] = 1.
            # self.benefit["biofiltration"] = 0.


            self.total_cost = 0
            self.total_benefit = 0




            #Compile views
            views = []
            # views.append(self.parcel)
            views.append(self.district)
            # views.append(self.road)


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
            # if self.rule in [1,2,4]:


            # convert = True
            full_budget = 200000
            year = 2000
            # # budget_rand = random.randrange(500,200000)
            # if self.rule in [1,2,4]:
            #     self.parcel.reset_reading()
            #     for p in self.parcel:
            #         landuse = p.GetFieldAsString("original_landuse")
            #         newlanduse = p.GetFieldAsString("new_landuse")
            #         # flooded = p.GetFieldAsInteger("flooded")
            #         area = p.GetFieldAsDouble("area")
            #         avg_wtp_stream = p.GetFieldAsDouble("avg_wtp_stream")
            #
            #         ''' Generate random number to randomize the iteration through parcels '''
            #         random_parcel = random.random()
            #
            #         landuses = ["PPRZ","PUZ1", "PUZ2", "PUZ4" ,"PUZ6","PUZ7"]
            #         if landuse in landuses and landuse == newlanduse and random_parcel > 0.5:
            #
            #             ### Strategy 1: randomly chosen with random area and random budget ###
            #             if self.rule == 1:
            #                 # Determine random budget from min 500 to max 200000
            #
            #
            #                 # Choose a random technology
            #
            #
            #
            #                 if int(area) > 300:
            #                     # Choose a random area to be converted, from min 25 m2 to max total area of parcel
            #                     con_area= area
            #
            #                     #calculate the annualised cost of technology
            #                     # if self.tech== 1:
            #                     #     if 500 > con_area >= 25:
            #                     #         self.cost= (150*con_area)/(1*(1/(1+0.05)**20)/0.05)+10*con_area
            #                     #     elif 10000 > con_area > 500:
            #                     #         self.cost= (100*con_area)/(1*(1/(1+0.05)**20)/0.05)+2*con_area
            #                     #     elif con_area > 10000:
            #                     #         self.cost= (75*con_area)/(1*(1/(1+0.05)**20)/0.05)+0.5*con_area
            #                     # elif self.tech == 2:
            #                     #     if 250 > con_area >= 25:
            #                     #         self.cost= (250*con_area)/(1*(1/(1+0.05)**20)/0.05)+20*con_area
            #                     #     elif 1000 > con_area > 250:
            #                     #         self.cost= (200*con_area)/(1*(1/(1+0.05)**20)/0.05)+10*con_area
            #                     #     elif con_area > 1000:
            #                     #         self.cost= (150*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #                     # elif self.tech == 3:
            #                     #     if 100 > con_area >= 25:
            #                     #         self.cost= (1000*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #                     #     elif 500 > con_area > 100:
            #                     #         self.cost= (350*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #                     #     elif con_area > 500:
            #                     #         self.cost= (250*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #                                                 # if self.tech== 1:
            #                     # Calculate capital cost
            #                     self.tech = random.randrange(1,4)
            #                     self.technologies = {1:'wetland', 2:'sedimentation', 3:'raingarden'}
            #                     if self.tech == 1:
            #                         if 500 > con_area >= 300:
            #                             self.cost= 150*con_area
            #                             opex= 10
            #                         elif 10000 > con_area > 500:
            #                             self.cost= (100*con_area)
            #                             opex= 2
            #                         elif con_area > 10000:
            #                             self.cost= (75*con_area)
            #                             opex= 0.5
            #                     elif self.tech == 2:
            #                         if 250 > con_area >= 25:
            #                             self.cost= (250*con_area)
            #                             opex= 20
            #
            #                         elif 1000 > con_area > 250:
            #                             self.cost= (200*con_area)
            #                             opex= 10
            #                         elif con_area > 1000:
            #                             self.cost= (150*con_area)
            #                             opex= 5
            #                     elif self.tech == 3:
            #                         if 100 > con_area >= 25:
            #                             self.cost= (1000*con_area)
            #                             opex= 2
            #                         elif 500 > con_area > 100:
            #                             self.cost= (350*con_area)
            #                         elif con_area > 500:
            #                             self.cost= (250*con_area)
            #                         opex= 5
            #                 else:
            #                     self.tech = random.randrange(1,3)
            #                     self.technologies = {1:'sedimentation', 2:'raingarden'}
            #
            #                     if self.tech == 1:
            #                         if 250 > con_area >= 25:
            #                             self.cost= (250*con_area)
            #                             opex= 20
            #
            #                         elif 1000 > con_area > 250:
            #                             self.cost= (200*con_area)
            #                             opex= 10
            #                         elif con_area > 1000:
            #                             self.cost= (150*con_area)
            #                             opex= 5
            #                     elif self.tech == 2:
            #                         if 100 > con_area >= 25:
            #                             self.cost= (1000*con_area)
            #                             opex= 2
            #                         elif 500 > con_area > 100:
            #                             self.cost= (350*con_area)
            #                         elif con_area > 500:
            #                             self.cost= (250*con_area)
            #                         opex= 5
            #
            #
            #
            #                 if self.cost> full_budget:
            #                     print 'The cost is above budget'
            #                     year+=1
            #
            #                 else:
            #
            #                     self.benefitdic = {'wetland':136*con_area, 'sedimentation':1341*con_area, 'raingarden': 10244*con_area}
            #                     test = self.technologies[self.tech]
            #                     b = self.benefitdic[self.technologies[self.tech]]
            #                     p.SetField("new_landuse", test)
            #                     p.SetField("benefit", b)
            #                     p.SetField("cost", self.cost)
            #                     p.SetField("OPEX", opex)
            #                     self.total_cost += self.cost
            #                     self.total_benefit += self.benefitdic[self.technologies[self.tech]]
            #                     print 'Year: ' + str(year)+ 'Converted area is: ' + str(con_area) +' and cost is: '+str(self.cost) + 'the benefit is: ' + str(b)+'the budget is: ' + str(full_budget)
            #                     print str(self.technologies[self.tech])
            #                     full_budget -= self.cost
            #                     year+=1
            #
            #
            #             # ### Strategy 2: randomly choosen on flooded parcel ###
            #             # elif self.rule == 2:
            #             #     if flooded == 1:
            #             #         budget = random.randrange(1,200000)
            #             #         self.tech = random.randrange(1,4)
            #             #         self.technologies = {1:'wetland', 2:'sedimentation' , 3:'raingarden' }
            #             #
            #             #         con_area= random.randrange(25,int(area))
            #             #         if self.tech == 1:
            #             #             if 500 > con_area > 200:
            #             #                 cost = (150*con_area)/(1*(1/(1+0.05)**20)/0.05)+10*con_area
            #             #             elif 10000 > con_area > 500:
            #             #                 cost = (100*con_area)/(1*(1/(1+0.05)**20)/0.05)+2*con_area
            #             #             elif con_area > 10000:
            #             #                 cost = (75*con_area)/(1*(1/(1+0.05)**20)/0.05)+0.5*con_area
            #             #         elif self.tech == 2:
            #             #             if 250 > con_area > 25:
            #             #                 cost = (250*con_area)/(1*(1/(1+0.05)**20)/0.05)+20*con_area
            #             #             elif 1000 > con_area > 250:
            #             #                 cost = (200*con_area)/(1*(1/(1+0.05)**20)/0.05)+10*con_area
            #             #             elif con_area > 1000:
            #             #                 cost = (150*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #             #         elif self.tech == 3:
            #             #             if 100 > con_area > 25:
            #             #                 cost = (1000*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #             #             elif 500 > con_area > 100:
            #             #                 cost = (350*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #             #             elif con_area > 500:
            #             #                 cost = (250*con_area)/(1*(1/(1+0.05)**20)/0.05)+5*con_area
            #             #
            #             #         self.benefitdic = {'wetland':136*area, 'sedimentation':1341*area, 'raingarden': 10244*area}
            #             #
            #             #         if self.cost > budget:
            #             #             continue
            #             #         else:
            #             #             p.SetField("new_landuse", self.technologies[self.tech])
            #             #             p.SetField("benefit", self.benefitdic[self.technologies[self.tech]])
            #             #             p.SetField("cost", cost)
            #             #             self.total_cost += cost
            #             #             print str(self.technologies[self.tech]) + ' installed for a cost of '  + str(cost)+' and a benefit of '+str(self.benefitdic[self.technologies[self.tech]])
            #             #
            #             #
            #             #
            #             # ### Strategy 3: Optimal spending with budget of 200000###
            #             elif self.rule == 2:
            #
            #
            #                 if area >1000:
            #                     if 10000 > area > 500:
            #                         ann_cost_wetland = (100*area)/(1*(1/(1+0.05)**20)/0.05)+2*area
            #                         cost_wetland = (100*area)
            #                     elif area > 10000:
            #                         ann_cost_wetland = (75*area)/(1*(1/(1+0.05)**20)/0.05)+0.5*area
            #                         cost_wetland = (75*area)
            #                     if 1000 > area > 250:
            #                         ann_cost_sedimentation = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                         cost_sedimentation = (200*area)
            #                     elif area >= 1000:
            #                         ann_cost_sedimentation = (150*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_sedimentation = (150*area)
            #
            #                     all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation}
            #                     all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation}
            #                     self.benefitdic = {'wetland':136*area, 'sedimentation':1341*area}
            #
            #                     benefit_sedimentation=1341
            #                     benefit_wetland = 136
            #
            #                     ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                     options = {'wetland':benefit_wetland*area/ann_cost_wetland, 'sedimentation':benefit_sedimentation*area/ann_cost_sedimentation}
            #                     best_option = max(options)
            #                     cost_best_option = all_cap_costs[best_option]
            #                     benefit = self.benefitdic[best_option]
            #
            #
            #                 elif 1000 >= area >300:
            #                     ### Calculate annualised cost and capital cost ###
            #                     if 500 > area > 300:
            #                         ann_cost_wetland = (150*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                         cost_wetland = (150*area)
            #                     elif 10000 > area > 500:
            #                         ann_cost_wetland = (100*area)/(1*(1/(1+0.05)**20)/0.05)+2*area
            #                         cost_wetland = (100*area)
            #                     elif area > 10000:
            #                         ann_cost_wetland = (75*area)/(1*(1/(1+0.05)**20)/0.05)+0.5*area
            #                         cost_wetland = (75*area)
            #                     if 250 > area > 50:
            #                         ann_cost_sedimentation = (250*area)/(1*(1/(1+0.05)**20)/0.05)+20*area
            #                         cost_sedimentation = (250*area)
            #                     elif 1000 > area > 250:
            #                         ann_cost_sedimentation = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                         cost_sedimentation = (200*area)
            #                     elif area > 1000:
            #                         ann_cost_sedimentation = (150*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_sedimentation = (150*area)
            #                     if 100 > area > 25:
            #                         ann_cost_raingarden = (1000*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_raingarden = (1000*area)
            #                     elif 500 > area > 100:
            #                         ann_cost_raingarden = (350*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_raingarden = (350*area)
            #                     elif 1000 > area > 500:
            #                         ann_cost_raingarden = (250*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_raingarden = (250*area)
            #
            #                     ''' Enter costs and benefits in dictionaries '''
            #                     all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
            #                     all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}
            #                     self.benefitdic = {'wetland':136*area, 'sedimentation':1341*area, 'raingarden': 10244*area}
            #
            #                     benefit_sedimentation=1341
            #                     benefit_wetland = 136
            #                     benefit_raingarden = 10244
            #
            #                     ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                     options = {'wetland':benefit_wetland*area/ann_cost_wetland, 'sedimentation':benefit_sedimentation*area/ann_cost_sedimentation,'raingarden': benefit_raingarden*area/ann_cost_raingarden}
            #                     best_option = max(options)
            #                     cost_best_option = all_cap_costs[best_option]
            #                     benefit = self.benefitdic[best_option]
            #
            #                 elif 300 >= area >25:
            #                     if 250 > area > 50:
            #                         ann_cost_sedimentation = (250*area)/(1*(1/(1+0.05)**20)/0.05)+20*area
            #                         cost_sedimentation = (250*area)
            #                     elif 1000 > area > 250:
            #                         ann_cost_sedimentation = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                         cost_sedimentation = (200*area)
            #
            #                     if 100 > area > 25:
            #                         ann_cost_raingarden = (1000*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_raingarden = (1000*area)
            #                     elif 500 > area > 100:
            #                         ann_cost_raingarden = (350*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_raingarden = (350*area)
            #
            #                     all_ann_costs = {'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
            #                     all_cap_costs = {'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}
            #                     self.benefitdic = { 'sedimentation':1341*area, 'raingarden': 10244*area}
            #
            #                     benefit_sedimentation=1341
            #                     benefit_raingarden = 10244
            #
            #                     ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                     options = {'sedimentation':benefit_sedimentation*area/ann_cost_sedimentation,'raingarden': benefit_raingarden*area/ann_cost_raingarden}
            #                     best_option = max(options)
            #                     cost_best_option = all_cap_costs[best_option]
            #                     benefit = self.benefitdic[best_option]
            #                 else:
            #
            #                     ann_cost_raingarden = (1000*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                     cost_raingarden = (1000*area)
            #
            #
            #                     all_ann_costs = {'raingarden':ann_cost_raingarden}
            #                     all_cap_costs = {'raingarden':cost_raingarden}
            #                     self.benefitdic = { 'raingarden': 10244*area}
            #
            #
            #                     benefit_raingarden = 10244
            #
            #                     ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                     options = {'raingarden': benefit_raingarden*area/ann_cost_raingarden}
            #                     best_option = max(options)
            #                     cost_best_option = all_cap_costs[best_option]
            #                     benefit = self.benefitdic[best_option]
            #
            #
            #                 # if 100 > area > 10:
            #                 #     cost_biofilter = (250*area)/(1*(1/(1+0.05)**20)/0.05)+20*area
            #                 # elif 500 > area > 100:
            #                 #     cost_biofilter = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                 # elif area > 500:
            #                 #     cost_biofilter = (150*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #
            #
            #
            #
            #                 '''If the cost is too high, there is no investment'''
            #                 if cost_best_option > full_budget:
            #                     print 'The cost is above budget'
            #                     year+=1
            #
            #                 else:
            #                     p.SetField("new_landuse", best_option)
            #                     p.SetField("benefit", benefit)
            #                     p.SetField("cost", cost_best_option)
            #                     p.SetField("OPEX", all_ann_costs[best_option])
            #                     self.total_cost += cost_best_option
            #                     self.total_benefit += benefit
            #
            #                     print 'Year: ' + str(year)+ str(best_option) + ' installed for a cost of '  + str(cost_best_option)+' and total cost of ' + str(self.total_cost) + ' and a benefit of '+str(benefit)
            #                     full_budget -= cost_best_option
            #                     year+=1
            #
            #
            #             elif self.rule == 4:
            #                 rn = random.random()*0.0164
            #                 print rn
            #                 if rn < avg_wtp_stream:
            #                     print 'rn is smaller than average willigness to pay'
            #
            #
            #
            #                     if area >1000:
            #                         if 10000 > area > 500:
            #                             ann_cost_wetland = (100*area)/(1*(1/(1+0.05)**20)/0.05)+2*area
            #                             cost_wetland = (100*area)
            #                         elif area > 10000:
            #                             ann_cost_wetland = (75*area)/(1*(1/(1+0.05)**20)/0.05)+0.5*area
            #                             cost_wetland = (75*area)
            #                         if 1000 > area > 250:
            #                             ann_cost_sedimentation = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                             cost_sedimentation = (200*area)
            #                         elif area >= 1000:
            #                             ann_cost_sedimentation = (150*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_sedimentation = (150*area)
            #
            #                         all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation}
            #                         all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation}
            #                         self.benefitdic = {'wetland':136*area, 'sedimentation':1341*area}
            #
            #                         benefit_sedimentation=1341
            #                         benefit_wetland = 136
            #
            #                         ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                         options = {'wetland':benefit_wetland*area/ann_cost_wetland, 'sedimentation':benefit_sedimentation*area/ann_cost_sedimentation}
            #                         best_option = max(options)
            #                         cost_best_option = all_cap_costs[best_option]
            #                         benefit = self.benefitdic[best_option]
            #
            #
            #                     elif 1000 >= area >300:
            #                         ### Calculate annualised cost and capital cost ###
            #                         if 500 > area > 300:
            #                             ann_cost_wetland = (150*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                             cost_wetland = (150*area)
            #                         elif 10000 > area > 500:
            #                             ann_cost_wetland = (100*area)/(1*(1/(1+0.05)**20)/0.05)+2*area
            #                             cost_wetland = (100*area)
            #                         elif area > 10000:
            #                             ann_cost_wetland = (75*area)/(1*(1/(1+0.05)**20)/0.05)+0.5*area
            #                             cost_wetland = (75*area)
            #                         if 250 > area > 50:
            #                             ann_cost_sedimentation = (250*area)/(1*(1/(1+0.05)**20)/0.05)+20*area
            #                             cost_sedimentation = (250*area)
            #                         elif 1000 > area > 250:
            #                             ann_cost_sedimentation = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                             cost_sedimentation = (200*area)
            #                         elif area > 1000:
            #                             ann_cost_sedimentation = (150*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_sedimentation = (150*area)
            #                         if 100 > area > 25:
            #                             ann_cost_raingarden = (1000*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_raingarden = (1000*area)
            #                         elif 500 > area > 100:
            #                             ann_cost_raingarden = (350*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_raingarden = (350*area)
            #                         elif 1000 > area > 500:
            #                             ann_cost_raingarden = (250*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_raingarden = (250*area)
            #
            #                         ''' Enter costs and benefits in dictionaries '''
            #                         all_ann_costs = {'wetland':ann_cost_wetland,'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
            #                         all_cap_costs = {'wetland':cost_wetland,'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}
            #                         self.benefitdic = {'wetland':136*area, 'sedimentation':1341*area, 'raingarden': 10244*area}
            #
            #                         benefit_sedimentation=1341
            #                         benefit_wetland = 136
            #                         benefit_raingarden = 10244
            #
            #                         ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                         options = {'wetland':benefit_wetland*area/ann_cost_wetland, 'sedimentation':benefit_sedimentation*area/ann_cost_sedimentation,'raingarden': benefit_raingarden*area/ann_cost_raingarden}
            #                         best_option = max(options)
            #                         cost_best_option = all_cap_costs[best_option]
            #                         benefit = self.benefitdic[best_option]
            #
            #                     elif 300 >= area >25:
            #                         if 250 > area > 50:
            #                             ann_cost_sedimentation = (250*area)/(1*(1/(1+0.05)**20)/0.05)+20*area
            #                             cost_sedimentation = (250*area)
            #                         elif 1000 > area > 250:
            #                             ann_cost_sedimentation = (200*area)/(1*(1/(1+0.05)**20)/0.05)+10*area
            #                             cost_sedimentation = (200*area)
            #
            #                         if 100 > area > 25:
            #                             ann_cost_raingarden = (1000*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_raingarden = (1000*area)
            #                         elif 500 > area > 100:
            #                             ann_cost_raingarden = (350*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                             cost_raingarden = (350*area)
            #
            #                         all_ann_costs = {'sedimentation' : ann_cost_sedimentation, 'raingarden':ann_cost_raingarden}
            #                         all_cap_costs = {'sedimentation' : cost_sedimentation, 'raingarden':cost_raingarden}
            #                         self.benefitdic = { 'sedimentation':1341*area, 'raingarden': 10244*area}
            #
            #                         benefit_sedimentation=1341
            #                         benefit_raingarden = 10244
            #
            #                         ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                         options = {'sedimentation':benefit_sedimentation*area/ann_cost_sedimentation,'raingarden': benefit_raingarden*area/ann_cost_raingarden}
            #                         best_option = max(options)
            #                         cost_best_option = all_cap_costs[best_option]
            #                         benefit = self.benefitdic[best_option]
            #                     else:
            #
            #                         ann_cost_raingarden = (1000*area)/(1*(1/(1+0.05)**20)/0.05)+5*area
            #                         cost_raingarden = (1000*area)
            #
            #
            #                         all_ann_costs = {'raingarden':ann_cost_raingarden}
            #                         all_cap_costs = {'raingarden':cost_raingarden}
            #                         self.benefitdic = { 'raingarden': 10244*area}
            #
            #
            #                         benefit_raingarden = 10244
            #
            #                         ''' Calculate B:C ratio of options and choose the option rendering the highest ratio '''
            #                         options = {'raingarden': benefit_raingarden*area/ann_cost_raingarden}
            #                         best_option = max(options)
            #                         cost_best_option = all_cap_costs[best_option]
            #                         benefit = self.benefitdic[best_option]
            #
            #
            #                     '''If the cost is too high, there is no investment'''
            #                     if cost_best_option > full_budget:
            #                         print 'The cost is above budget'
            #                         year+=1
            #
            #                     else:
            #                         p.SetField("new_landuse", best_option)
            #                         p.SetField("benefit", benefit)
            #                         p.SetField("cost", cost_best_option)
            #                         p.SetField("OPEX", all_ann_costs[best_option])
            #                         self.total_cost += cost_best_option
            #                         self.total_benefit += benefit
            #
            #                         print 'Year: '+ str(year) + str(best_option) + ' installed for a cost of '  + str(cost_best_option)+' and total cost of ' + str(self.total_cost) + ' and a benefit of '+str(benefit)
            #                         full_budget -= cost_best_option
            #                         year+=1
            #
            #
            #
            #     print 'total benefits: ' + str(self.total_benefit) + ' budget remaining: ' +str(full_budget)
            #     self.parcel.finalise()
            #
            #         ### Need to finish roads ###

            if self.rule in [1]:
                self.district.reset_reading()
                pcgreened=0
                for r in self.district:
                    area = r.GetFieldAsDouble("road_area")
                    flooded = r.GetFieldAsInteger("flooded")
                    ''' Generate random number to randomize the iteration through parcels '''
                    random_road = random.random()



                ### Placed on roads with random budget ###
                    if self.rule == 3:
                        budget = random.randrange(1,200000)
                        self.tech = random.randrange(1,3)
                        technologies = {1:'swale', 2:'bioretention'}
                        if area*0.2 > 20 and random_road > 0.5:
                            con_area= random.randrange(20,int(area*0.2))
                            if self.tech == 1:
                                # ann_cost = (25*con_area)/(1*(1/(1+0.05)**3)/0.05)+3*con_area
                                cost = (150*con_area)

                            elif self.tech == 2:
                                # ann_cost = (150*con_area)/(1*(1/(1+0.05)**4)/0.05)+4*con_area
                                cost = (150*con_area)

                            greened=con_area/(area*0.2)
                            '''No data on benefit for now'''
                            # benefitdic = {'swale':136*area, 'bioretention':1341*area}

                            if cost > budget or (pcgreened+pcgreened) > 1:
                                print 'Cost ' + str(cost) +' exceeds budget' + str(budget) + 'or percent greened ' + str(greened) +' exceeds road area'
                            else:
                                pcgreened += greened
                                r.SetField("technology", technologies[self.tech])
                                # r.SetField("benefit", benefitdic[technologies[tech]])
                                r.SetField("cost", cost)
                                r.SetField("area_greened", con_area)
                                r.SetField("pcgreened", pcgreened)
                                self.total_cost += cost
                                budget -= cost
                                print 'The budget is: ' + str(budget) + ' The technology is: ' + str(self.tech)+' The road is '+ str(pcgreened)+' percent greened'

                        ### Placed on roads with whole budget ###
                        # if self.rule == 5:
                        #     area_installed = area*0.3
                        #     cost_swale = (25*area_installed)/(1*(1/(1+0.05)**20)/0.05)+3*area_installed
                        #     cost_bioretention = (150*area_installed)/(1*(1/(1+0.05)**20)/0.05)+5*area_installed
                        #
                        #
                        #     all_costs = {'swale':cost_swale,'bioretention' : cost_bioretention}
                        #     benefit_swale=1341
                        #     benefit_bioretention = 136
                        #
                        #
                        #     options = {'swale':benefit_swale*area_installed/cost_swale, 'bioretention':benefit_bioretention*area/cost_bioretention}
                        #     benefitdic = {'swale':136*area_installed, 'bioretention':1341*area_installed}
                        #     best_option = max(options)
                        #     cost_best_option = all_costs[best_option]
                        #     benefit = benefitdic[best_option]
                        #     self.total_benefit += benefit
                        #     pc = area_installed/float(area)
                        #
                        #
                        #
                        #     if self.total_cost < self.budget:
                        #         r.SetField("technology", best_option)
                        #         r.SetField("benefit", benefit)
                        #         r.SetField("pcgreened", pc)
                        #         self.total_cost += cost_best_option
                        #
                        #
                        #
                        #
                        #

                self.district.finalise()
