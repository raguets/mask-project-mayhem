"""One-time source adapters. Does not launch or mutate Unreal assets."""
from pathlib import Path
P=Path(__file__).resolve().parents[2];S=P/'Source/VehicularCombat/Private';T=P/'Tools/Art'
f=S/'Core/CustomGameMode.cpp';c=f.read_text(encoding='utf-8-sig')
c=c.replace('Choice==TEXT("Switchblade");','Choice==TEXT("Switchblade") || Choice==TEXT("Manta");')
c=c.replace('TEXT("/Game/MASK/Switchblade/BP_Switchblade.BP_Switchblade_C")};','TEXT("/Game/MASK/Switchblade/BP_Switchblade.BP_Switchblade_C"),TEXT("/Game/MASK/Manta/BP_Manta.BP_Manta_C")};')
c=c.replace('FMath::Min(TrainingBotCount,5)','FMath::Min(TrainingBotCount,6)');f.write_text(c,encoding='utf-8')
c=(T/'import_raven_all.py').read_text(encoding='utf-8-sig').replace('RAVEN','MANTA').replace('raven','manta').replace('calhoun','vanessa')
c+="\nexec(compile((P/'Tools/Art/finalize_manta.py').read_text(encoding='utf-8-sig'),'<manta-contract>','exec'))\n"
(T/'import_manta_all.py').write_text(c,encoding='utf-8')
for name in ['Import','Test']:
    f=P/f'Tools/Migration/{name}-Raven.ps1';c=f.read_text(encoding='utf-8-sig').replace('Raven','Manta').replace('raven','manta').replace('RAVEN','MANTA')
    c=c.replace('?Vehicle=Thunderhawk?Bots=3','?Vehicle=Manta?Bots=6')
    (f.parent/f'{name}-Manta.ps1').write_text(c,encoding='utf-8')
# Adapt the actual Pinewoods control fixture, retaining explicit placement disclosure.
c=(S/'Tests/RavenSmoke.cpp').read_text(encoding='utf-8-sig').replace('Raven','Manta').replace('raven','manta')
c=c.replace('#include "MASK/MantaPawn.h"','#include "MASK/MantaPawn.h"\n#include "Engine/StaticMesh.h"')
c=c.replace('Names.Contains(TEXT("Manta")))','Names.Contains(TEXT("Raven")) && Names.Contains(TEXT("Manta")) && Names.Contains(TEXT("Condor")) && Names.Contains(TEXT("Switchblade")))')
c=c.replace('all_four_vehicle_families_present','all_seven_vehicle_families_present')
c=c.replace('GM && GM->SwitchPlayerVehicleTo(PC,Manta.Get())','PC->GetPawn()==Manta.Get() || (GM && GM->SwitchPlayerVehicleTo(PC,Manta.Get()))')
c=c.replace('definition_and_calhoun','definition_and_vanessa').replace('Calhoun Burns','Vanessa Warfield')
marker='            Check(TEXT("fixed_wing_no_hover")'
i=c.index(marker)
c=c[:i]+'''            Check(TEXT("venom_faction"),Car->Definition->Faction==EMaskFaction::Venom);
            bool Outside=true;int32 BaseMeshes=0;
            for(TActorIterator<AActor> I(W);I;++I) {
                TArray<UStaticMeshComponent*> Components;I->GetComponents(Components);
                for(auto* C:Components) { if(C->GetStaticMesh() && C->GetStaticMesh()->GetPathName().Contains(TEXT("BoulderHill"))) {
                    ++BaseMeshes;const FBox B=C->Bounds.GetBox().ExpandBy(FVector(500,500,0));const FVector P=Car->GetActorLocation();
                    Outside &= P.X<B.Min.X || P.X>B.Max.X || P.Y<B.Min.Y || P.Y>B.Max.Y;
                } }
            }
            Check(TEXT("natural_spawn_outside_mask_base"),Outside && BaseMeshes>0);
            Data->SetStringField(TEXT("natural_spawn"),Car->GetActorLocation().ToString());Shot(TEXT("spawn.png"));
'''+c[i:]
a=c.index('            TArray<UStaticMeshComponent*> Visuals;');b=c.index('            const float Command=',a)
c=c[:a]+'''            TArray<UStaticMeshComponent*> Visuals;Manta->GetComponents(Visuals);int32 WheelParts=0;
            for(auto* Part:Visuals) { if(Part->GetName().StartsWith(TEXT("SM_MA_")) && Part->GetName().Len()==8) { ++WheelParts; } }
            Check(TEXT("four_persistent_wheel_visuals"),WheelParts==4);
'''+c[b:]
c=c.replace('Actual Pinewoods map, four-vehicle fleet, explicit placement','Actual Pinewoods map, seven-vehicle fleet. Natural VENOM exterior spawn checked BEFORE explicit placement')
c=c.replace('Pinewoods four-vehicle fleet','Pinewoods seven-vehicle fleet')
(S/'Tests/MantaSmoke.cpp').write_text(c,encoding='utf-8')
