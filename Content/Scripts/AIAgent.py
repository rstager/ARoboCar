import unreal_engine as ue
import numpy as np
import math
from unreal_engine import FVector,FTransform,FRotator
from unreal_engine.classes import TextureRenderTarget2D,SceneComponent,SceneCaptureComponent2D
from unreal_engine.classes import Actor,SplineComponent,SkeletalMeshComponent
import subprocess
import pickle
import sys
import random
import os
import tempfile


class SplinePath:
    def __init__(self,actor,label):
        for landscape in actor.all_actors():
            if(landscape.get_name() == label):
                self.component=actor.get_actor_component_by_type(SplineComponent)
                if (self.component==None):
                    self.component = actor.add_actor_component(SplineComponent, 'Spline to follow')
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
                return
        print("Didn't find landscape ",label)

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
        #print("closest keys {} d={} {}, distance={}".format(key,d1,d2,distance))
        offset=(rvector-location).length()
        return distance,offset

class Vcam:
    def __init__(self,actor,label,sz,offset,rot):
        print(actor)
        self.width=sz[0]
        self.height=sz[1]
        #print("before attach",actor.get_actor_components())
        mesh=actor.get_actor_component_by_type(SkeletalMeshComponent)

        # we need three parts, SceneCaptureActor, ATextureReader, RenderTargetTextures
        self.rendertarget=TextureRenderTarget2D()
        self.rendertarget.set_property("SizeX",self.width)
        self.rendertarget.set_property("SizeY",self.height)

        xform=FTransform()
        xform.translation=FVector(offset[0],offset[1],offset[2])
        xform.rotation=FRotator(rot[0],rot[1],rot[2])
        ue.log("vcam xlate {} rot {}".format(xform.translation,xform.rotation))
        self.scene_capture=actor.get_actor_component_by_type(SceneCaptureComponent2D)

        self.scene_capture.set_relative_location(offset[0],offset[1],offset[2])
        self.scene_capture.set_relative_rotation(rot[0],rot[1],rot[2])
        self.scene_capture.set_property("TextureTarget",self.rendertarget)


        #ignore these..they are notes for work in progress
        #self.scene_capture= actor.actor_create_default_subobject(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture")
        #self.scene_capture = actor.ConstructObject(ue.find_class('SceneCaptureComponent2D'),
                                                                  #label + "_scenecapture")
        #self.scene_capture= actor.add_actor_component(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture")
        #print(self.scene_capture.get_actor())
        #ret=self.scene_capture.attach_to_actor(actor)
        #mesh=actor.get_actor_component_by_type(SkeletalMeshComponent)
        #self.scene_capture.attach_to_component(mesh)#.get_actor_component_by_type(),"ATTACHMENT_RULE_SNAP_TO_TARGET")

        #UWhateverComponent * NewComponent = ConstructObject < UWhateverComponent > (UWhateverComponent::StaticClass(), this, TEXT("ComponentName"));

        #NewComponent->RegisterComponent();
        #NewComponent->OnComponentCreated(); //Might not need this.
        #NewComponent->AttachTo(GetRootComponent(), SocketName / * NAME_None * /);
        #SpringArm = CreateDefaultSubobject < USpringArmComponent > (TEXT("SpringArm"));
        #SpringArm->SetRelativeLocation(FVector(0.0
        #SpringArm->SetupAttachment(RootComponent);


        #self.scene_capture= actor.add_actor_component(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture")
        #self.scene_capture= actor.AddComponent(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture",xform))
        #self.scene_capture.SetupAttachment(actor.RootComponent)
        #self.scene_capture.SetRelativeTransform(xform)
        #self.scene_capture.set_relative_location(FVector(offset[0],offset[1],offset[2]))
        #for c in actor.get_actor_components():
        #    if(c.is_a(ue.find_class('SceneCaptureComponent2D'))):
        #        ue.log("{} {} {} {} {}".format(c.get_name(),c.get_relative_location(),c.get_property('AttachParent'),c.get_property('bAbsoluteLocation'),c.get_property('Mobility')))

        # add reader last
        self.reader = actor.add_actor_component(ue.find_class('ATextureReader'),label+"_rendertarget")
        self.reader.set_property('RenderTarget',self.rendertarget)
        self.reader.SetWidthHeight(sz[0],sz[1])
    def capture(self):
        return self.reader.GetBuffer() # valid, pixels,framelag

