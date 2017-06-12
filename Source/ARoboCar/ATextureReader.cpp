// Fill out your copyright notice in the Description page of Project Settings.

#include "ARoboCar.h"
#include "ATextureReader.h"


#define print(format,...) UE_LOG(LogTemp, Log, TEXT(format), ##__VA_ARGS__)

// Sets default values for this component's properties
UATextureReader::UATextureReader()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;
	// ...
}


// Called when the game starts
void UATextureReader::BeginPlay()
{
	Super::BeginPlay();
    print("Texture Reader begin play Here");
    if(RenderTarget==NULL)return;
    FTextureRenderTarget2DResource* RenderResource = (FTextureRenderTarget2DResource*)RenderTarget->Resource;
    this->height=RenderResource->GetSizeXY().Y;
    //RenderTarget->SizeX=w;
	// ...
	
}
void UATextureReader::SetWidthHeight(int w,int h)
{
    this->height=h;
    this->width=w;
    RenderTarget->InitAutoFormat( w, h);
    FTextureRenderTarget2DResource* RenderResource = (FTextureRenderTarget2DResource*)RenderTarget->Resource;
    print("set hw %d %d",RenderResource->GetSizeXY().Y,RenderResource->GetSizeXY().X)
    //RenderTarget->SizeX=w;
   //RenderTarget->SizeY=h;
}

// Called every frame
void UATextureReader::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    //print("Texture Reader tick %d",RenderTarget != NULL);
    StartReadPixels();
}


bool UATextureReader::GetBuffer(TArray<FColor> &buf, int &frame)
{
    struct context *ctx= &buffers[lastindex];
    if (ctx->bBufferReady) {
        //print("GetBuffer %d %d",lastindex,this->Pixels[lastindex].Num());
        buf = ctx->Pixels; 
        frame=GFrameCounter-ctx->frame;
        return true;
    } else {
        print("GetBuffer no data available");
        return false;
    }
}

void UATextureReader::StartReadPixels()
{
    if(RenderTarget==NULL)return;
	//borrowed from RenderTarget::ReadPixels()
	FTextureRenderTarget2DResource* RenderResource = (FTextureRenderTarget2DResource*)RenderTarget->Resource;
 
	// Read the render target surface data back.	
	struct FReadSurfaceContext
	{
		FRenderTarget* SrcRenderTarget;
		TArray<FColor>* OutData;
		FIntRect Rect;
		FReadSurfaceDataFlags Flags;
        uint32 frame;
        bool *bBufferReadyp;
        int index;
        int *lastp;
	};
    struct context *ctx= &buffers[fillindex];
	//Pixels.Reset();
	FReadSurfaceContext ReadSurfaceContext =
	{
		RenderResource,
		&ctx->Pixels,
		FIntRect(0, 0, RenderResource->GetSizeXY().X, RenderResource->GetSizeXY().Y),
		FReadSurfaceDataFlags(RCM_UNorm, CubeFace_MAX),
        GFrameNumber,
        &ctx->bBufferReady,
        fillindex,
        &lastindex
	};
    ctx->ReadPixelFence.BeginFence();
	ctx->bReadPixelsStarted = true; 
    ctx->bBufferReady = false; 
    ctx->frame = GFrameCounter;  // Game thread 
    fillindex = (fillindex +1)%DEPTH;
    //print("Queue Reading %d %d",ReadSurfaceContext.OutData->Num(),ReadSurfaceContext.frame);
	ENQUEUE_UNIQUE_RENDER_COMMAND_ONEPARAMETER(
		ReadSurfaceCommand,
		FReadSurfaceContext, Context, ReadSurfaceContext,
		{
            //print("Start Reading %d %d %d",Context.OutData->Num(),Context.frame,GFrameNumberRenderThread);
			RHICmdList.ReadSurfaceData(
			Context.SrcRenderTarget->GetRenderTargetTexture(),
				Context.Rect,
				*Context.OutData,
				Context.Flags
				);
            //print("Done Reading %d %d %d",Context.OutData->Num(),Context.frame,GFrameNumberRenderThread);
            *Context.lastp = Context.index;
            *Context.bBufferReadyp = true;
		});
}

