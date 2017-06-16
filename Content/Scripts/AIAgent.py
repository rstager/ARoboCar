import unreal_engine as ue
import numpy as np
import math
from unreal_engine import FVector,FTransform,FRotator
from unreal_engine.classes import TextureRenderTarget2D,SceneComponent,SceneCaptureComponent2D
from unreal_engine.classes import Actor,SplineComponent,SkeletalMeshComponent
#import os
#os.environ["HDF5_DISABLE_VERSION_CHECK"]="1"
#import h5py
import pickle

class SplinePath:
    def __init__(self,actor,label):
        landscape=actor.get_world().find_actor_by_label(label)
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
        offset=(rvector-location).length
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
        #self.scene_capture= actor.actor_create_default_subobject(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture")
        #self.scene_capture = actor.ConstructObject(ue.find_class('SceneCaptureComponent2D'),
                                                                  #label + "_scenecapture")
        #self.scene_capture= actor.add_actor_component(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture")
        self.scene_capture.set_relative_location(offset[0],offset[1],offset[2])
        self.scene_capture.set_relative_rotation(rot[0],rot[1],rot[2])
        #print(self.scene_capture.get_actor())
        #ret=self.scene_capture.attach_to_actor(actor)
        #print (ret)
        #mesh=actor.get_actor_component_by_type(SkeletalMeshComponent)
        #print("mesh",mesh)
        #self.scene_capture.attach_to_component(mesh)#.get_actor_component_by_type(),"ATTACHMENT_RULE_SNAP_TO_TARGET")

        #UWhateverComponent * NewComponent = ConstructObject < UWhateverComponent > (UWhateverComponent::StaticClass(), this, TEXT("ComponentName"));

        #NewComponent->RegisterComponent();
        #NewComponent->OnComponentCreated(); //Might not need this.
        #NewComponent->AttachTo(GetRootComponent(), SocketName / * NAME_None * /);
        #SpringArm = CreateDefaultSubobject < USpringArmComponent > (TEXT("SpringArm"));
        #SpringArm->SetRelativeLocation(FVector(0.0
        #SpringArm->SetupAttachment(RootComponent);


        #self.scene_capture= actor.add_actor_component(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture")
        #self.scene_capture= actor.AddComponent(ue.find_class('SceneCaptureComponent2D'),label+"_scenecapture",xform)
        self.scene_capture.set_property("TextureTarget",self.rendertarget)
        #print(dir(self.scene_capture.__class__))
        #print("is actor",self.scene_capture.is_a(Actor))
        #print("is actor",actor.is_a(Actor))
        #self.scene_capture.SetupAttachment(actor.RootComponent)
        #self.scene_capture.SetRelativeTransform(xform)
        #self.scene_capture.set_relative_location(FVector(offset[0],offset[1],offset[2]))
        for c in actor.get_actor_components():
            if(c.is_a(ue.find_class('SceneCaptureComponent2D'))):
                ue.log("{} {} {} {} {}".format(c.get_name(),c.get_relative_location(),c.get_property('AttachParent'),c.get_property('bAbsoluteLocation'),c.get_property('Mobility')))
                properties_list = c.properties()
                #print(properties_list)

        # add reader last
        self.reader = actor.add_actor_component(ue.find_class('ATextureReader'),label+"_rendertarget")
        self.reader.set_property('RenderTarget',self.rendertarget)
        self.reader.SetWidthHeight(sz[0],sz[1])
    def capture(self):
        return self.reader.GetBuffer() # valid, pixels,framelag

class Driver:
    def __init__(self):

        pass
    def begin_play(self):
        self.pawn = self.uobject.get_owner()
        ue.log("Driver Begin Play {}".format(self.pawn.get_name()))

        self.height=90
        self.width=160

        self.path=SplinePath(self.pawn,'Racetrack1')
        self.vcam=Vcam(self.pawn,"frontcamera",[self.width,self.height],[0,0,100],[0,-10,0])

        self.pawn.EnableIncarView(True)

        #setup h5
        self.batchsz=0
        if self.batchsz != 0:
            self.maxidx = self.batchsz
            self.output = h5py.File("robocar.hdf5", 'w')
            self.images = self.output.create_dataset('frontcamera', (self.maxidx, self.width, self.height, 4), 'i1', maxshape=(None, self.width, self.height, 4))
            self.images.attrs['description'] = "simple test"
            self.controls = self.output.create_dataset('steering.throttle', (self.maxidx, 2), maxshape=(None, 2))
            self.h5idx=0
            self.output.flush()

    def tick(self,delta_time):
        if not hasattr(self, 'vcam'):
            return
        valid, pixels,framelag =self.vcam.capture()
        if(valid):
            location = self.pawn.get_actor_location()
            rotation = self.pawn.get_actor_rotation()
            camloc=self.vcam.scene_capture.get_world_location()
            if True:
                properties_list = self.pawn.properties()
                name = self.pawn.get_name()
                ue.log("{} at [{} {} {}] [{}x{}] {} {} vcam {} {} {}".format(name,location[0],location[1],location[2],
                                                               self.vcam.width,self.vcam.height,len(pixels),framelag,camloc[0],camloc[1],camloc[2]))
            img=np.array(pixels).reshape((self.vcam.height,self.vcam.width,4)).astype(np.uint8)[:,:,0:3]
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
            pickle.dump(img, open("viewport.data", "wb"))
            #record in H5
            if self.batchsz != 0 :
                self.images[self.h5idx]=img
                self.control[self.h5idx]=[vmove.SteeringInput,vmove.ThrottleInput]
                self.h5idx+=1
                if (self.h5idx > self.maxidx):
                    self.maxidx += self.batchsz
                    self.images.resize((self.maxidx,self.height,self.width,4))
                    self.controls.resize((self.maxidx,2))
                    self.output.flush()