class Driver:
    def open_connection(self):
        if hasattr(self,"fstate"):
            ue.log("Closing controller connection")
            self.fstate.close()
            self.fcmd.close()

        # open pipes, create if needed
        # note this code is duplicated in simulator.py.
        tmpdir=tempfile.gettempdir()
        state_filename=os.path.join(tmpdir,"sim_state")
        cmd_filename=os.path.join(tmpdir,"sim_cmd")
        if not os.path.exists(state_filename):
            os.mkfifo(state_filename)
        if not os.path.exists(cmd_filename):
            os.mkfifo(cmd_filename)

        ue.log("WAITING FOR controller to connect")
        self.fstate = open(state_filename, "wb")
        self.fcmd = open(cmd_filename, "rb")
        print("Fifos opened sending config")

        #send initial config
        pickle.dump({"camerawidth":self.width,"cameraheight":self.height}, self.fstate)
        self.fstate.flush()

        #check to see if client wants to change config
        self.requested_config = pickle.load(self.fcmd)
        print("Requested config",self.requested_config)


    def begin_play(self):
        self.pawn = self.uobject.get_owner()
        ue.log("Driver Begin Play {}".format(self.pawn.get_name()))

        self.height=90
        self.width=160

        self.path=SplinePath(self.pawn,'Racetrack1')
        self.vcam=Vcam(self.pawn,"frontcamera",[self.width,self.height],[50,0,200],[0,-30,0])

        self.pawn.EnableIncarView(False)

        self.history=[]
        self.open_connection()
        self.firsttime=True

    def tick(self,delta_time):
        if not hasattr(self, 'vcam'):
            return
        if(len(self.history)>4): self.history.pop(0)
        location = self.pawn.get_actor_location() #current values
        rotation = self.pawn.get_actor_rotation()
        self.history.append((location,rotation))
        valid, pixels,framelag =self.vcam.capture()
        if(valid and framelag <=len(self.history)):
            location,rotation=self.history[-(framelag+1)] #values at time of snapshot
            img=np.array(pixels).reshape((self.vcam.height,self.vcam.width,4)).astype(np.uint8)[:,:,0:3]
            #
            # Control side
            #
            vmove=self.pawn.VehicleMovement
            vmove.BrakeInput= 0
            dummy, angle = self.path.direction_ahead(self.pawn, 400)
            pathdistance,offset=self.path.closest(location)

            try:
                # we send the data first, but we let the controller process in parrallel, so the command is actually
                # one tick late.  We view this as a get command...send data,  but the controller
                # views it as get data...send command.  So we skip the first get command to keep things in sync.
                if self.firsttime:
                    self.firsttime=False
                else:
                    # read previous command
                    cmd=pickle.load(self.fcmd)
                    vmove.SteeringInput=cmd["steering"]
                    vmove.ThrottleInput = cmd["throttle"]
                    #ue.log("got command {} {}".format(vmove.SteeringInput,vmove.ThrottleInput))

                #send the state and give the controller some time to process
                pickle.dump({"pathdistance":pathdistance,"pathoffset":offset,"PIDthrottle":0.7,"PIDsteering":-angle,"delta_time":delta_time,"frontcamera":img}, self.fstate)
                self.fstate.flush()

            except (OSError,ValueError,EOFError,BrokenPipeError):
                print("Lost connection to controller")
                self.fstate.close()
                self.fcmd.close()
                self.uobject.quit_game()


            if False:  # conditional debug info
                name = self.pawn.get_name()
                ue.log("{} at [{:8.1f} {:8.1f} {:8.1f}] [{:4}x{:4}] {:5} {:1} vmove {:5.4f} {:3.2f} reward={:10.1f} offset={:5.4f}".format(
                        name, location[0], location[1], location[2],
                        self.vcam.width, self.vcam.height, len(pixels), framelag, vmove.SteeringInput,
                        vmove.ThrottleInput, reward, offset))
    def on_preexit(self):
        ue.log("on preexit")
        try:
            self.fstate.close()
            self.fcmd.close()
        except:
            ue.log("Error closing pipes")
