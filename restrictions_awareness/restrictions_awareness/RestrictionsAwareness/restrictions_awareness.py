__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr



class RestrictionsAwareness(Module):
        display_name = "policy_maker"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("restriction", INT)


            self.policy_maker = ViewContainer("policy_maker", COMPONENT, READ)
            self.policy_maker.addAttribute("dam_volume", Attribute.DOUBLE, READ)
            self.policy_maker.addAttribute("restriction", Attribute.INT, WRITE)


            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.policy_maker)
            # views.append(self.city_environment)


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
            self.policy_maker.reset_reading()
            # self.city_environment.reset_reading()
            for b in self.policy_maker:
                volume = b.GetFieldAsDouble("dam_volume")

                if volume > 980:
                    self.restriction = 0
                    b.SetField("restriction", self.restriction)
                    print 'Volume is '+str(volume) +' and the restriction is 0'
                elif 980 >= volume > 575:
                    self.restriction = 1
                    b.SetField("restriction", self.restriction)
                    print 'Volume is '+str(volume) +' and the restriction is 1'
                elif 575 > volume:
                    self.restriction = 2
                    b.SetField("restriction", self.restriction)
                    print 'Volume is '+str(volume) +' and the restriction is 2'
            self.policy_maker.finalise()




            #     self.city.restriction=0
            # elif 980000 >= self.city_environment.dam_volume > 575000:
            #     self.city.restriction=1
            # elif 575000 >= self.city_environment.dam_volume:
            #     self.city.restriction=2

            # if city_environment.GetFieldAsDouble("dam_volume") > 980000:
            #     self.city.restriction=0
            # elif 980000 >= city_environment.GetFieldAsDouble("dam_volume") > 575000:
            #     self.city.restriction=1
            # elif 575000 >= city_environment.GetFieldAsDouble("dam_volume"):
            #     self.city.restriction=2


            # for c_e in self.city_environment:
            #     d_v = c_e.GetFieldAsDouble("dam_volume")
            #     for c in self.city:
            #         r = c.GetFieldAsDouble("restriction")
            #         if d_v > 980000:
            #             self.restriction = 0
            #             c.SetField("restriction", self.restriction)
            #         elif 980000 >= d_v > 575000:
            #             self.restriction = 1
            #             c.SetField("restriction", self.restriction)
            #         elif 575000 >= d_v:
            #             self.restriction = 2
            #             c.SetField("restriction", self.restriction)

            # for c_e in self.city_environment:
            #     d_v = c_e.GetFieldAsDouble("dam_volume")
            #     print d_v
                # for c in self.city:
                #     r = c.GetFieldAsDouble("restriction")
                #     if d_v > 980000:
                #         self.restriction = 0
                #         c.SetField("restriction", self.restriction)
                #     elif 980000 >= d_v > 575000:
                #         self.restriction = 1
                #         c.SetField("restriction", self.restriction)
                #     elif 575000 >= d_v:
                #         self.restriction = 2
                #         c.SetField("restriction", self.restriction)


            # self.city_environment.finalise()
