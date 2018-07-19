__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *



class water_balance(Module):
        display_name = "Water balance"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.__restriction_scenarios = {
                1: {1: 0.45, 2: 0.4, 3: 0.35, 4: 0.25},
                2: {1:0.5,2:0.45, 3:0.4, 4:0.3},
                3: {1:0.55,2:0.5, 3:0.45, 4:0.35},
                4: {1:0.6,2:0.55, 3:0.5, 4:0.4},
                5: {1: 0.65, 2: 0.6, 3: 0.55, 4: 0.45}}

            self.city = ViewContainer("city", COMPONENT, READ)

            # self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("mel_total_demand", Attribute.DOUBLE, READ)
            self.city.addAttribute("inflow", Attribute.DOUBLE, READ)
            self.city.addAttribute("restriction_scenario", Attribute.INT, READ)
            self.city.addAttribute("dam_full", Attribute.DOUBLE, READ)
            self.city.addAttribute("dam_volume", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("dam_percent", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("monthly_dam_volume", Attribute.STRING, WRITE)
            self.city.addAttribute("monthly_restrictions", Attribute.STRING, WRITE)
            self.city.addAttribute("modelled_restriction", Attribute.INT, WRITE)
            self.city.addAttribute("desal_cap", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("desal_cost", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("desal_delay", Attribute.INT, WRITE)
            self.city.addAttribute("year", Attribute.INT, READ)


            views = []
            views.append(self.city)
            self.registerViewContainers(views)

            #Data Stream Definition

        """
        Data Manipulation Process (DMP)
        """

        def run(self):

            self.city.reset_reading()

            for c in self.city:
                inflow = c.GetFieldAsDouble("inflow")
                monthly_inflow = inflow/12.

                demand = c.GetFieldAsDouble("mel_total_demand")
                monthly_demand = demand/12.

                dam_volume = c.GetFieldAsDouble("dam_volume")
                dam_full = c.GetFieldAsDouble("dam_full")

                desal_cap = c.GetFieldAsDouble("desal_cap")
                desal_cost = c.GetFieldAsDouble("desal_cost")

                sc = c.GetFieldAsInteger("restriction_scenario")
                desal_delay = c.GetFieldAsInteger("desal_delay")

                year = c.GetFieldAsInteger("year")

                restrictions = self.__restriction_scenarios[sc]

                storages = []
                restriction_list = []

                for i in range(12):
                    dam_volume = dam_volume + monthly_inflow - monthly_demand
                    storages.append(max(dam_volume,0))
                    dam_percent = dam_volume/dam_full

                    if year >= 2015:
                        if dam_percent > restrictions[1]:
                            restriction = 0
                        elif restrictions[2] < dam_percent <=  restrictions[1]:
                            restriction = 1
                        elif restrictions[3] < dam_percent <=  restrictions[2]:
                            restriction = 2
                        elif restrictions[4] < dam_percent <= restrictions[3]:
                            restriction = 3
                        elif  dam_percent < restrictions[4]:
                            restriction = 4
                        restriction_list.append(restriction)
                    else:
                        if dam_percent >= 0.5:
                            restriction = 0
                        elif 0.5 > dam_percent >=  0.45:
                            restriction = 1
                        elif 0.45 > dam_percent >=  0.4:
                            restriction = 2
                        elif 0.4 > dam_percent >= 0.3:
                            restriction = 3
                        elif  dam_percent > 0.3:
                            restriction = 4
                        restriction_list.append(restriction)

                rest = max(set(restriction_list), key=restriction_list.count)

                new_dam_volume = min(storages[-1], dam_full)
                dam_percent = new_dam_volume/dam_full

                if desal_delay == 1:
                    desal_cap += 150
                    desal_cost += 6
                    c.SetField("desal_cap", desal_cap)
                    c.SetField("desal_cost", desal_cost)

                if year >= 2015:
                    if desal_delay > 0:
                        desal_delay -= 1
                        c.SetField("desal_delay", desal_delay)
                    elif desal_delay == 0 and dam_percent < restrictions[4]:
                        desal_delay = 5
                        c.SetField("desal_delay", desal_delay)
                    else:
                        c.SetField("desal_delay", desal_delay)

                else:
                    if desal_delay > 0:
                        desal_delay -= 1
                        c.SetField("desal_delay", desal_delay)
                    elif desal_delay == 0 and dam_percent < 0.3:
                        desal_delay = 5
                        c.SetField("desal_delay", desal_delay)
                    else:
                        c.SetField("desal_delay", desal_delay)

                c.SetField("dam_volume", new_dam_volume)
                c.SetField("dam_percent", dam_percent)
                c.SetField("monthly_dam_volume", str(storages))
                c.SetField("monthly_restrictions", str(restriction_list))
                c.SetField("modelled_restriction", rest)

            self.city.finalise()