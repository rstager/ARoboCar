import unreal_engine as ue
from unreal_engine import FVector
from unreal_engine.classes import Actor,Pawn,PyActor
from unreal_engine.classes import SplineComponent

ue.log("Content Scripts")

class Spline:
    def begin_play(self):
        # get a reference to a spline component
        self.spline = self.uobject.get_owner().get_actor_component_by_type(ue.find_class('SplineComponent'))
        # find the length of the spline
        self.max_distance = self.spline.get_spline_length()
        self.distance = 0.0
        # get a reference to the actor to move (as a blueprint property)
        self.actor_to_move = self.uobject.get_owner().get_property('ObjectToMove')

    def tick(self, delta_time):
        if self.distance >= self.max_distance:
            return
        # find the next point on the spline
        next_point = self.spline.get_world_location_at_distance_along_spline(self.distance)
        self.actor_to_move.set_actor_location(next_point)
        self.distance += 100 * delta_time

class Follower:
    def __init__(self):
        ue.log("Follower init")
        self.spline=None
        self.distance=0

    def begin_play(self):
        # find the length of the spline
        world=ue.get_editor_world()
        spline_actor=world.find_actor_by_label('Racetrack1_spline')
        self.spline=spline_actor.get_actor_component_by_type(SplineComponent)
        self.distance = 0.0
        self.max_distance = 0.0
        # get a reference to the actor to move (as a blueprint property)
        self.actor_to_move=self.uobject.get_owner()

    def tick(self, delta_time):
        if (self.spline!=None) :
            #ue.log("Follower max {} distance {}".format()
            if (self.max_distance==0):
                self.max_distance = self.spline.get_spline_length()
            if self.distance >= self.max_distance:
                return
            # find the next point on the spline
            next_point = self.spline.get_world_location_at_distance_along_spline(self.distance)
            #next_point.z=100
            self.actor_to_move.set_actor_location(next_point)
            #ue.log("set actor location {} {} {}".format(next_point,self.max_distance,self.distance))
            self.distance += 400 * delta_time

