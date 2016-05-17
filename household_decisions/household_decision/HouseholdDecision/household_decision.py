__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *



class HouseholdDecision(Module):
        display_name = "Households"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition
            self.createParameter("rule", INT)
            self.rule = 1
            self.rwht_option = ViewContainer("rwht_option", COMPONENT, READ)

            self.rwht_option.addAttribute("volume", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("parcel_id", Attribute.INTEGER, READ)

            self.rwht_option.addAttribute("incentive", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("wtp", Attribute.DOUBLE, READ)
            # self.rwht_option.addAttribute("ogc_fid", Attribute.DOUBLE, READ)


            self.rwht_option.addAttribute("pv_indoor", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("pv_outdoor", Attribute.DOUBLE, READ)
            self.rwht_option.addAttribute("placed", Attribute.DOUBLE, WRITE)
            self.rwht_option.addAttribute("plumbed", Attribute.DOUBLE, WRITE)

            # self.rwht_option.addAttribute("plumbed", Attribute.DOUBLE, READ)


            #Compile views
            views = []
            views.append(self.rwht_option)
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
            self.rwht_option.reset_reading()
            parcel_seen = []
            parcel_number =[]
            for r in self.rwht_option:

                # Calculate PV for indoor use
                i = r.GetFieldAsDouble("incentive")
                v = r.GetFieldAsDouble("volume")
                wtp = r.GetFieldAsDouble("wtp")
                pv_indoor = r.GetFieldAsDouble("pv_indoor")
                pv_outdoor = r.GetFieldAsDouble("pv_outdoor")
                id = r.GetFieldAsInteger("parcel_id")


                if len(parcel_number) == 3:
                else:
                    dict['indoor':{v:pv_indoor}]
                    dict['outdoor':{v:pv_indoor}]



                pv_total_costs_indoor = pv_total_costs_indoor_fun(y, v)
                pv_non_potable_saving = pv_non_potable_saving_fun(r.GetFieldAsDouble("annual_water_savings"), p)

                pv_indoor = pv_non_potable_saving - pv_total_costs_indoor
                r.SetField("pv_total_costs_indoor", pv_total_costs_indoor)
                r.SetField("pv_non_potable_saving", pv_non_potable_saving)
                r.SetField("pv_indoor", pv_indoor)

                # Calculate PV for outdoor use

                pv_total_costs_outdoor = pv_total_costs_outdoor_fun(y, v)
                pv_outdoor_potable_saving = pv_outdoor_potable_saving_fun(r.GetFieldAsDouble("outdoor_water_savings"), p)

                pv_outdoor = pv_outdoor_potable_saving - pv_total_costs_outdoor
                r.SetField("pv_total_costs_outdoor", pv_total_costs_outdoor)
                r.SetField("pv_outdoor_potable_saving", pv_outdoor_potable_saving)
                r.SetField("pv_outdoor", pv_outdoor)




            self.rwht_option.finalise()
