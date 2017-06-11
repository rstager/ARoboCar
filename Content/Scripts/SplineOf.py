import unreal_engine as ue
from unreal_engine import FVector
from unreal_engine.classes import Actor,Pawn,PyActor
from unreal_engine.classes import SplineComponent

ue.log("LandscapeToSpline")
world=ue.get_editor_world()
def spline_of(arg):
    if (isinstance(arg,str)):
        road=world.find_actor_by_label('Racetrack1')
    else:
        road=arg
    path=world.actor_spawn(Pawn,FVector(0,0,0))
    path.set_actor_label(road.get_actor_label()+"_spline")
    path.spline=path.add_actor_component(SplineComponent,'Spline to follow')
    path.spline.ClearSplinePoints()
    for segment in road.SplineComponent.Segments:
        first=True
        for p in segment.Points:
            if not first:
               path.spline.AddSplineWorldPoint(p.Center)
            else:
               first=False
    return path

#road=world.find_actor_by_label('Racetrack1')
#path=convert_to_spline(road)
#rabbit=world.find_actor_by_label('rabbit')

#path.add_actor_component(Follower,'follow ticker')






