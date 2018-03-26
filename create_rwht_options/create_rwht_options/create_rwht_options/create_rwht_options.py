from pydynamind import *

class NewRWHTOptions(Module):
    display_name = "New RWHT options"
    group_name = "ABM"
    """
    Module Initialisation
    """

    def __init__(self):
        Module.__init__(self)

        # To use the GDAL API
        self.setIsGDALModule(True)
        # Parameter Definition

        
    def init(self):

        self.__parcel = ViewContainer("parcel", COMPONENT, READ)
        self.__parcel.addAttribute("annual_outdoor_demand", Attribute.DOUBLE, READ)
        self.__parcel.addAttribute("annual_non_potable_demand", Attribute.DOUBLE, READ)
        self.__parcel.addAttribute("roof_area", Attribute.DOUBLE, READ)
        self.__parcel.addAttribute("persons", Attribute.INT, READ)
        self.__parcel.addAttribute("rainfall", Attribute.INT, READ)

        self.__rwht_option = ViewContainer("rwht_option", COMPONENT, WRITE)
        self.__rwht_option.addAttribute("outdoor_water_savings", Attribute.DOUBLE, WRITE)
        self.__rwht_option.addAttribute("non_potable_savings", Attribute.DOUBLE, WRITE)
        self.__rwht_option.addAttribute("volume", Attribute.DOUBLE, WRITE)
        self.__rwht_option.addAttribute("total_sewerage", Attribute.DOUBLE, WRITE)
        self.__rwht_option.addAttribute("parcel_id", Attribute.INT, WRITE)

        self.registerViewContainers([self.__parcel, self.__rwht_option])

    """
    Data Manipulation Process (DMP)
    """

    def run(self):
        # Data Stream Manipulation

        self.__parcel.reset_reading()

        for p in self.__parcel:
            annual_outdoor_demand = p.GetFieldAsDouble("annual_outdoor_demand")
            annual_non_potable_demand = p.GetFieldAsDouble("annual_non_potable_demand")
            roof_area = p.GetFieldAsDouble("roof_area")
            rainfall = p.GetFieldAsDouble("rainfall")
            persons = p.GetFieldAsInteger("persons")

            for v in [2,5,10]:
                option = self.__rwht_option.create_feature()

                if v == 2:
                    outdoor_water_savings = 0.12751266 + 0.20324091 * annual_outdoor_demand + 0.02524949*roof_area+ -3.72497699  * persons + 0.01564831*rainfall
                    non_potable_savings = -10.85879352 + -0.26321637 * annual_non_potable_demand + 0.03505458*roof_area + 15.21275745*persons + 0.03017235*rainfall
                if v == 5:
                    outdoor_water_savings = -8.12624283 + 0.30882026 * annual_outdoor_demand + 0.04623133*roof_area+ -4.36292328  * persons + 0.02870202*rainfall
                    non_potable_savings = -19.84041825  + -0.33294597 * annual_non_potable_demand + 0.05754990*roof_area + 19.50883635*persons + 0.04032498*rainfall
                if v == 10:
                    outdoor_water_savings = -13.09198054 + 0.36779529 * annual_outdoor_demand + 0.05702749*roof_area+ -4.53763756  * persons + 0.03514167*rainfall
                    non_potable_savings = -24.90739351 + -0.35769547 * annual_non_potable_demand + 0.07042853*roof_area + 21.21696507*persons + 0.04555054*rainfall

                option.SetField("volume", v)
                option.SetField("outdoor_water_savings", max(0,outdoor_water_savings))
                option.SetField("non_potable_savings",  max(0,non_potable_savings))
                option.SetField("total_sewerage", 35)
                option.SetField("parcel_id", p.GetFID())

        self.__parcel.finalise()
        self.__rwht_option.finalise()
