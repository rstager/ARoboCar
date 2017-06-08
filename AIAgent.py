import unreal_engine as ue
import pickle
import numpy as np

class Driver:
    
    def begin_play(self):
        ue.log('Driver Begin Play')

        # get a reference to the owing pawn (a character)
        self.pawn = self.uobject.get_owner()
        ue.log(self.pawn.get_name())
        self.pawn.EnableIncarView(True)
        # need to see if this is legal to cache the texture
        self.texture=self.uobject.get_owner().get_actor_component_by_type(ue.find_class('ATextureReader'))
        self.texture.SetWidthHeight(160,90)

    def tick(self,delta_time):
        valid, pixels,framelag =self.texture.GetBuffer()
        if(valid): 
            width=self.texture.width
            height=self.texture.height
            location = self.pawn.get_actor_location()
            rotation = self.pawn.get_actor_rotation()
            properties_list = self.pawn.properties()
            name = self.pawn.get_name()
            ue.log("{} at [{} {} {}] [{}x{}] {} {}".format(name,location[0],location[1],location[2],width,height,len(pixels),framelag))
            img=np.array(pixels).reshape((height,width,4)).astype(np.uint8)[:,:,0:3]
            #pickle.dump( img, open( "viewport.data", "wb" ) )
            #
            # Control side
            #
            vmove=self.pawn.VehicleMovement
            vmove.BrakeInput= 0
            #ue.log("Brake={} ".format(vmove.BrakeInput))
            vmove.SteeringInput=0.0
            vmove.ThrottleInput=0.7
