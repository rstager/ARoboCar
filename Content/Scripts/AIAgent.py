import unreal_engine as ue
import pickle
import numpy as np
import math
from unreal_engine import FVector
from unreal_engine.classes import SplineComponent



class SplinePath:
    def __init__(self,actor,label):
        landscape=actor.get_world().find_actor_by_label(label)
        self.component=actor.get_actor_component_by_type(SplineComponent)
        if (self.component==None):
            self.component = actor.add_actor_component(SplineComponent, 'Spline to follow')
        print(dir(self.component))
        self.component.SetClosedLoop(True)
        self.component.ClearSplinePoints()
        for segment in  landscape.SplineComponent.Segments:
            first = True
            for p in segment.Points:
                if not first:
                    self.component.AddSplineWorldPoint(p.Center)
                else:
                    first = False
        self.max_distance = self.component.get_spline_length()
        self.distance = 0.0

    def loc_at(self,distance):
        return self.component.get_world_location_at_distance_along_spline(distance % self.max_distance)

    def vector_ahead(self,actor_location,distance_ahead):
        closest_distance,nearest_offset=self.closest(actor_location)
        location_ahead=self.location_at(closest_distance+distance_ahead)
        return location_ahead - actor_location

    def direction_ahead(self,actor,distance_ahead):
        rvector=self.vector_ahead(actor.get_actor_location(),distance_ahead)
        distance = rvector.length()
        angle = FVector.cross(rvector, actor.get_actor_forward()).z / distance
        return distance,angle

    def location_at(self,distance):
        return self.component.get_world_location_at_distance_along_spline(distance)

    def closest(self,location):
        rvector= self.component.FindLocationClosestToWorldLocation(location)
        key=self.component.FindInputKeyClosestToWorldLocation(location)
        d1=self.component.GetDistanceAlongSplineAtSplinePoint(int(key))
        d2=self.component.GetDistanceAlongSplineAtSplinePoint(int(key)+1)
        distance=(d2-d1)*(key%1.0)+d1
        print("closest keys {} d={} {}, distance={}".format(key,d1,d2,distance))
        offset=(rvector-location).length
        return distance,offset

class Vcam:
    def __init__(self,actor,sz,offset,dir):
        self.width=sz[0]
        self.height=sz[1]
        self.texture=actor.get_actor_component_by_type(ue.find_class('ATextureReader'))
        self.texture.SetWidthHeight(sz[0],sz[1])
    def capture(self):
        return self.texture.GetBuffer() # valid, pixels,framelag

class Driver:
    def begin_play(self):
        self.pawn = self.uobject.get_owner()
        ue.log("Driver Begin Play {}".format(self.pawn.get_name()))
        self.pawn.EnableIncarView(True)
        self.vcam=Vcam(self.pawn,[160,90],[0,0],[0,0])
        self.path=SplinePath(self.pawn,'Racetrack1')

    def tick(self,delta_time):
        valid, pixels,framelag =self.vcam.capture()
        if(valid):
            location = self.pawn.get_actor_location()
            rotation = self.pawn.get_actor_rotation()
            if True:
                properties_list = self.pawn.properties()
                name = self.pawn.get_name()
                ue.log("{} at [{} {} {}] [{}x{}] {} {}".format(name,location[0],location[1],location[2],
                                                               self.vcam.width,self.vcam.height,len(pixels),framelag))
            img=np.array(pixels).reshape((self.vcam.height,self.vcam.width,4)).astype(np.uint8)[:,:,0:3]
            #pickle.dump( img, open( "viewport.data", "wb" ) )
            #
            # Control side
            #
            vmove=self.pawn.VehicleMovement
            vmove.BrakeInput= 0
            if (self.path):
                distance, angle=self.path.direction_ahead(self.pawn,200)
                vmove.SteeringInput= -angle
                vmove.ThrottleInput=0.7
                ue.log("vmove {} {}".format(vmove.SteeringInput,vmove.ThrottleInput))
            else:
                vmove.SteeringInput=0.0
                #vmove.ThrottleInput=0.7
