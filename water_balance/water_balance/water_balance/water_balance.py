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



            self.city = ViewContainer("city", COMPONENT, READ)

            # self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("mel_total_demand", Attribute.DOUBLE, READ)
            self.city.addAttribute("inflow", Attribute.DOUBLE, READ)
            self.city.addAttribute("dam_full", Attribute.DOUBLE, READ)
            self.city.addAttribute("dam_volume", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("dam_percent", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("monthly_dam_volume", Attribute.STRING, WRITE)
            self.city.addAttribute("monthly_restrictions", Attribute.STRING, WRITE)
            self.city.addAttribute("modelled_restriction", Attribute.INT, WRITE)



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

                # new_dam_volume = min((dam_volume - demand + inflow),1811)
                storages = []
                perc_storages = []
                restriction_list = []

                for i in range(12):
                    monthly_storage = dam_volume + monthly_inflow - monthly_demand
                    dam_volume = monthly_storage
                    storages.append(dam_volume)
                    dam_percent = dam_volume/dam_full
                    if dam_percent > 0.5:
                        restriction = 0
                    elif 0.45 < dam_percent <=  0.5:
                        restriction = 1
                    elif 0.4 < dam_percent <=  0.45:
                        restriction = 2
                    elif 0.3 < dam_percent <= 0.4:
                        restriction = 3
                    elif  dam_percent < 0.30:
                        restriction = 4
                    restriction_list.append(restriction)

                rest = max(set(restriction_list), key=restriction_list.count)

                new_dam_volume = min(storages[-1], dam_full)
                dam_percent = new_dam_volume/dam_full
                c.SetField("dam_volume", new_dam_volume)
                c.SetField("dam_percent", dam_percent)
                c.SetField("monthly_dam_volume", str(storages))
                c.SetField("monthly_restrictions", str(restriction_list))
                c.SetField("modelled_restriction",rest)

            self.city.finalise()