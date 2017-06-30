// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "Components/ActorComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "ATextureReader.generated.h"
#define DEPTH 4
UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class AROBOCAR_API UATextureReader : public UActorComponent
{
	GENERATED_BODY()
    
	UPROPERTY(Category = HeightMap, EditAnywhere)
	UTextureRenderTarget2D* RenderTarget;
    
    UPROPERTY( EditAnywhere)
    int width;
    UPROPERTY( EditAnywhere)
    int height;
    
    UFUNCTION(BlueprintCallable, Category = "HeightMap|Texture Helper")
    int StartReadPixels();
    
    UFUNCTION(BlueprintCallable, Category = "HeightMap|Texture Helper")
    void SetWidthHeight(int w,int h);
    
    UFUNCTION(BlueprintCallable, Category = "HeightMap|Texture Helper")
    bool GetBuffer(TArray<FColor> &pixels, int &frame, int &curframe);
    
private:
    struct context {
        bool bReadPixelsStarted;
        bool bBufferReady;
        uint32 frame;
        FRenderCommandFence ReadPixelFence;  
        TArray<FColor> Pixels;     
    };
    struct context buffers[DEPTH];
    int lastindex=0;
    int fillindex=0;
    
public:	
	// Sets default values for this component's properties
	UATextureReader();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

		
	
};
