// Copyright 1998-2017 Epic Games, Inc. All Rights Reserved.
#pragma once
#include "GameFramework/GameModeBase.h"
#include "ARoboCarGameMode.generated.h"

UCLASS(minimalapi)
class AARoboCarGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AARoboCarGameMode();
    void BeginPlay();
};



