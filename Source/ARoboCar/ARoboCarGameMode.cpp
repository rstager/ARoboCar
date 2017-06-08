// Copyright 1998-2017 Epic Games, Inc. All Rights Reserved.

#include "ARoboCar.h"
#include "ARoboCarGameMode.h"
#include "ARoboCarPawn.h"
#include "ARoboCarHud.h"
#include "Engine.h"

AARoboCarGameMode::AARoboCarGameMode()
{
	DefaultPawnClass = AARoboCarPawn::StaticClass();
	HUDClass = AARoboCarHud::StaticClass();
    //GEngine->GameUserSettings->SetScreenResolution(FIntPoint(640,480));
}
 void AARoboCarGameMode::BeginPlay()
 {
     // ... your code ...
     if(GEngine)
     {
         UGameUserSettings* MyGameSettings = GEngine->GetGameUserSettings();
         MyGameSettings->SetScreenResolution(FIntPoint(640,360));
         //MyGameSettings->SetFullscreenMode(EWindowMode::Fullscreen);
         MyGameSettings->SetVSyncEnabled(true);
         MyGameSettings->ApplySettings(false);
     }
     
     // ... your code ...
 }