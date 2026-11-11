#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DynamicsSmoke.generated.h"

/** Opt-in test fixture only; no persistent map or art asset is modified. */
UCLASS()
class ADynamicsTestFloor : public AActor
{
	GENERATED_BODY()
public: ADynamicsTestFloor();
};
