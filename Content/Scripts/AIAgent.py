import unreal_engine as ue
import numpy as np
import math
from unreal_engine import FVector,FTransform,FRotator
from unreal_engine.classes import TextureRenderTarget2D,SceneComponent,SceneCaptureComponent2D
from unreal_engine.classes import Actor,SplineComponent,SkeletalMeshComponent
import subprocess
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

        #setup recording
        self.batchsz=100
        if self.batchsz != 0:
            self.batch=0
            self.images = np.zeros ([self.batchsz, self.height, self.width, 3])
            self.controls =np.zeros ([self.batchsz, 2])
            ue.log("images={},controls={}".format(self.images.shape,self.controls.shape))
            self.outputidx=0
            self.batchidx=0
            self.maxidx=self.batchsz
            ue.log("search path ".format(sys.path))
            self.h5process=subprocess.Popen(["python", "Content/Scripts/2h5.py"], stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.output = self.h5process.stdin
            pickle.dump((self.batchsz, self.width, self.height), self.output)


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

            #record
            if self.batchsz != 0 :

                self.images[self.batchidx]=img
                self.controls[self.batchidx]=[vmove.SteeringInput,vmove.ThrottleInput]
                self.batchidx+=1
                self.outputidx+=1
                if (self.batchidx >= self.batchsz):
                    ue.log("Output to 2h5.py {} {}".format(self.maxidx,np.sum(self.images)))
                    pickle.dump(self.images, self.output )
                    pickle.dump(self.controls, self.output )
                    self.maxidx += self.batchsz
                    self.batchidx=0
                    self.images = np.zeros((self.batchsz, self.height, self.width, 3), np.uint8)
                    self.controls = np.zeros((self.batchsz, 2))
                    self.output.flush()