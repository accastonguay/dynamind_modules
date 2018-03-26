__author__ = 'acharett'

from pydynamind import *
from osgeo import ogr
import random
import math

class council_influences(Module):
        display_name = "council_influences"
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

            '''Index Numbers ;  Non-tradables ;  Melbourne'''

            self.__cpi = {2004: 77, 2005: 79.425, 2006: 81.675, 2007: 84.5, 2008: 88.95, 2009: 90.9, 2010: 94.775, 2011: 98.425,
             2012: 101.85}

            """Pv costs from ewater"""

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
            self.parcel.addAttribute("outdoor_imp", Attribute.DOUBLE, READ)
            self.parcel.addAttribute("block_id", Attribute.INT, READ)
            self.parcel.addAttribute("new_landuse", Attribute.STRING, WRITE)
            self.parcel.addAttribute("council", Attribute.STRING, READ)
            self.parcel.addAttribute("N_removed", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("nrem_benefit", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("private_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("released", Attribute.INT, READ)
            self.parcel.addAttribute("conv_area", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("basin_percent_treated", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("basin_eia_treated", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("installation_year", Attribute.INT, WRITE)
            self.parcel.addAttribute("contribution_year", Attribute.INT, WRITE)
            self.parcel.addAttribute("OPEX", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("temp_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_cost", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_nrem", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("pv_benefit_total", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("npv", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("offset_paid", Attribute.DOUBLE, WRITE)
            self.parcel.addAttribute("ownership", Attribute.STRING, WRITE)
            self.parcel.addAttribute("rainfall", Attribute.DOUBLE, READ)


            self.council = ViewContainer("council", COMPONENT, READ)
            self.council.addAttribute("const_cost_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("maint_cost_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("rf_factor", Attribute.DOUBLE, READ)
            self.council.addAttribute("year", Attribute.INT, READ)
            self.council.addAttribute("influence_rule", Attribute.INT, READ)
            self.council.addAttribute("discount_rate", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("expected_removal", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("offset_source", Attribute.STRING, WRITE)
            self.council.addAttribute("offset_scenario", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("lifespan_rg", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("lifespan_wetland", Attribute.DOUBLE, WRITE)
            self.council.addAttribute("lifespan_pond", Attribute.DOUBLE, WRITE)
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
                if year <= 2012:
                    mcost = cost* self.__cpi[year] / self.__cpi[2012]
                    renewal = self.__annualised_renewal[technology] * self.__cpi[year] / self.__cpi[2004]

                else:
                    mcost = cost*(3.15 * year - 6236.6)/ self.__cpi[2012]
                    renewal = self.__annualised_renewal[technology] * (3.15 * year - 6236.6) / self.__cpi[2004]
                maintenance_cost = []
                renewal_cost = []
                for y in self.__years[technology]:
                    maintenance_cost.append(mcost)
                    renewal_cost.append(renewal)
                discount_maintenance_cost = [(d * m) + (d*r) for d, m, r in zip(self.__discount_factor[technology], maintenance_cost,renewal_cost)]
                return sum(discount_maintenance_cost)

        """Total PV costs function for Music"""
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

        def contribution(self, imp_area):
            return 413.61*imp_area**0.5711

        def run(self):
            #Data Stream Manipulation

            self.council.reset_reading()
            for c in self.council:
                influence_rule = c.GetFieldAsInteger("influence_rule")
                const_cost_factor= c.GetFieldAsDouble("const_cost_factor")
                maint_cost_factor= c.GetFieldAsDouble("maint_cost_factor")
                budget_factor= c.GetFieldAsDouble("budget_factor")
                rf_factor = c.GetFieldAsDouble("rf_factor")
                year = c.GetFieldAsInteger("year")

                c.SetField("discount_rate", self.discount_rate)
                c.SetField("expected_removal", self.expected_removal)
                c.SetField("offset_source", self.offset_source)
                c.SetField("offset_scenario", self.offset_scenario)
                c.SetField("budget_source", self.budget_source)
                c.SetField("cost_source", self.cost_source)

                c.SetField("lifespan_rg", self.lifespan_rg)
                c.SetField("lifespan_wetland", self.lifespan_wetland)
                c.SetField("lifespan_pond", self.lifespan_pond)
            self.council.finalise()

            self.parcel.reset_reading()

            for p in self.parcel:

                outdoor_imp = p.GetFieldAsDouble("outdoor_imp")
                area = p.GetFieldAsDouble("convertible_area")
                rainfall = p.GetFieldAsDouble("rainfall")
                released = p.GetFieldAsInteger("released")
                rainfall = rainfall/1000.
                runoff = rainfall * rf_factor * 0.9
                offset_rate = self.offset(year, self.offset_source, self.offset_scenario)

                ### Strategy 1: Mandatory installation of raingarden ###
                if influence_rule == 1:
                    if year == released and outdoor_imp > 0:
                        # print "entered second loop"
                        technology = "raingarden"
                        requiredArea = self.design_curves(self.expected_removal, technology) * outdoor_imp

                        conArea = min(requiredArea, area)

                        percent_treated = conArea / requiredArea

                        cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                        opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                        # offset_rate = self.offset(year, self.offset_source, self.offset_scenario)
                        eia_treated = conArea / self.design_curves(self.expected_removal, technology)

                        N_removed = self.n_removed(eia_treated, runoff)

                        b = self.benefit_fun(offset_rate, N_removed)

                        p.SetField("new_landuse", technology)
                        p.SetField("N_removed", N_removed)
                        p.SetField("private_cost", cost)
                        p.SetField("temp_cost", cost)
                        p.SetField("OPEX", opex)
                        p.SetField("installation_year", year)
                        p.SetField("conv_area", conArea)
                        p.SetField("percent_treated", percent_treated)
                        p.SetField("offset_paid", 0)
                        p.SetField("basin_eia_treated", eia_treated)
                        p.SetField("nrem_benefit", b)

                        pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)

                        pvb_nrem = self.pv_benefit(b, technology)
                        npv = pvb_nrem - pvc

                        p.SetField("pv_cost", pvc)
                        p.SetField("pv_benefit_nrem", pvb_nrem)
                        p.SetField("pv_benefit_total", pvb_nrem)
                        p.SetField("npv", npv)
                        p.SetField("ownership", "private")

                if influence_rule == 2:
                    if year == released and outdoor_imp > 0:
                        gross_contribution = self.contribution(outdoor_imp)
                        technology = "raingarden"
                        requiredArea = self.design_curves(1, technology) * outdoor_imp

                        conArea = min(requiredArea, area)
                        cost = self.const_cost(technology, conArea, year, self.cost_source) * const_cost_factor
                        opex = self.maint_cost(technology, conArea, year, self.cost_source) * maint_cost_factor

                        if cost > gross_contribution:
                            net_contribution = gross_contribution
                            p.SetField("offset_paid", net_contribution)
                            p.SetField("contribution_year", year)

                        elif cost < gross_contribution:

                            percent_treated = conArea / requiredArea
                            net_contribution = gross_contribution - gross_contribution*percent_treated

                            eia_treated = conArea / self.design_curves(self.expected_removal, technology)
                            N_removed = self.n_removed(eia_treated, runoff)
                            b = self.benefit_fun(offset_rate, N_removed)
                            p.SetField("basin_eia_treated", eia_treated)
                            p.SetField("nrem_benefit", b)
                            p.SetField("new_landuse", technology)
                            p.SetField("N_removed", N_removed)
                            p.SetField("benefit", b)
                            p.SetField("private_cost", cost)
                            p.SetField("temp_cost", cost)
                            p.SetField("OPEX", opex)
                            p.SetField("installation_year", year)
                            p.SetField("conv_area", conArea)
                            p.SetField("percent_treated", percent_treated)
                            p.SetField("offset_paid", net_contribution)

                            pvc = self.pv_total_costs(year, technology, conArea, self.cost_source)
                            pvb_nrem = self.pv_benefit(b, technology)
                            npv = pvb_nrem - pvc

                            p.SetField("pv_cost", pvc)
                            p.SetField("pv_benefit_nrem", pvb_nrem)
                            p.SetField("pv_benefit_total", pvb_nrem)
                            p.SetField("npv", npv)
                            p.SetField("ownership", "private")
            self.parcel.finalise()
