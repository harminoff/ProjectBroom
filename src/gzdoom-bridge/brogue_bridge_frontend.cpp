/*
 * Brogue CE -> GZDoom source-build integration.
 *
 * The Brogue adapter is loaded as a DLL in the same process. This keeps the
 * C global namespace of Brogue isolated from GZDoom while preserving the
 * required synchronous, in-process simulation boundary.
 */
#include "brogue_bridge_frontend.h"

#include "BrogueBridge.h"
#include "c_dispatch.h"
#include "c_cvars.h"
#include "d_event.h"
#include "doomstat.h"
#include "g_levellocals.h"
#include "keydef.h"
#include "p_local.h"
#include "p_pspr.h"
#include "g_statusbar/sbar.h"
#include "v_video.h"
#include "v_draw.h"
#include "v_font.h"

#include <algorithm>
#include <cstdint>
#include <cstring>
#include <iterator>
#include <cmath>
#include <unordered_map>
#include <vector>
#include <string>

#ifdef _WIN32
#include <windows.h>
#undef DrawText
#endif

CVAR(Int, brg_seed, 1, CVAR_ARCHIVE | CVAR_GLOBALCONFIG)
CVAR(Int, brg_monster_anim_tics, 5, CVAR_ARCHIVE | CVAR_GLOBALCONFIG)
CVAR(Bool, brg_monster_omniscience, false, CVAR_ARCHIVE | CVAR_GLOBALCONFIG)
CVAR(Int, brg_compare_pid, 0, 0)
CVAR(Float, brg_hud_scale, 1.0, CVAR_ARCHIVE | CVAR_GLOBALCONFIG)
CVAR(Bool, brg_debug, false, CVAR_ARCHIVE | CVAR_GLOBALCONFIG)
CVAR(Int, brg_fx_quality, 1, CVAR_ARCHIVE | CVAR_GLOBALCONFIG)

namespace
{
using BridgeInitialize = BrogueBridgeResult (*)();
using BridgeStartGame = BrogueBridgeResult (*)(uint64_t);
using BridgeGetState = BrogueBridgeResult (*)(BrogueBridgeState *);
using BridgeGetMonsterCatalog = BrogueBridgeResult (*)(BrogueBridgeMonsterCatalog *);
using BridgePerformAction = BrogueBridgeResult (*)(BrogueBridgeAction, BrogueBridgeTurnResult *);
using BridgePerformCommand = BrogueBridgeResult (*)(const BrogueBridgeCommand *, BrogueBridgeTurnResult *);
using BridgePreviewThrow = BrogueBridgeResult (*)(uint64_t, int32_t, int32_t, BrogueBridgeThrowPreview *);
using BridgeInspectCell = BrogueBridgeResult (*)(int32_t, int32_t, BrogueBridgeLookResult *);
using BridgeShutdown = void (*)();
using BridgeResultName = const char *(*)(BrogueBridgeResult);

struct BridgeApi
{
#ifdef _WIN32
	HMODULE module = nullptr;
#endif
	BridgeInitialize initialize = nullptr;
	BridgeStartGame startGame = nullptr;
	BridgeGetState getState = nullptr;
	BridgeGetMonsterCatalog getMonsterCatalog = nullptr;
	BridgePerformAction performAction = nullptr;
	BridgePerformCommand performCommand = nullptr;
	BridgePreviewThrow previewThrow = nullptr;
	BridgeInspectCell inspectCell = nullptr;
	BridgeShutdown shutdown = nullptr;
	BridgeResultName resultName = nullptr;
};

BridgeApi Api;
BrogueBridgeState State{};
BrogueBridgeMonsterCatalog MonsterCatalog{};
bool Loaded = false;
bool Started = false;
bool PendingWait = false;
std::vector<BrogueBridgeAction> PendingActions;
size_t PendingActionIndex = 0;
FFont *BrogueUiFont = nullptr;
FFont *BrogueMapFont = nullptr;

struct ItemProxy
{
	uint64_t id = 0;
	int category = 0;
	int visualKind = -1;
	int x = -1;
	int y = -1;
	AActor *actor = nullptr;
	bool spawnAttempted = false;
};

std::vector<ItemProxy> ItemProxies;
FLevelLocals *ItemProxyLevel = nullptr;
int LastLoggedItemCount = -1;
int LastLoggedVisibleItemCount = -1;

struct DoorProxy
{
	int x = -1;
	int y = -1;
	double yaw = 0.0;
	PClassActor *presentationType = nullptr;
	AActor *actor = nullptr;
};

enum class CellFxKind
{
	None,
	Lava,
	Fire,
	Gas,
};

struct CellFxProxy
{
	int x = -1;
	int y = -1;
	CellFxKind kind = CellFxKind::None;
	bool seen = false;
	AActor *actor = nullptr;
};

std::vector<DoorProxy> DoorProxies;
FLevelLocals *DoorProxyLevel = nullptr;
std::unordered_map<int, CellFxProxy> CellFxProxies;
FLevelLocals *CellFxProxyLevel = nullptr;
int LastLoggedCellFxCount = -1;
AActor *FallShaftMarker = nullptr;
FLevelLocals *FallShaftLevel = nullptr;
bool PendingFallShaft = false;
int PendingFallLandingX = -1;
int PendingFallLandingY = -1;

struct MonsterProxy
{
	uint64_t id = 0;
	int kind = -1;
	int presentationKind = -1;
	int x = -1;
	int y = -1;
	int hp = 0;
	int maxHp = 0;
	BrogueBridgeVisibility visibility = BROGUE_VISIBILITY_HIDDEN;
	bool ally = false;
	AActor *actor = nullptr;
	DVector3 moveFrom{};
	DVector3 moveTo{};
	int moveTics = 0;
	int moveTotal = 0;
	int pulseTics = 0;
	int deathTics = 0;
};

std::unordered_map<uint64_t, MonsterProxy> MonsterProxies;
FLevelLocals *MonsterProxyLevel = nullptr;
int LastLoggedMonsterCount = -1;
int LastLoggedDirectMonsterCount = -1;
BrogueBridgeAction BufferedAction = BROGUE_ACTION_WAIT;
bool HasBufferedAction = false;

enum class WeaponUiMode { None, Equip, ThrowSelect, ThrowTarget, Look };
WeaponUiMode WeaponUi = WeaponUiMode::None;
int WeaponSelection = 0;
uint64_t ThrowItemId = 0;
int TargetX = 0;
int TargetY = 0;
AActor *TargetMarker = nullptr;
std::vector<AActor *> PathMarkers;
BrogueBridgeLookResult LookResult{};

struct ProjectileAnimation
{
	AActor *actor = nullptr;
	std::vector<DVector3> points;
	size_t point = 0;
	int tics = 0;
};
ProjectileAnimation Projectile;
uint64_t LastVisualWeaponId = 0;

bool InventoryOpen = false;
int InventorySelection = 0;
enum class ApplyUiMode { None, Confirm, SelectItem };
ApplyUiMode ApplyUi = ApplyUiMode::None;
uint64_t ApplyItemId = 0;
std::vector<uint64_t> ApplyChoiceIds;
int ApplyChoiceSelection = 0;
FString ApplyPrompt;
bool CommandConfirmationOpen = false;
BrogueBridgeCommand CommandConfirmationCommand{};
FString CommandConfirmationPrompt;
FString CommandConfirmationSource;

#ifdef _WIN32
HWND ComparisonWindow = nullptr;
bool ComparisonKeysDown[9]{};
#endif

void CloseWeaponUi();
void BeginTargeting(uint64_t itemId);
void RefreshTargeting();

constexpr int BrogueMapWidth = 79;

DVector3 BrogueCellToWorld(int x, int y)
{
	const double worldX = x * 64.0 + 32.0;
	const double worldY = (28 - y) * 64.0 + 32.0;
	double worldZ = 0.0;
	if (primaryLevel != nullptr)
	{
		sector_t *sector = primaryLevel->PointInSector(worldX, worldY);
		if (sector != nullptr) worldZ = sector->floorplane.ZatPoint(worldX, worldY);
	}
	return DVector3(worldX, worldY, worldZ);
}

bool IsBrogueMap()
{
	if (primaryLevel == nullptr) return false;
	const char *name = primaryLevel->MapName.GetChars();
	return name != nullptr
		&& (name[0] == 'B' || name[0] == 'b')
		&& (name[1] == 'R' || name[1] == 'r')
		&& (name[2] == 'G' || name[2] == 'g');
}

#ifdef _WIN32
FString BridgeLibraryPath()
{
	wchar_t modulePath[32768];
	DWORD length = GetModuleFileNameW(nullptr, modulePath, DWORD(std::size(modulePath)));
	if (length == 0 || length >= std::size(modulePath)) return "";

	while (length > 0 && modulePath[length - 1] != L'\\' && modulePath[length - 1] != L'/')
		--length;
	modulePath[length] = L'\0';

	wchar_t dllPath[32768];
	wcscpy_s(dllPath, modulePath);
	wcscat_s(dllPath, L"brogue-bridge.dll");

	int needed = WideCharToMultiByte(CP_UTF8, 0, dllPath, -1, nullptr, 0, nullptr, nullptr);
	if (needed <= 0) return "";
	FString result;
	char *buffer = result.LockNewBuffer(needed);
	WideCharToMultiByte(CP_UTF8, 0, dllPath, -1, buffer, needed, nullptr, nullptr);
	result.UnlockBuffer();
	return result;
}

template <typename T>
T GetBridgeProc(HMODULE module, const char *name)
{
	return reinterpret_cast<T>(GetProcAddress(module, name));
}
#endif

bool LoadBridge()
{
	if (Loaded) return true;

#ifdef _WIN32
	FString path = BridgeLibraryPath();
	if (path.IsEmpty())
	{
		Printf("Brogue bridge: could not resolve brogue-bridge.dll beside the engine.\n");
		return false;
	}

	Api.module = LoadLibraryA(path.GetChars());
	if (Api.module == nullptr)
	{
		Printf("Brogue bridge: could not load %s (error %lu).\n", path.GetChars(), GetLastError());
		return false;
	}

	Api.initialize = GetBridgeProc<BridgeInitialize>(Api.module, "brogue_bridge_initialize");
	Api.startGame = GetBridgeProc<BridgeStartGame>(Api.module, "brogue_bridge_start_game");
	Api.getState = GetBridgeProc<BridgeGetState>(Api.module, "brogue_bridge_get_state");
	Api.getMonsterCatalog = GetBridgeProc<BridgeGetMonsterCatalog>(Api.module, "brogue_bridge_get_monster_catalog");
	Api.performAction = GetBridgeProc<BridgePerformAction>(Api.module, "brogue_bridge_perform_action");
	Api.performCommand = GetBridgeProc<BridgePerformCommand>(Api.module, "brogue_bridge_perform_command");
	Api.previewThrow = GetBridgeProc<BridgePreviewThrow>(Api.module, "brogue_bridge_preview_throw");
	Api.inspectCell = GetBridgeProc<BridgeInspectCell>(Api.module, "brogue_bridge_inspect_cell");
	Api.shutdown = GetBridgeProc<BridgeShutdown>(Api.module, "brogue_bridge_shutdown");
	Api.resultName = GetBridgeProc<BridgeResultName>(Api.module, "brogue_bridge_result_name");
#else
	Printf("Brogue bridge: this source integration currently requires Windows.\n");
	return false;
#endif

	if (Api.initialize == nullptr || Api.startGame == nullptr || Api.getState == nullptr
		|| Api.getMonsterCatalog == nullptr
		|| Api.performAction == nullptr || Api.performCommand == nullptr || Api.previewThrow == nullptr
		|| Api.inspectCell == nullptr
		|| Api.shutdown == nullptr || Api.resultName == nullptr)
	{
		Printf("Brogue bridge: DLL is missing a required API export.\n");
#ifdef _WIN32
		FreeLibrary(Api.module);
		Api.module = nullptr;
#endif
		return false;
	}

	Loaded = true;
	return true;
}

void SyncPlayer()
{
	if (!Started || primaryLevel == nullptr || players[consoleplayer].mo == nullptr) return;

	AActor *pawn = players[consoleplayer].mo;
	const DVector3 world = BrogueCellToWorld(State.player.x, State.player.y);
	pawn->SetOrigin(world.X, world.Y, world.Z, false);
	players[consoleplayer].health = (std::max)(0, State.player.hp);
	pawn->health = (std::max)(0, State.player.hp);
}

int PickupVisualKind(const BrogueBridgeItemState &item)
{
	// Brogue randomizes the apparent identities of these categories. Until
	// Brogue marks the kind known, select the category-generic model so the 3D
	// frontend cannot reveal information that the simulation has withheld.
	const bool categoryHidesIdentity = item.category == 8   // POTION
		|| item.category == 16   // SCROLL
		|| item.category == 32   // STAFF
		|| item.category == 64   // WAND
		|| item.category == 128; // RING
	if (categoryHidesIdentity && !item.kindKnown) return -1;
	// Brogue's single-kind special categories (gold, amulet and gemstone)
	// use kind=-1 internally because no catalog lookup is needed. The visual
	// registry gives each category a single canonical model at kind zero.
	return item.kind < 0 ? 0 : item.kind;
}

FString PickupClassName(const BrogueBridgeItemState &item)
{
	FString name;
	const int visualKind = PickupVisualKind(item);
	if (visualKind < 0)
		name.Format("BroguePickupC%04dGeneric", item.category);
	else
		name.Format("BroguePickupC%04dK%02d", item.category, visualKind);
	return name;
}

const BrogueBridgeItemState *FindItem(uint64_t id)
{
	for (uint32_t index = 0; index < State.itemCount; ++index)
		if (State.items[index].id == id) return &State.items[index];
	return nullptr;
}

std::vector<uint32_t> CarriedWeaponIndices()
{
	std::vector<uint32_t> result;
	for (uint32_t index = 0; index < State.itemCount; ++index)
	{
		const BrogueBridgeItemState &item = State.items[index];
		if (item.carried && item.category == 2 && item.kind >= 0 && item.kind < 15)
			result.push_back(index);
	}
	std::sort(result.begin(), result.end(), [](uint32_t left, uint32_t right)
	{
		return State.items[left].inventoryOrder < State.items[right].inventoryOrder;
	});
	return result;
}

void SyncWeaponView()
{
	if (!Started || players[consoleplayer].mo == nullptr) return;
	player_t *player = &players[consoleplayer];
	const BrogueBridgeItemState *weapon = FindItem(State.player.equippedWeaponId);
	if (weapon == nullptr || weapon->category != 2 || weapon->kind < 0 || weapon->kind >= 15)
	{
		static uint64_t lastMissingId = UINT64_MAX;
		if (lastMissingId != State.player.equippedWeaponId)
		{
			Printf("Brogue weapon: no presentable equipped item for id=%llu (items=%u).\n",
				(unsigned long long)State.player.equippedWeaponId, State.itemCount);
			lastMissingId = State.player.equippedWeaponId;
		}
		if (LastVisualWeaponId == 0 && player->ReadyWeapon == nullptr) return;
		player->ReadyWeapon = nullptr;
		player->PendingWeapon = static_cast<AActor *>(WP_NOCHANGE);
		P_SetPsprite(player, PSP_WEAPON, nullptr);
		LastVisualWeaponId = 0;
		return;
	}

	FString className;
	className.Format("BrogueViewWeaponK%02d", weapon->kind);
	PClassActor *type = PClass::FindActor(className.GetChars());
	if (type == nullptr)
	{
		Printf("Brogue weapon: missing visual class %s.\n", className.GetChars());
		return;
	}
	AActor *visual = players[consoleplayer].mo->FindInventory(type);
	if (visual == nullptr) visual = players[consoleplayer].mo->GiveInventoryType(type);
	if (visual == nullptr)
	{
		Printf("Brogue weapon: GiveInventoryType rejected %s.\n", className.GetChars());
		return;
	}
	if (LastVisualWeaponId == weapon->id) return;
	player->ReadyWeapon = visual;
	player->PendingWeapon = static_cast<AActor *>(WP_NOCHANGE);
	P_SetupPsprites(player, true);
	LastVisualWeaponId = weapon->id;
	if (brg_debug)
		Printf("Brogue weapon: presenting id=%llu kind=%d class=%s.\n",
			(unsigned long long)weapon->id, weapon->kind, className.GetChars());
}

void PlayWeaponState(FName stateName)
{
	player_t *player = &players[consoleplayer];
	if (player->ReadyWeapon == nullptr) return;
	FState *state = player->ReadyWeapon->FindState(stateName);
	if (state != nullptr) P_SetPsprite(player, PSP_WEAPON, state);
}

void ClearItemProxies(bool destroyActors)
{
	if (destroyActors)
	{
		for (ItemProxy &proxy : ItemProxies)
		{
			if (proxy.actor != nullptr && !(proxy.actor->ObjectFlags & OF_EuthanizeMe))
				proxy.actor->Destroy();
		}
	}
	ItemProxies.clear();
}

ItemProxy *FindItemProxy(uint64_t id)
{
	for (ItemProxy &proxy : ItemProxies)
		if (proxy.id == id) return &proxy;
	return nullptr;
}

AActor *SpawnItemProxy(const BrogueBridgeItemState &item)
{
	FString className = PickupClassName(item);
	const DVector3 world = BrogueCellToWorld(item.x, item.y);
	AActor *actor = Spawn(primaryLevel, className.GetChars(), world, NO_REPLACE);
	if (actor == nullptr)
	{
		Printf("Brogue pickup: could not spawn %s for item %llu category=%d kind=%d.\n",
			className.GetChars(), (unsigned long long)item.id, item.category, item.kind);
		return nullptr;
	}
	if (!item.visible) actor->renderflags |= RF_INVISIBLE;
	return actor;
}

FString MonsterClassName(int presentationKind)
{
	FString name;
	name.Format("BrogueMonsterK%02d", (std::max)(0, presentationKind));
	return name;
}

void ClearMonsterProxies(bool destroyActors)
{
	if (destroyActors)
	{
		for (auto &entry : MonsterProxies)
		{
			AActor *actor = entry.second.actor;
			if (actor != nullptr && !(actor->ObjectFlags & OF_EuthanizeMe)) actor->Destroy();
		}
	}
	MonsterProxies.clear();
}

void ApplyMonsterVisibility(MonsterProxy &proxy)
{
	if (proxy.actor == nullptr) return;
	const bool shown = brg_monster_omniscience || proxy.visibility != BROGUE_VISIBILITY_HIDDEN;
	if (!shown)
	{
		proxy.actor->renderflags |= RF_INVISIBLE;
		proxy.actor->Alpha = 0.0;
		return;
	}
	proxy.actor->renderflags &= ~RF_INVISIBLE;
	proxy.actor->RenderStyle = proxy.visibility == BROGUE_VISIBILITY_SENSED
		? STYLE_Translucent : STYLE_Normal;
	proxy.actor->Alpha = proxy.visibility == BROGUE_VISIBILITY_SENSED ? 0.38 : 1.0;
	if (proxy.ally) proxy.actor->flags |= MF_FRIENDLY;
	else proxy.actor->flags &= ~MF_FRIENDLY;
}

AActor *SpawnMonsterProxy(const BrogueBridgeCreatureState &creature)
{
	const int visualKind = creature.presentationKind >= 0 ? creature.presentationKind : creature.kind;
	const FString className = MonsterClassName(visualKind);
	const DVector3 world = BrogueCellToWorld(creature.x, creature.y);
	AActor *actor = Spawn(primaryLevel, className.GetChars(), world, NO_REPLACE);
	if (actor == nullptr)
	{
		Printf("Brogue monster: could not spawn %s for entity %llu kind=%d.\n",
			className.GetChars(), (unsigned long long)creature.id, creature.kind);
		return nullptr;
	}
	actor->health = creature.hp;
	return actor;
}

void BeginMonsterEventAnimations(const BrogueBridgeTurnResult *result)
{
	if (result == nullptr) return;
	for (uint32_t index = 0; index < result->eventCount; ++index)
	{
		const BrogueBridgeEvent &event = result->events[index];
		if (event.type == BROGUE_EVENT_ATTACK_ATTEMPTED)
		{
			auto found = MonsterProxies.find(event.sourceEntityId);
			if (found != MonsterProxies.end()) found->second.pulseTics = 4;
		}
		else if (event.type == BROGUE_EVENT_ENTITY_DAMAGED)
		{
			auto found = MonsterProxies.find(event.targetEntityId);
			if (found != MonsterProxies.end()) found->second.pulseTics = 5;
		}
		else if (event.type == BROGUE_EVENT_ENTITY_DIED)
		{
			auto found = MonsterProxies.find(event.targetEntityId);
			if (found != MonsterProxies.end()) found->second.deathTics = 7;
		}
	}
}

void SyncMonsters(const BrogueBridgeTurnResult *result = nullptr)
{
	if (!Started || primaryLevel == nullptr) return;
	if (MonsterProxyLevel != primaryLevel)
	{
		ClearMonsterProxies(false);
		MonsterProxyLevel = primaryLevel;
		LastLoggedMonsterCount = LastLoggedDirectMonsterCount = -1;
	}
	BeginMonsterEventAnimations(result);

	std::vector<uint64_t> liveIds;
	liveIds.reserve(State.creatureCount);
	int directCount = 0;
	for (uint32_t index = 0; index < State.creatureCount; ++index)
	{
		const BrogueBridgeCreatureState &creature = State.creatures[index];
		if (!creature.alive || creature.x < 0 || creature.y < 0) continue;
		liveIds.push_back(creature.id);
		if (creature.visibility == BROGUE_VISIBILITY_DIRECT) ++directCount;
		const int visualKind = creature.presentationKind >= 0 ? creature.presentationKind : creature.kind;
		auto inserted = MonsterProxies.emplace(creature.id, MonsterProxy{});
		MonsterProxy &proxy = inserted.first->second;
		if (inserted.second) proxy.id = creature.id;
		if (proxy.actor != nullptr && proxy.presentationKind != visualKind)
		{
			if (!(proxy.actor->ObjectFlags & OF_EuthanizeMe)) proxy.actor->Destroy();
			proxy.actor = nullptr;
		}
		if (proxy.actor == nullptr) proxy.actor = SpawnMonsterProxy(creature);
		if (!inserted.second && proxy.actor != nullptr && (proxy.x != creature.x || proxy.y != creature.y))
		{
			proxy.moveFrom = proxy.actor->Pos();
			proxy.moveTo = BrogueCellToWorld(creature.x, creature.y);
			proxy.moveTotal = proxy.moveTics = (std::max)(1, int(brg_monster_anim_tics));
			const double dx = proxy.moveTo.X - proxy.moveFrom.X;
			const double dy = proxy.moveTo.Y - proxy.moveFrom.Y;
			if (dx != 0.0 || dy != 0.0)
				proxy.actor->Angles.Yaw = DAngle::fromDeg(std::atan2(dy, dx) * 57.29577951308232);
		}
		proxy.kind = creature.kind;
		proxy.presentationKind = visualKind;
		proxy.x = creature.x;
		proxy.y = creature.y;
		proxy.hp = creature.hp;
		proxy.maxHp = creature.maxHp;
		proxy.visibility = creature.visibility;
		proxy.ally = creature.isAlly != 0;
		if (proxy.actor != nullptr) proxy.actor->health = creature.hp;
		ApplyMonsterVisibility(proxy);
	}

	for (auto iterator = MonsterProxies.begin(); iterator != MonsterProxies.end();)
	{
		const bool alive = std::find(liveIds.begin(), liveIds.end(), iterator->first) != liveIds.end();
		if (!alive && iterator->second.deathTics == 0)
		{
			AActor *actor = iterator->second.actor;
			if (actor != nullptr && !(actor->ObjectFlags & OF_EuthanizeMe)) actor->Destroy();
			iterator = MonsterProxies.erase(iterator);
		}
		else ++iterator;
	}
	if (brg_debug && (int(liveIds.size()) != LastLoggedMonsterCount || directCount != LastLoggedDirectMonsterCount))
	{
		Printf("Brogue monsters: synced %u live entities, %d directly visible.\n",
			unsigned(liveIds.size()), directCount);
		LastLoggedMonsterCount = int(liveIds.size());
		LastLoggedDirectMonsterCount = directCount;
	}
}

bool TickMonsterAnimations()
{
	bool active = false;
	for (auto iterator = MonsterProxies.begin(); iterator != MonsterProxies.end();)
	{
		MonsterProxy &proxy = iterator->second;
		if (proxy.actor == nullptr || (proxy.actor->ObjectFlags & OF_EuthanizeMe))
		{
			iterator = MonsterProxies.erase(iterator);
			continue;
		}
		if (proxy.moveTics > 0)
		{
			--proxy.moveTics;
			const double fraction = 1.0 - double(proxy.moveTics) / proxy.moveTotal;
			const DVector3 position = proxy.moveFrom + (proxy.moveTo - proxy.moveFrom) * fraction;
			proxy.actor->SetOrigin(position, false);
			active = active || proxy.moveTics > 0;
		}
		if (proxy.pulseTics > 0)
		{
			--proxy.pulseTics;
			const double scale = 1.0 + (proxy.pulseTics % 2 ? .12 : 0.0);
			proxy.actor->Scale.X = proxy.actor->Scale.Y = scale;
			active = active || proxy.pulseTics > 0;
		}
		else proxy.actor->Scale.X = proxy.actor->Scale.Y = 1.0;
		if (proxy.deathTics > 0)
		{
			--proxy.deathTics;
			proxy.actor->Scale.Y = (std::max)(.08, proxy.deathTics / 7.0);
			active = true;
			if (proxy.deathTics == 0)
			{
				proxy.actor->Destroy();
				iterator = MonsterProxies.erase(iterator);
				continue;
			}
		}
		++iterator;
	}
	return active;
}

bool MonsterAnimationsActive()
{
	for (const auto &entry : MonsterProxies)
		if (entry.second.moveTics > 0 || entry.second.pulseTics > 0 || entry.second.deathTics > 0) return true;
	return false;
}

void SyncItems()
{
	if (!Started || primaryLevel == nullptr) return;
	if (ItemProxyLevel != primaryLevel)
	{
		// Actors from the previous FLevelLocals have already been torn down by
		// GZDoom. Never dereference those stale pointers.
		ClearItemProxies(false);
		ItemProxyLevel = primaryLevel;
		LastLoggedItemCount = -1;
		LastLoggedVisibleItemCount = -1;
	}

	std::vector<uint64_t> liveIds;
	liveIds.reserve(State.itemCount);
	int visibleCount = 0;
	for (uint32_t index = 0; index < State.itemCount; ++index)
	{
		const BrogueBridgeItemState &item = State.items[index];
		if (item.carried || item.x < 0 || item.y < 0 || item.x >= State.width || item.y >= State.height)
			continue;

		liveIds.push_back(item.id);
		if (item.visible) ++visibleCount;
		const int visualKind = PickupVisualKind(item);
		ItemProxy *proxy = FindItemProxy(item.id);
		if (proxy != nullptr && (proxy->category != item.category || proxy->visualKind != visualKind
			|| proxy->x != item.x || proxy->y != item.y))
		{
			if (proxy->actor != nullptr && !(proxy->actor->ObjectFlags & OF_EuthanizeMe))
				proxy->actor->Destroy();
			proxy->actor = nullptr;
			proxy->spawnAttempted = false;
		}

		if (proxy == nullptr)
		{
			ItemProxies.push_back({item.id, item.category, visualKind, item.x, item.y, nullptr, false});
			proxy = &ItemProxies.back();
		}
		proxy->category = item.category;
		proxy->visualKind = visualKind;
		proxy->x = item.x;
		proxy->y = item.y;
		if (!proxy->spawnAttempted)
		{
			proxy->actor = SpawnItemProxy(item);
			proxy->spawnAttempted = true;
		}
		if (proxy->actor != nullptr)
		{
			if (item.visible) proxy->actor->renderflags &= ~RF_INVISIBLE;
			else proxy->actor->renderflags |= RF_INVISIBLE;
		}
	}

	for (size_t index = ItemProxies.size(); index-- > 0;)
	{
		const bool alive = std::find(liveIds.begin(), liveIds.end(), ItemProxies[index].id) != liveIds.end();
		if (!alive)
		{
			if (ItemProxies[index].actor != nullptr && !(ItemProxies[index].actor->ObjectFlags & OF_EuthanizeMe))
				ItemProxies[index].actor->Destroy();
			ItemProxies.erase(ItemProxies.begin() + index);
		}
	}

	const int floorItemCount = int(liveIds.size());
	if (brg_debug && (floorItemCount != LastLoggedItemCount || visibleCount != LastLoggedVisibleItemCount))
	{
		Printf("Brogue pickups: synced %d floor items, %d currently visible.\n",
			floorItemCount, visibleCount);
		LastLoggedItemCount = floorItemCount;
		LastLoggedVisibleItemCount = visibleCount;
	}
}

const BrogueBridgeCellState *FindStateCell(int x, int y)
{
	if (x < 0 || y < 0 || x >= State.width || y >= State.height) return nullptr;
	const uint32_t index = uint32_t(y * State.width + x);
	if (index >= State.cellCount) return nullptr;
	const BrogueBridgeCellState *cell = &State.cells[index];
	return cell->x == x && cell->y == y ? cell : nullptr;
}

CellFxKind CellEffectKind(const BrogueBridgeCellState &cell)
{
	if (cell.isFire) return CellFxKind::Fire;
	if (cell.isLava) return CellFxKind::Lava;
	if (cell.isGas) return CellFxKind::Gas;
	return CellFxKind::None;
}

const char *CellEffectClass(CellFxKind kind)
{
	switch (kind)
	{
	case CellFxKind::Lava: return "BrogueLavaFx";
	case CellFxKind::Fire: return "BrogueFireFx";
	case CellFxKind::Gas: return "BrogueGasFx";
	default: return nullptr;
	}
}

bool CellEffectSampled(const BrogueBridgeCellState &cell, CellFxKind kind, int quality)
{
	if (quality <= 0 || kind == CellFxKind::None) return false;
	if (kind == CellFxKind::Fire || kind == CellFxKind::Gas) return true;
	const int divisor = quality >= 2 ? 2 : 4;
	return ((cell.x * 17 + cell.y * 31) % divisor) == 0;
}

void SyncCellEffects()
{
	if (!Started || primaryLevel == nullptr) return;
	if (CellFxProxyLevel != primaryLevel)
	{
		CellFxProxies.clear();
		CellFxProxyLevel = primaryLevel;
	}

	for (auto &entry : CellFxProxies) entry.second.seen = false;
	const int quality = (std::max)(0, (std::min)(2, int(brg_fx_quality)));
	for (uint32_t index = 0; index < State.cellCount; ++index)
	{
		const BrogueBridgeCellState &cell = State.cells[index];
		const CellFxKind kind = CellEffectKind(cell);
		if (!CellEffectSampled(cell, kind, quality)) continue;

		const int key = cell.y * State.width + cell.x;
		CellFxProxy &proxy = CellFxProxies[key];
		proxy.x = cell.x;
		proxy.y = cell.y;
		proxy.seen = true;
		const bool actorAlive = proxy.actor != nullptr
			&& !(proxy.actor->ObjectFlags & OF_EuthanizeMe);
		if (proxy.kind != kind && actorAlive)
		{
			proxy.actor->Destroy();
			proxy.actor = nullptr;
		}
		proxy.kind = kind;
		if (proxy.actor == nullptr || (proxy.actor->ObjectFlags & OF_EuthanizeMe))
		{
			const char *className = CellEffectClass(kind);
			if (className == nullptr) continue;
			DVector3 position = BrogueCellToWorld(cell.x, cell.y);
			position.Z += 1.0;
			proxy.actor = Spawn(primaryLevel, className, position, NO_REPLACE);
		}
	}

	for (auto iterator = CellFxProxies.begin(); iterator != CellFxProxies.end();)
	{
		CellFxProxy &proxy = iterator->second;
		if (proxy.seen)
		{
			++iterator;
			continue;
		}
		if (proxy.actor != nullptr && !(proxy.actor->ObjectFlags & OF_EuthanizeMe))
			proxy.actor->Destroy();
		iterator = CellFxProxies.erase(iterator);
	}
	if (brg_debug && LastLoggedCellFxCount != int(CellFxProxies.size()))
	{
		LastLoggedCellFxCount = int(CellFxProxies.size());
		Printf("Brogue bridge: synchronized %d authoritative ambient effect cells (quality=%d).\n",
			LastLoggedCellFxCount, quality);
	}
}

void SpawnTransientEffect(const char *className, int x, int y, double zOffset)
{
	if (primaryLevel == nullptr || int(brg_fx_quality) <= 0) return;
	if (x < 0 || y < 0 || x >= State.width || y >= State.height) return;
	DVector3 position = BrogueCellToWorld(x, y);
	position.Z += zOffset;
	Spawn(primaryLevel, className, position, NO_REPLACE);
}

void SpawnBridgeEventEffects(const BrogueBridgeTurnResult &result)
{
	for (uint32_t index = 0; index < result.eventCount; ++index)
	{
		const BrogueBridgeEvent &event = result.events[index];
		const BrogueBridgeCellState *cell = FindStateCell(event.x, event.y);
		if (event.type == BROGUE_EVENT_PLAYER_MOVED
			|| event.type == BROGUE_EVENT_CREATURE_MOVED)
		{
			if (cell != nullptr && cell->isLiquid && !cell->isLava)
				SpawnTransientEffect("BrogueWaterSplashFx", event.x, event.y, 2.0);
		}
		else if (event.type == BROGUE_EVENT_PROJECTILE_IMPACT)
		{
			SpawnTransientEffect("BrogueImpactFx", event.x, event.y, 24.0);
		}
		else if (event.type == BROGUE_EVENT_ENTITY_DAMAGED
			&& cell != nullptr && cell->currentlyVisible)
		{
			SpawnTransientEffect("BrogueDamageFx", event.x, event.y, 24.0);
		}
		else if (event.type == BROGUE_EVENT_ENTITY_DIED
			&& cell != nullptr && cell->currentlyVisible)
		{
			SpawnTransientEffect("BrogueDeathFx", event.x, event.y, 18.0);
		}
	}
}

void SyncDoorMarkers()
{
	if (primaryLevel == nullptr) return;
	PClassActor *type = PClass::FindActor("BrogueDoorMarker");
	if (type == nullptr)
	{
		Printf("Brogue bridge: BrogueDoorMarker presentation class is missing.\n");
		return;
	}

	if (DoorProxyLevel != primaryLevel)
	{
		DoorProxies.clear();
		auto iterator = primaryLevel->GetThinkerIterator<AActor>();
		while (AActor *actor = iterator.Next())
		{
			if (!actor->IsA(type)) continue;
			DoorProxy proxy;
			proxy.x = actor->args[0];
			proxy.y = actor->args[1];
			proxy.yaw = actor->Angles.Yaw.Degrees();
			proxy.presentationType = actor->GetClass();
			proxy.actor = actor;
			DoorProxies.push_back(proxy);
		}
		DoorProxyLevel = primaryLevel;
		if (brg_debug) Printf("Brogue bridge: registered %zu coordinate-bound door panels.\n", DoorProxies.size());
	}

	for (DoorProxy &proxy : DoorProxies)
	{
		const BrogueBridgeCellState *cell = FindStateCell(proxy.x, proxy.y);
		if (cell == nullptr)
		{
			if (proxy.actor != nullptr && !(proxy.actor->ObjectFlags & OF_EuthanizeMe))
				proxy.actor->Destroy();
			proxy.actor = nullptr;
			Printf("Brogue bridge: door marker references invalid cell %d,%d.\n", proxy.x, proxy.y);
			continue;
		}

		// Brogue doors and barricades do not share one obstruction flag. A
		// closed door blocks sight but permits its move-to-open interaction;
		// a wooden barricade blocks movement while deliberately allowing sight.
		// Either obstruction means that the authoritative doorway presentation
		// remains closed. OPEN_DOOR has neither flag and removes the marker.
		const bool closed = cell->isDoor && (cell->isSolid || cell->blocksVision);
		const bool actorAlive = proxy.actor != nullptr
			&& !(proxy.actor->ObjectFlags & OF_EuthanizeMe);
		if (!closed)
		{
			// Destruction is intentional: a Brogue OPEN_DOOR has no panel. This
			// avoids depending on model alpha/render flags for authoritative state.
			if (actorAlive) proxy.actor->Destroy();
			proxy.actor = nullptr;
			continue;
		}

		DVector3 position = BrogueCellToWorld(proxy.x, proxy.y);
		if (!actorAlive)
		{
			PClassActor *spawnType = proxy.presentationType != nullptr
				? proxy.presentationType : type;
			proxy.actor = Spawn(primaryLevel, spawnType, position, NO_REPLACE);
			if (proxy.actor == nullptr)
			{
				Printf("Brogue bridge: could not respawn closed door panel at %d,%d.\n",
					proxy.x, proxy.y);
				continue;
			}
			proxy.actor->args[0] = proxy.x;
			proxy.actor->args[1] = proxy.y;
			proxy.actor->Angles.Yaw = DAngle::fromDeg(proxy.yaw);
		}
		proxy.actor->Alpha = 1.0;
		proxy.actor->renderflags &= ~RF_INVISIBLE;
		proxy.actor->SetOrigin(position, false);
	}
}

void SyncTerrainEvents(const BrogueBridgeTurnResult &result)
{
	if (primaryLevel == nullptr) return;

	for (uint32_t index = 0; index < result.eventCount; ++index)
	{
		const BrogueBridgeEvent &event = result.events[index];
		if (event.type != BROGUE_EVENT_CELL_TERRAIN_CHANGED) continue;

		const BrogueBridgeCellState *cell = FindStateCell(event.x, event.y);
		if (cell == nullptr)
		{
			Printf("Brogue bridge: terrain event references invalid cell %d,%d.\n", event.x, event.y);
			continue;
		}

		if (brg_debug)
			Printf("Brogue terrain cell=%d,%d door=%s blocksVision=%s revision=%llu.\n",
				event.x, event.y, cell->isDoor ? "true" : "false",
				cell->blocksVision ? "true" : "false",
				(unsigned long long)State.revision);
	}
	// The caller refreshes all markers from the post-action snapshot. Do not
	// depend on a terrain event surviving a bounded/truncated event stream.
}

void SyncFallShaftMarker()
{
	if (!PendingFallShaft || primaryLevel == nullptr
		|| primaryLevel->levelnum != State.depth) return;
	if (PendingFallLandingX < 0 || PendingFallLandingY < 0
		|| PendingFallLandingX >= State.width || PendingFallLandingY >= State.height)
	{
		Printf("Brogue bridge: fall shaft has invalid landing cell %d,%d.\n",
			PendingFallLandingX, PendingFallLandingY);
		PendingFallShaft = false;
		return;
	}

	PClassActor *type = PClass::FindActor("BrogueFallShaftMarker");
	if (type == nullptr)
	{
		Printf("Brogue bridge: BrogueFallShaftMarker presentation class is missing.\n");
		PendingFallShaft = false;
		return;
	}

	DVector3 position = BrogueCellToWorld(PendingFallLandingX, PendingFallLandingY);
	sector_t *sector = primaryLevel->PointInSector(position.X, position.Y);
	if (sector == nullptr)
	{
		Printf("Brogue bridge: no destination sector for fall shaft at %d,%d.\n",
			PendingFallLandingX, PendingFallLandingY);
		PendingFallShaft = false;
		return;
	}
	// The model is 40 units tall. Recess its dark cap one unit below the real
	// ceiling to avoid z-fighting while preserving the map's physical ceiling.
	const double ceilingZ = sector->ceilingplane.ZatPoint(position.X, position.Y);
	position.Z = ceilingZ - 41.0;
	FallShaftMarker = Spawn(primaryLevel, type, position, NO_REPLACE);
	FallShaftLevel = primaryLevel;
	if (FallShaftMarker == nullptr)
		Printf("Brogue bridge: could not spawn fall shaft at %d,%d.\n",
			PendingFallLandingX, PendingFallLandingY);
	else if (brg_debug)
		Printf("Brogue bridge: fall shaft landing=%d,%d ceiling=%.1f.\n",
			PendingFallLandingX, PendingFallLandingY, ceilingZ);
	PendingFallShaft = false;
}

void ClearProjectile()
{
	if (Projectile.actor != nullptr && !(Projectile.actor->ObjectFlags & OF_EuthanizeMe))
		Projectile.actor->Destroy();
	Projectile = {};
}

// Drop every raw pointer owned by the current FLevelLocals before GZDoom tears
// that level down. GZDoom owns these actors and destroys them as part of the
// map change. Keeping a pointer until the next level (or engine shutdown) is a
// use-after-free: the old actor's storage can still be readable even though
// its virtual table has already been cleared.
void DetachLevelPresentation()
{
	ItemProxies.clear();
	MonsterProxies.clear();
	DoorProxies.clear();
	CellFxProxies.clear();
	FallShaftMarker = nullptr;
	FallShaftLevel = nullptr;
	Projectile = {};
	TargetMarker = nullptr;
	PathMarkers.clear();
	ItemProxyLevel = nullptr;
	MonsterProxyLevel = nullptr;
	DoorProxyLevel = nullptr;
	CellFxProxyLevel = nullptr;
	LastLoggedCellFxCount = -1;
	LastLoggedItemCount = -1;
	LastLoggedVisibleItemCount = -1;
	LastLoggedMonsterCount = -1;
	LastLoggedDirectMonsterCount = -1;
	HasBufferedAction = false;
	BufferedAction = BROGUE_ACTION_WAIT;
	WeaponUi = WeaponUiMode::None;
	ThrowItemId = 0;
	LookResult = {};
	LastVisualWeaponId = 0;
	InventoryOpen = false;
	ApplyUi = ApplyUiMode::None;
	ApplyItemId = 0;
	ApplyChoiceIds.clear();
	CommandConfirmationOpen = false;
	CommandConfirmationCommand = {};
	CommandConfirmationPrompt = "";
	CommandConfirmationSource = "";
}

void BeginProjectileAnimation(const BrogueBridgeTurnResult &result)
{
	std::vector<DVector3> points;
	const BrogueBridgeEvent *first = nullptr;
	for (uint32_t index = 0; index < result.eventCount; ++index)
	{
		const BrogueBridgeEvent &event = result.events[index];
		if (event.type != BROGUE_EVENT_PROJECTILE_MOVED) continue;
		if (first == nullptr)
		{
			first = &event;
			points.push_back(BrogueCellToWorld(event.fromX, event.fromY) + DVector3(0, 0, 28));
		}
		points.push_back(BrogueCellToWorld(event.toX, event.toY) + DVector3(0, 0, 28));
	}
	if (first == nullptr || points.size() < 2) return;

	ClearProjectile();
	FString className;
	className.Format("BroguePickupC%04dK%02d", first->itemCategory, (std::max)(0, first->itemKind));
	Projectile.actor = Spawn(primaryLevel, className.GetChars(), points.front(), NO_REPLACE);
	if (Projectile.actor == nullptr)
		Projectile.actor = Spawn(primaryLevel, "BrogueWeaponTargetMarker", points.front(), NO_REPLACE);
	Projectile.points = std::move(points);
	Projectile.point = 1;
	Projectile.tics = 2;
	PlayWeaponState(FName("BridgeThrow"));
}

bool TickProjectile()
{
	if (Projectile.actor == nullptr || Projectile.point >= Projectile.points.size()) return false;
	const DVector3 from = Projectile.actor->Pos();
	const DVector3 to = Projectile.points[Projectile.point];
	Projectile.actor->SetOrigin(from + (to - from) * 0.5, false);
	if (--Projectile.tics <= 0)
	{
		Projectile.actor->SetOrigin(to, false);
		++Projectile.point;
		Projectile.tics = 2;
		if (Projectile.point >= Projectile.points.size())
		{
			ClearProjectile();
			return false;
		}
	}
	return true;
}

void ProcessWeaponEvents(const BrogueBridgeTurnResult &result)
{
	for (uint32_t index = 0; index < result.eventCount; ++index)
	{
		const BrogueBridgeEvent &event = result.events[index];
		if (event.type == BROGUE_EVENT_ATTACK_ATTEMPTED && event.sourceEntityId == 1)
			PlayWeaponState(FName("BridgeAttack"));
	}
	BeginProjectileAnimation(result);
	SyncWeaponView();
}

bool SyncLevelEvent(const BrogueBridgeTurnResult &result)
{
	for (uint32_t index = 0; index < result.eventCount; ++index)
	{
		const BrogueBridgeEvent &event = result.events[index];
		if (event.type != BROGUE_EVENT_LEVEL_CHANGE_REQUESTED)
			continue;

		PendingFallShaft = (event.eventFlags & BROGUE_EVENT_FLAG_LEVEL_FALL) != 0;
		PendingFallLandingX = event.toX;
		PendingFallLandingY = event.toY;

		FString destination;
		destination.Format("BRG%02d", State.depth);
		if (brg_debug) Printf("Brogue bridge: authoritative level change to %s.\n", destination.GetChars());
		DetachLevelPresentation();
		primaryLevel->ChangeLevel(destination.GetChars(), 0, 16 /* CHANGELEVEL_NOINTERMISSION */);
		return true;
	}
	return false;
}

bool EnsureStarted()
{
	if (!IsBrogueMap()) return false;
	if (Started) return true;
	if (!LoadBridge()) return false;

	BrogueBridgeResult result = Api.initialize();
	if (result != BROGUE_BRIDGE_OK)
	{
		Printf("Brogue bridge: initialize failed: %s.\n", Api.resultName(result));
		return false;
	}

	const uint64_t seed = uint64_t((std::max)(1, int(brg_seed)));
	result = Api.startGame(seed);
	BrogueBridgeResult stateResult = Api.getState(&State);
	if (result != BROGUE_BRIDGE_OK || stateResult != BROGUE_BRIDGE_OK)
	{
		Printf("Brogue bridge: start failed: %s.\n",
			Api.resultName(result != BROGUE_BRIDGE_OK ? result : stateResult));
		Api.shutdown();
		return false;
	}
	if (State.apiVersion != BROGUE_BRIDGE_API_VERSION)
	{
		Printf("Brogue bridge: API mismatch (engine=%d, DLL=%d). Rebuild both bridge components.\n",
			BROGUE_BRIDGE_API_VERSION, State.apiVersion);
		Api.shutdown();
		return false;
	}

	Started = true;
	Api.getMonsterCatalog(&MonsterCatalog);
	if (brg_debug)
		Printf("Brogue bridge: attached seed=%llu depth=%d levelSeed=%llu player=%d,%d.\n",
			(unsigned long long)State.gameSeed, State.depth,
			(unsigned long long)State.levelSeed, State.player.x, State.player.y);
	SyncPlayer();
	SyncDoorMarkers();
	SyncCellEffects();
	SyncItems();
	SyncMonsters();
	SyncWeaponView();
	return true;
}

BrogueBridgeResult PerformCommandResult(BrogueBridgeCommand command, const char *source,
	BrogueBridgeTurnResult &result, bool reportFailure)
{
	if (!EnsureStarted()) return BROGUE_BRIDGE_GAME_NOT_STARTED;
	if (command.expectedRevision == 0) command.expectedRevision = State.revision;

	result = {};
	BrogueBridgeResult bridgeResult = Api.performCommand(&command, &result);
	if (bridgeResult != BROGUE_BRIDGE_OK)
	{
		if (reportFailure)
			Printf("Brogue bridge: %s command failed: %s.\n", source, Api.resultName(bridgeResult));
		return bridgeResult;
	}

	if (Api.getState(&State) != BROGUE_BRIDGE_OK) return BROGUE_BRIDGE_INVALID_STATE;
	if (brg_debug)
	{
		Printf("Brogue command=%d action=%d item=%llu source=%s accepted=%s turn=%llu revision=%llu player=%d,%d hash=%016llx\n",
			int(command.type), int(command.action), (unsigned long long)command.itemId,
			source, result.actionAccepted ? "true" : "false",
			(unsigned long long)State.absoluteTurn,
			(unsigned long long)State.revision,
			State.player.x, State.player.y,
			(unsigned long long)State.stateHash);
	}
	// Once Brogue has changed depth, State describes the destination floor but
	// primaryLevel still describes the source floor until GZDoom applies the
	// queued map change. Do not project destination terrain into the old map.
	if (SyncLevelEvent(result)) return BROGUE_BRIDGE_OK;

	SyncTerrainEvents(result);
	SyncDoorMarkers();
	SyncCellEffects();
	SpawnBridgeEventEffects(result);
	SyncPlayer();
	SyncItems();
	SyncMonsters(&result);
	ProcessWeaponEvents(result);
	return BROGUE_BRIDGE_OK;
}

bool PerformCommand(BrogueBridgeCommand command, const char *source)
{
	BrogueBridgeTurnResult result{};
	return PerformCommandResult(command, source, result, true) == BROGUE_BRIDGE_OK;
}

void ClearCommandConfirmation()
{
	CommandConfirmationOpen = false;
	CommandConfirmationCommand = {};
	CommandConfirmationPrompt = "";
	CommandConfirmationSource = "";
}

bool SubmitConfirmableCommand(BrogueBridgeCommand command, const char *source)
{
	BrogueBridgeTurnResult result{};
	const BrogueBridgeResult bridgeResult = PerformCommandResult(command, source, result, false);
	if (bridgeResult == BROGUE_BRIDGE_CONFIRMATION_REQUIRED)
	{
		CommandConfirmationOpen = true;
		CommandConfirmationCommand = command;
		CommandConfirmationPrompt = result.prompt;
		CommandConfirmationSource = source;
		return true;
	}
	if (bridgeResult != BROGUE_BRIDGE_OK)
	{
		Printf("Brogue bridge: %s command failed: %s.\n", source, Api.resultName(bridgeResult));
		return false;
	}
	ClearCommandConfirmation();
	return true;
}

bool PerformAction(BrogueBridgeAction action, const char *source)
{
	BrogueBridgeCommand command{};
	command.apiVersion = BROGUE_BRIDGE_API_VERSION;
	command.type = BROGUE_COMMAND_ACTION;
	command.action = action;
	command.expectedRevision = State.revision;
	return SubmitConfirmableCommand(command, source);
}

bool PerformItemCommand(BrogueBridgeCommandType type, uint64_t itemId, int targetX = 0, int targetY = 0)
{
	BrogueBridgeCommand command{};
	command.apiVersion = BROGUE_BRIDGE_API_VERSION;
	command.type = type;
	command.action = BROGUE_ACTION_WAIT;
	command.expectedRevision = State.revision;
	command.itemId = itemId;
	command.targetX = targetX;
	command.targetY = targetY;
	command.confirmed = 1;
	return PerformCommand(command, "weapon-ui");
}

std::vector<uint32_t> CarriedInventoryIndices()
{
	std::vector<uint32_t> result;
	for (uint32_t index = 0; index < State.itemCount; ++index)
		if (State.items[index].carried) result.push_back(index);
	std::sort(result.begin(), result.end(), [](uint32_t left, uint32_t right)
	{
		const BrogueBridgeItemState &a = State.items[left];
		const BrogueBridgeItemState &b = State.items[right];
		if (a.inventoryOrder != b.inventoryOrder) return a.inventoryOrder < b.inventoryOrder;
		return a.inventoryLetter < b.inventoryLetter;
	});
	return result;
}

void CloseInventory()
{
	InventoryOpen = false;
	InventorySelection = 0;
	ApplyUi = ApplyUiMode::None;
	ApplyItemId = 0;
	ApplyChoiceIds.clear();
	ApplyChoiceSelection = 0;
	ApplyPrompt = "";
	ClearCommandConfirmation();
}

void SetApplyPrompt(const BrogueBridgeTurnResult &result, ApplyUiMode mode)
{
	ApplyUi = mode;
	ApplyPrompt = result.prompt;
	ApplyChoiceIds.assign(result.choiceItemIds, result.choiceItemIds + result.choiceCount);
	ApplyChoiceSelection = 0;
}

bool SubmitApply(uint64_t itemId, uint64_t secondaryItemId, bool confirmed)
{
	BrogueBridgeCommand command{};
	command.apiVersion = BROGUE_BRIDGE_API_VERSION;
	command.type = BROGUE_COMMAND_APPLY_ITEM;
	command.action = BROGUE_ACTION_WAIT;
	command.expectedRevision = State.revision;
	command.itemId = itemId;
	command.secondaryItemId = secondaryItemId;
	command.confirmed = confirmed ? 1 : 0;
	BrogueBridgeTurnResult result{};
	const BrogueBridgeResult bridgeResult = PerformCommandResult(command, "inventory-apply", result, false);
	if (bridgeResult == BROGUE_BRIDGE_CONFIRMATION_REQUIRED)
	{
		ApplyItemId = itemId;
		SetApplyPrompt(result, ApplyUiMode::Confirm);
		return true;
	}
	if (bridgeResult == BROGUE_BRIDGE_SELECTION_REQUIRED)
	{
		ApplyItemId = itemId;
		SetApplyPrompt(result, ApplyUiMode::SelectItem);
		return true;
	}
	if (bridgeResult != BROGUE_BRIDGE_OK)
	{
		Printf("Brogue bridge: inventory apply failed: %s.\n", Api.resultName(bridgeResult));
		return false;
	}
	ApplyUi = ApplyUiMode::None;
	ApplyItemId = 0;
	ApplyChoiceIds.clear();
	return true;
}

bool HandleInventoryInput(const event_t *event)
{
	const int key = event->data1;
	if (key == 0x17) // I
	{
		if (event->type == EV_KeyDown)
		{
			// Brogue does not permit cancelling the mandatory identify/enchant
			// choice after a scroll has been read. Keep that contract here even
			// though the bridge performs the choice as an atomic command.
			if (ApplyUi == ApplyUiMode::SelectItem) return true;
			if (WeaponUi != WeaponUiMode::None) CloseWeaponUi();
			if (InventoryOpen) CloseInventory();
			else { InventoryOpen = true; InventorySelection = 0; }
		}
		return true;
	}
	if (!InventoryOpen) return false;
	if (event->type == EV_KeyUp) return true;
	if (event->type != EV_KeyDown) return true;
	if (ApplyUi == ApplyUiMode::Confirm)
	{
		if (key == KEY_ENTER || event->data2 == 'y' || event->data2 == 'Y')
			SubmitApply(ApplyItemId, 0, true);
		else if (key == KEY_ESCAPE || key == KEY_MOUSE2 || event->data2 == 'n' || event->data2 == 'N')
		{
			ApplyUi = ApplyUiMode::None;
			ApplyItemId = 0;
		}
		return true;
	}
	if (ApplyUi == ApplyUiMode::SelectItem)
	{
		if (ApplyChoiceIds.empty()) return true;
		if (key == 0xc8 || key == KEY_MWHEELUP) --ApplyChoiceSelection;
		else if (key == 0xd0 || key == KEY_MWHEELDOWN) ++ApplyChoiceSelection;
		else
		{
			for (size_t index = 0; index < ApplyChoiceIds.size(); ++index)
			{
				const BrogueBridgeItemState *choice = FindItem(ApplyChoiceIds[index]);
				if (choice != nullptr && choice->inventoryLetter != 0
					&& event->data2 == choice->inventoryLetter)
					ApplyChoiceSelection = int(index);
			}
		}
		ApplyChoiceSelection = (ApplyChoiceSelection % int(ApplyChoiceIds.size())
			+ int(ApplyChoiceIds.size())) % int(ApplyChoiceIds.size());
		if (key == KEY_ENTER || key == 0x16) // Enter or U: apply to selection
			SubmitApply(ApplyItemId, ApplyChoiceIds[ApplyChoiceSelection], true);
		return true;
	}
	const std::vector<uint32_t> inventory = CarriedInventoryIndices();
	if (inventory.empty())
	{
		if (key == KEY_ESCAPE || key == KEY_ENTER) CloseInventory();
		return true;
	}
	if (key == KEY_ESCAPE || key == KEY_MOUSE2) { CloseInventory(); return true; }
	if (key == 0xc8 || key == KEY_MWHEELUP) --InventorySelection;
	else if (key == 0xd0 || key == KEY_MWHEELDOWN) ++InventorySelection;
	else
	{
		for (size_t index = 0; index < inventory.size(); ++index)
		{
			const int letter = State.items[inventory[index]].inventoryLetter;
			if (letter != 0 && event->data2 == letter) { InventorySelection = int(index); break; }
		}
	}
	InventorySelection = (InventorySelection % int(inventory.size()) + int(inventory.size())) % int(inventory.size());
	const BrogueBridgeItemState &item = State.items[inventory[InventorySelection]];
	if ((key == KEY_ENTER || key == 0x16) && (item.actionFlags & BROGUE_ITEM_ACTION_APPLY)) // Enter or U: use
		SubmitApply(item.id, 0, false);
	else if (key == KEY_ENTER || key == 0x12) // Enter or E: equip/remove
	{
		if (item.actionFlags & BROGUE_ITEM_ACTION_UNEQUIP)
			PerformItemCommand(BROGUE_COMMAND_UNEQUIP_ITEM, item.id);
		else if (item.actionFlags & BROGUE_ITEM_ACTION_EQUIP)
			PerformItemCommand(BROGUE_COMMAND_EQUIP_ITEM, item.id);
	}
	else if (key == 0x20 && (item.actionFlags & BROGUE_ITEM_ACTION_DROP)) // D
		PerformItemCommand(BROGUE_COMMAND_DROP_ITEM, item.id);
	else if (key == 0x14 && (item.actionFlags & BROGUE_ITEM_ACTION_THROW)) // T
	{
		const uint64_t id = item.id;
		CloseInventory();
		BeginTargeting(id);
		RefreshTargeting();
	}
	return true;
}

void PerformQueuedWait()
{
	if (!PendingWait || !EnsureStarted()) return;

	PendingWait = false;
	PerformAction(BROGUE_ACTION_WAIT, "brg_wait");
}

bool ParseActionName(const char *name, BrogueBridgeAction &action)
{
	if (name == nullptr) return false;
	struct NamedAction { const char *name; BrogueBridgeAction action; };
	static const NamedAction names[] = {
		{"N", BROGUE_ACTION_MOVE_N}, {"NE", BROGUE_ACTION_MOVE_NE},
		{"E", BROGUE_ACTION_MOVE_E}, {"SE", BROGUE_ACTION_MOVE_SE},
		{"S", BROGUE_ACTION_MOVE_S}, {"SW", BROGUE_ACTION_MOVE_SW},
		{"W", BROGUE_ACTION_MOVE_W}, {"NW", BROGUE_ACTION_MOVE_NW},
		{"WAIT", BROGUE_ACTION_WAIT},
	};
	for (const NamedAction &candidate : names)
	{
		if (_stricmp(name, candidate.name) == 0)
		{
			action = candidate.action;
			return true;
		}
	}
	return false;
}

int FacingOctant()
{
	AActor *camera = players[consoleplayer].camera != nullptr
		? players[consoleplayer].camera
		: players[consoleplayer].mo;
	if (camera == nullptr) return -1;

	double yaw = camera->Angles.Yaw.Degrees();
	while (yaw < 0.0) yaw += 360.0;
	while (yaw >= 360.0) yaw -= 360.0;
	return int((yaw + 22.5) / 45.0) % 8;
}

// GZDoom yaw 0 points along world +X. The generated map uses +X for Brogue
// east and +Y for Brogue north, so this table converts a quantized view yaw
// into the corresponding Brogue intent.
const BrogueBridgeAction FacingActions[8] = {
	BROGUE_ACTION_MOVE_E,
	BROGUE_ACTION_MOVE_NE,
	BROGUE_ACTION_MOVE_N,
	BROGUE_ACTION_MOVE_NW,
	BROGUE_ACTION_MOVE_W,
	BROGUE_ACTION_MOVE_SW,
	BROGUE_ACTION_MOVE_S,
	BROGUE_ACTION_MOVE_SE,
};

#ifdef _WIN32
struct ComparisonKey
{
	int virtualKey;
	int scanCode;
	BrogueBridgeAction action;
};

const ComparisonKey ComparisonKeys[9] = {
	{VK_NUMPAD8, 0x48, BROGUE_ACTION_MOVE_N},
	{VK_NUMPAD9, 0x49, BROGUE_ACTION_MOVE_NE},
	{VK_NUMPAD6, 0x4d, BROGUE_ACTION_MOVE_E},
	{VK_NUMPAD3, 0x51, BROGUE_ACTION_MOVE_SE},
	{VK_NUMPAD2, 0x50, BROGUE_ACTION_MOVE_S},
	{VK_NUMPAD1, 0x4f, BROGUE_ACTION_MOVE_SW},
	{VK_NUMPAD4, 0x4b, BROGUE_ACTION_MOVE_W},
	{VK_NUMPAD7, 0x47, BROGUE_ACTION_MOVE_NW},
	{VK_NUMPAD5, 0x4c, BROGUE_ACTION_WAIT},
};

BOOL CALLBACK FindComparisonWindow(HWND window, LPARAM parameter)
{
	DWORD processId = 0;
	GetWindowThreadProcessId(window, &processId);
	if (processId == DWORD(brg_compare_pid) && IsWindowVisible(window)
		&& GetWindow(window, GW_OWNER) == nullptr)
	{
		ComparisonWindow = window;
		return FALSE;
	}
	return TRUE;
}

HWND GetComparisonWindow()
{
	if (brg_compare_pid <= 0) return nullptr;
	DWORD processId = 0;
	if (ComparisonWindow != nullptr)
		GetWindowThreadProcessId(ComparisonWindow, &processId);
	if (ComparisonWindow == nullptr || !IsWindow(ComparisonWindow)
		|| processId != DWORD(brg_compare_pid))
	{
		ComparisonWindow = nullptr;
		EnumWindows(FindComparisonWindow, 0);
	}
	return ComparisonWindow;
}

bool IsComparisonScanCode(int scanCode)
{
	for (const ComparisonKey &key : ComparisonKeys)
		if (key.scanCode == scanCode) return true;
	return false;
}

void DeliverComparisonKey(const ComparisonKey &key)
{
	HWND window = GetComparisonWindow();
	if (window == nullptr) return;
	// If Brogue already owns keyboard focus, its SDL input loop receives the
	// physical numpad event. Posting it again would advance Brogue twice.
	if (GetForegroundWindow() == window) return;
	SetForegroundWindow(window);
	const UINT scan = MapVirtualKeyW(UINT(key.virtualKey), MAPVK_VK_TO_VSC);
	const LPARAM down = LPARAM(1 | (scan << 16));
	const LPARAM up = down | LPARAM(1u << 30) | LPARAM(1u << 31);
	PostMessageW(window, WM_KEYDOWN, WPARAM(key.virtualKey), down);
	PostMessageW(window, WM_KEYUP, WPARAM(key.virtualKey), up);
}

void PollComparisonInput()
{
	if (brg_compare_pid <= 0 || GetComparisonWindow() == nullptr) return;
	for (size_t index = 0; index < std::size(ComparisonKeys); ++index)
	{
		const bool down = (GetAsyncKeyState(ComparisonKeys[index].virtualKey) & 0x8000) != 0;
		if (down && !ComparisonKeysDown[index])
		{
			DeliverComparisonKey(ComparisonKeys[index]);
			PerformAction(ComparisonKeys[index].action, "comparison-numpad");
		}
		ComparisonKeysDown[index] = down;
	}
}
#else
bool IsComparisonScanCode(int) { return false; }
void PollComparisonInput() {}
#endif

bool MapFacingRelativeKeyToAction(int key, BrogueBridgeAction &action)
{
	const int facing = FacingOctant();
	if (facing < 0) return false;

	int offset;
	switch (key)
	{
	case 0x11: offset = 0; break; // W: forward
	case 0x1f: offset = 4; break; // S: backward
	case 0x1e: offset = 2; break; // A: strafe left
	case 0x20: offset = 6; break; // D: strafe right
	case 0x12: offset = 7; break; // E: forward-right, retained as a diagonal convenience
	default: return false;
	}

	action = FacingActions[(facing + offset) % 8];
	return true;
}

bool MapKeyToAction(int key, BrogueBridgeAction &action)
{
	// DirectInput scan codes are used by GZDoom's event_t on Windows. Normal
	// play uses camera-relative WASD, cardinal arrows, and Space to wait. The
	// numpad remains reserved for the explicit side-by-side comparison mode.
	switch (key)
	{
	case KEY_SPACE: action = BROGUE_ACTION_WAIT; return true;
	case 0xc8: action = BROGUE_ACTION_MOVE_N; return true;
	case 0xcd: action = BROGUE_ACTION_MOVE_E; return true;
	case 0xd0: action = BROGUE_ACTION_MOVE_S; return true;
	case 0xcb: action = BROGUE_ACTION_MOVE_W; return true;
	default: return MapFacingRelativeKeyToAction(key, action);
	}
}

void ClearTargetMarkers()
{
	if (TargetMarker != nullptr && !(TargetMarker->ObjectFlags & OF_EuthanizeMe)) TargetMarker->Destroy();
	TargetMarker = nullptr;
	for (AActor *actor : PathMarkers)
		if (actor != nullptr && !(actor->ObjectFlags & OF_EuthanizeMe)) actor->Destroy();
	PathMarkers.clear();
}

void CloseWeaponUi()
{
	WeaponUi = WeaponUiMode::None;
	ThrowItemId = 0;
	LookResult = {};
	LastVisualWeaponId = 0;
	ClearTargetMarkers();
	C_MidPrint(nullptr, nullptr);
}

void ShowWeaponSelector(bool throwing)
{
	const std::vector<uint32_t> weapons = CarriedWeaponIndices();
	const int count = int(weapons.size()) + (throwing ? 0 : 1);
	if (count <= 0)
	{
		C_MidPrint(nullptr, throwing ? "No throwable weapons." : "Empty hands");
		return;
	}
	WeaponSelection = (WeaponSelection % count + count) % count;
	C_MidPrint(nullptr, nullptr);
}

void BeginTargeting(uint64_t itemId)
{
	ThrowItemId = itemId;
	WeaponUi = WeaponUiMode::ThrowTarget;
	const int facing = FacingOctant() < 0 ? 0 : FacingOctant();
	static const int dx[8] = {1, 1, 0, -1, -1, -1, 0, 1};
	static const int dy[8] = {0, -1, -1, -1, 0, 1, 1, 1};
	TargetX = (std::clamp)(State.player.x + dx[facing] * 5, 0, State.width - 1);
	TargetY = (std::clamp)(State.player.y + dy[facing] * 5, 0, State.height - 1);
}

void RefreshTargeting()
{
	if (WeaponUi != WeaponUiMode::ThrowTarget || Api.previewThrow == nullptr) return;
	BrogueBridgeThrowPreview preview{};
	const BrogueBridgeResult result = Api.previewThrow(ThrowItemId, TargetX, TargetY, &preview);
	ClearTargetMarkers();
	if (primaryLevel != nullptr)
	{
		TargetMarker = Spawn(primaryLevel, "BrogueWeaponTargetMarker",
			BrogueCellToWorld(TargetX, TargetY) + DVector3(0, 0, 4), NO_REPLACE);
		if (result == BROGUE_BRIDGE_OK)
		{
			for (uint32_t index = 0; index < preview.pathCount; ++index)
			{
				AActor *marker = Spawn(primaryLevel, "BrogueWeaponPathMarker",
					BrogueCellToWorld(preview.path[index].x, preview.path[index].y) + DVector3(0, 0, 3), NO_REPLACE);
				if (marker != nullptr) PathMarkers.push_back(marker);
			}
		}
	}
	const BrogueBridgeItemState *item = FindItem(ThrowItemId);
	FString text;
	text.Format("THROW %s -> %d,%d\n%s\nMove cursor, Tab target, click/Enter throw, Esc cancel",
		item != nullptr ? item->displayName : "item", TargetX, TargetY,
		result == BROGUE_BRIDGE_OK && preview.valid ? "Valid trajectory" : preview.message);
	C_MidPrint(nullptr, text.GetChars());
}

void CycleVisibleTarget()
{
	std::vector<const BrogueBridgeCreatureState *> visible;
	for (uint32_t index = 0; index < State.creatureCount; ++index)
		if (State.creatures[index].alive && State.creatures[index].visibility == BROGUE_VISIBILITY_DIRECT)
			visible.push_back(&State.creatures[index]);
	if (visible.empty()) return;
	auto found = std::find_if(visible.begin(), visible.end(), [](const BrogueBridgeCreatureState *creature)
		{ return creature->x == TargetX && creature->y == TargetY; });
	if (found == visible.end() || ++found == visible.end()) found = visible.begin();
	TargetX = (*found)->x;
	TargetY = (*found)->y;
}

void RefreshLook()
{
	if (WeaponUi != WeaponUiMode::Look || Api.inspectCell == nullptr) return;
	LookResult = {};
	Api.inspectCell(TargetX, TargetY, &LookResult);
	ClearTargetMarkers();
	if (primaryLevel != nullptr)
		TargetMarker = Spawn(primaryLevel, "BrogueWeaponTargetMarker",
			BrogueCellToWorld(TargetX, TargetY) + DVector3(0, 0, 4), NO_REPLACE);
}

void CycleLookTarget()
{
	struct LookPoint { int x; int y; };
	std::vector<LookPoint> points;
	for (uint32_t index = 0; index < State.creatureCount; ++index)
	{
		const BrogueBridgeCreatureState &creature = State.creatures[index];
		if (creature.alive && creature.visibility != BROGUE_VISIBILITY_HIDDEN)
			points.push_back({creature.x, creature.y});
	}
	for (uint32_t index = 0; index < State.itemCount; ++index)
	{
		const BrogueBridgeItemState &item = State.items[index];
		if (!item.carried && item.visible) points.push_back({item.x, item.y});
	}
	for (uint32_t index = 0; index < State.cellCount; ++index)
	{
		const BrogueBridgeCellState &cell = State.cells[index];
		if (cell.currentlyVisible && (cell.isStairsUp || cell.isStairsDown || (cell.isDoor && !cell.isSecret)))
			points.push_back({cell.x, cell.y});
	}
	std::sort(points.begin(), points.end(), [](const LookPoint &left, const LookPoint &right)
	{
		return left.y != right.y ? left.y < right.y : left.x < right.x;
	});
	points.erase(std::unique(points.begin(), points.end(), [](const LookPoint &left, const LookPoint &right)
		{ return left.x == right.x && left.y == right.y; }), points.end());
	if (points.empty()) return;
	auto found = std::find_if(points.begin(), points.end(), [](const LookPoint &point)
		{ return point.x == TargetX && point.y == TargetY; });
	if (found == points.end() || ++found == points.end()) found = points.begin();
	TargetX = found->x;
	TargetY = found->y;
}

bool HandleWeaponUiInput(const event_t *event)
{
	const int key = event->data1;
	if (key == 0x10) // Q: toggle weapon menu
	{
		if (event->type == EV_KeyDown)
		{
			if (WeaponUi == WeaponUiMode::Equip) CloseWeaponUi();
			else
			{
				if (InventoryOpen) CloseInventory();
				if (WeaponUi != WeaponUiMode::None) CloseWeaponUi();
				WeaponUi = WeaponUiMode::Equip;
				WeaponSelection = 0;
				const std::vector<uint32_t> weapons = CarriedWeaponIndices();
				for (size_t index = 0; index < weapons.size(); ++index)
					if (State.items[weapons[index]].equipped) WeaponSelection = int(index) + 1;
				ShowWeaponSelector(false);
			}
		}
		return true;
	}
	if (key == 0x26) // L: toggle bridge-driven look mode
	{
		if (event->type == EV_KeyDown)
		{
			if (WeaponUi == WeaponUiMode::Look) CloseWeaponUi();
			else
			{
				if (InventoryOpen) CloseInventory();
				if (WeaponUi != WeaponUiMode::None) CloseWeaponUi();
				WeaponUi = WeaponUiMode::Look;
				TargetX = State.player.x;
				TargetY = State.player.y;
				RefreshLook();
			}
		}
		return true;
	}
	if (event->type != EV_KeyDown) return WeaponUi != WeaponUiMode::None;
	if (key == KEY_ESCAPE && WeaponUi != WeaponUiMode::None) { CloseWeaponUi(); return true; }
	if (key == 0x14) // T: toggle throw selection
	{
		if (WeaponUi == WeaponUiMode::ThrowSelect) CloseWeaponUi();
		else
		{
			if (WeaponUi != WeaponUiMode::None) CloseWeaponUi();
			WeaponUi = WeaponUiMode::ThrowSelect;
			WeaponSelection = 0;
			ShowWeaponSelector(true);
		}
		return true;
	}
	if (WeaponUi == WeaponUiMode::None) return false;
	if (WeaponUi == WeaponUiMode::Look)
	{
		if (key == KEY_SPACE || key == KEY_ENTER || key == KEY_MOUSE1)
		{
			CloseWeaponUi();
			return true;
		}
		if (key == KEY_TAB || key == KEY_MWHEELUP || key == KEY_MWHEELDOWN)
		{
			CycleLookTarget();
		}
		else
		{
			BrogueBridgeAction action;
			if (!MapKeyToAction(key, action) || action == BROGUE_ACTION_WAIT) return true;
			static const int dx[BROGUE_ACTION_COUNT] = {0,1,1,1,0,-1,-1,-1,0};
			static const int dy[BROGUE_ACTION_COUNT] = {-1,-1,0,1,1,1,0,-1,0};
			TargetX = (std::clamp)(TargetX + dx[action], 0, State.width - 1);
			TargetY = (std::clamp)(TargetY + dy[action], 0, State.height - 1);
		}
		RefreshLook();
		return true;
	}

	if (WeaponUi == WeaponUiMode::Equip || WeaponUi == WeaponUiMode::ThrowSelect)
	{
		const bool throwing = WeaponUi == WeaponUiMode::ThrowSelect;
		const std::vector<uint32_t> weapons = CarriedWeaponIndices();
		const int count = int(weapons.size()) + (throwing ? 0 : 1);
		if (key == KEY_MWHEELUP || key == 0xc8) --WeaponSelection;
		else if (key == KEY_MWHEELDOWN || key == 0xd0) ++WeaponSelection;
		else
		{
			for (size_t index = 0; index < weapons.size(); ++index)
			{
				if (State.items[weapons[index]].inventoryLetter != 0
					&& event->data2 == State.items[weapons[index]].inventoryLetter)
					WeaponSelection = int(index) + (throwing ? 0 : 1);
			}
		}
		if (count > 0) WeaponSelection = (WeaponSelection % count + count) % count;
		if (key == KEY_ENTER || key == KEY_MOUSE1 || key == 0x12) // Enter/click/E
		{
			if (throwing)
			{
				if (!weapons.empty())
				{
					BeginTargeting(State.items[weapons[WeaponSelection]].id);
					RefreshTargeting();
				}
			}
			else
			{
				if (WeaponSelection == 0)
				{
					if (State.player.equippedWeaponId != 0)
						PerformItemCommand(BROGUE_COMMAND_UNEQUIP_ITEM, State.player.equippedWeaponId);
				}
				else if (WeaponSelection - 1 < int(weapons.size()))
					PerformItemCommand(BROGUE_COMMAND_EQUIP_ITEM, State.items[weapons[WeaponSelection - 1]].id);
				CloseWeaponUi();
			}
			return true;
		}
		ShowWeaponSelector(throwing);
		return true;
	}

	if (WeaponUi == WeaponUiMode::ThrowTarget)
	{
		if (key == KEY_TAB) CycleVisibleTarget();
		else if (key == KEY_ENTER || key == KEY_MOUSE1)
		{
			const uint64_t item = ThrowItemId;
			const int x = TargetX, y = TargetY;
			CloseWeaponUi();
			PerformItemCommand(BROGUE_COMMAND_THROW_ITEM, item, x, y);
			return true;
		}
		else
		{
			BrogueBridgeAction action;
			if (!MapKeyToAction(key, action)) return true;
			static const int dx[BROGUE_ACTION_COUNT] = {0,1,1,1,0,-1,-1,-1,0};
			static const int dy[BROGUE_ACTION_COUNT] = {-1,-1,0,1,1,1,0,-1,0};
			TargetX = (std::clamp)(TargetX + dx[action], 0, State.width - 1);
			TargetY = (std::clamp)(TargetY + dy[action], 0, State.height - 1);
		}
		RefreshTargeting();
		return true;
	}
	return false;
}

double HudScale()
{
	// Bitmap text must remain on whole-pixel multiples. Fractional scaling was
	// the source of the blurred UI seen in the original implementation.
	return std::round((std::clamp)(double(brg_hud_scale), 1.0, 3.0));
}

int HudSize(int value)
{
	return int(std::lround(double(value) * HudScale()));
}

FFont *GetBrogueUiFont()
{
	if (BrogueUiFont == nullptr) BrogueUiFont = V_GetFont("BrogueUI");
	return BrogueUiFont != nullptr ? BrogueUiFont : SmallFont;
}

int StatusRailWidth()
{
	// Size the rail from its longest fixed-format row instead of assuming the
	// old Doom font width. This accommodates four-digit nutrition values and
	// common 23-character creature/status rows at every supported HUD scale.
	FFont *font = GetBrogueUiFont();
	const int contentWidth = font != nullptr
		? font->StringWidth("Nutrition   0000 / 0000")
		: 276;
	return int(std::lround(double(contentWidth) * HudScale())) + HudSize(16);
}

FFont *GetBrogueMapFont()
{
	if (BrogueMapFont == nullptr) BrogueMapFont = V_GetFont("BrogueMap");
	return BrogueMapFont != nullptr ? BrogueMapFont : SmallFont;
}

PalEntry HudColor(int color)
{
	// Brogue uses bright terminal colors on black. Use explicit RGB values so
	// the Doom IWAD's font translation tables cannot dim the custom glyphs.
	switch (color)
	{
	case CR_GOLD: return PalEntry(255, 238, 209, 76);
	case CR_GREEN: return PalEntry(255, 91, 244, 91);
	case CR_RED: return PalEntry(255, 255, 76, 76);
	case CR_CYAN: return PalEntry(255, 84, 224, 240);
	case CR_TAN: return PalEntry(255, 214, 204, 187);
	case CR_DARKGRAY: return PalEntry(255, 145, 139, 145);
	case CR_LIGHTBLUE: return PalEntry(255, 132, 132, 255);
	default: return PalEntry(255, 245, 241, 224);
	}
}

void HudText(int color, int x, int y, const char *text)
{
	if (text == nullptr || *text == '\0') return;
	DrawText(twod, GetBrogueUiFont(), CR_UNTRANSLATED, x, y, text,
		DTA_ScaleX, HudScale(), DTA_ScaleY, HudScale(),
		DTA_FillColor, HudColor(color), DTA_BilinearFilter, false, TAG_DONE);
}

void HudTextColor(PalEntry color, int x, int y, const char *text)
{
	if (text == nullptr || *text == '\0') return;
	DrawText(twod, GetBrogueUiFont(), CR_UNTRANSLATED, x, y, text,
		DTA_ScaleX, HudScale(), DTA_ScaleY, HudScale(),
		DTA_FillColor, color, DTA_BilinearFilter, false, TAG_DONE);
}

void HudRailText(int color, int x, int y, const char *text)
{
	if (text == nullptr || *text == '\0') return;
	DrawText(twod, GetBrogueUiFont(), CR_UNTRANSLATED, x, y, text,
		DTA_ScaleX, HudScale(), DTA_ScaleY, HudScale(),
		DTA_FillColor, HudColor(color), DTA_BilinearFilter, false,
		DTA_ClipRight, StatusRailWidth() - HudSize(5), TAG_DONE);
}

const char *MonsterName(int kind)
{
	if (kind >= 0 && uint32_t(kind) < MonsterCatalog.count
		&& MonsterCatalog.kinds[kind].name[0] != '\0') return MonsterCatalog.kinds[kind].name;
	return "creature";
}

FString CellDescription(const BrogueBridgeCellState *cell)
{
	if (cell == nullptr) return "Unknown terrain";
	if (cell->isStairsUp) return "Up ladder";
	if (cell->isStairsDown) return "Down ladder";
	if (cell->isDoor) return cell->isSecret ? "Secret door" : "Door";
	if (cell->isBridge) return "Bridge";
	if (cell->isLava) return "Lava";
	if (cell->isDeepWater) return "Deep water";
	if (cell->isMud) return "Mud";
	if (cell->isLiquid) return "Water";
	if (cell->isChasm) return "Chasm";
	if (cell->isSolid) return "Cavern wall";
	return "Cavern floor";
}

void DrawBrogueMinimap()
{
	// This is a compact rendering of Brogue's own final cell appearance, not a
	// second semantic color scheme. The bridge obtains these glyphs and colors
	// from getCellAppearance(), including memory, lighting and entities.
	const int cellWidth = 5;
	const int cellHeight = 8;
	const int mapWidth = State.width * cellWidth;
	const int mapHeight = State.height * cellHeight;
	const int margin = 9;
	const int pad = 4;
	const int frame = 2;
	const int originX = twod->GetWidth() - mapWidth - margin;
	const int originY = 8;
	const int frameX = originX - pad;
	const int frameY = originY - pad;
	const int frameWidth = mapWidth + pad * 2;
	const int frameHeight = mapHeight + pad * 2;
	const PalEntry frameColor(255, 102, 82, 145);
	Dim(twod, 0x00000000, .94f, frameX, frameY, frameWidth, frameHeight);
	Dim(twod, frameColor, 1.f, frameX, frameY, frameWidth, frame);
	Dim(twod, frameColor, 1.f, frameX, frameY + frameHeight - frame, frameWidth, frame);
	Dim(twod, frameColor, 1.f, frameX, frameY, frame, frameHeight);
	Dim(twod, frameColor, 1.f, frameX + frameWidth - frame, frameY, frame, frameHeight);
	FFont *font = GetBrogueMapFont();
	for (uint32_t index = 0; index < State.cellCount; ++index)
	{
		const BrogueBridgeCellState &cell = State.cells[index];
		if (!cell.discovered && !cell.currentlyVisible && !cell.magicMapped) continue;
		const int x = originX + cell.x * cellWidth;
		const int y = originY + cell.y * cellHeight;
		const PalEntry background(255, cell.backgroundRed, cell.backgroundGreen, cell.backgroundBlue);
		const PalEntry foreground(255, cell.foregroundRed, cell.foregroundGreen, cell.foregroundBlue);
		Dim(twod, background, 1.f, x, y, cellWidth, cellHeight);

		uint32_t glyph = cell.displayCodepoint;
		if (glyph == 0x00b7) glyph = '.';       // middle dot
		else if (glyph == 0x2237) glyph = ':';  // four dots
		else if (glyph == 0x25c7) glyph = '^';  // diamond
		else if (glyph == 0x22cf) glyph = '^';  // flipped V
		else if (glyph == 0x2648) glyph = '"';  // grass
		else if (glyph == 0x00df) glyph = 'S';
		else if (glyph == 0x2640 || glyph == 0x26b2) glyph = '&';
		else if (glyph == 0x266a) glyph = '?';
		else if (glyph == 0x26aa) glyph = '=';
		else if (glyph == 0x03df || glyph == 0x25cf) glyph = '*';
		else if (glyph == 0x00a4) glyph = '$';
		else if (glyph == 0x2191) glyph = ')';
		else if (glyph == 0x2193) glyph = '(';
		else if (glyph == 0x03a9) glyph = '+';
		else if (glyph == 0x29f2) glyph = '-';
		else if (glyph == 0x29f3) glyph = '+';
		else if (glyph == 0x1f780) glyph = '<';
		else if (glyph < 33 || glyph > 126) glyph = '?';
		DrawChar(twod, font, CR_UNTRANSLATED, x, y, int(glyph),
			DTA_FillColor, foreground, DTA_BilinearFilter, false, TAG_DONE);
	}
}

void DrawStatusRail()
{
	const int railWidth = StatusRailWidth();
	Dim(twod, 0x00100907, .82f, 0, 0, railWidth, twod->GetHeight());
	Dim(twod, 0x006f4c2c, .9f, railWidth - 2, 0, 2, twod->GetHeight());
	const int x = HudSize(7);
	int y = HudSize(8);
	FString text;
	text.Format("PROJECT BROOM  Depth %d", State.depth);
	HudRailText(CR_GOLD, x, y, text.GetChars()); y += HudSize(24);
	text.Format("Health      %d / %d", State.player.hp, State.player.maxHp);
	HudRailText(State.player.hp * 3 < State.player.maxHp ? CR_RED : CR_GREEN, x, y, text.GetChars()); y += HudSize(22);
	text.Format("Nutrition   %d / %d", State.player.nutrition, State.player.maxNutrition);
	HudRailText(CR_CYAN, x, y, text.GetChars()); y += HudSize(22);
	text.Format("Strength    %d", State.player.strength); HudRailText(CR_TAN, x, y, text.GetChars()); y += HudSize(22);
	text.Format("Armor       %d", State.player.armor); HudRailText(CR_TAN, x, y, text.GetChars()); y += HudSize(22);
	text.Format("Gold        %llu", (unsigned long long)State.player.gold); HudRailText(CR_GOLD, x, y, text.GetChars()); y += HudSize(22);
	text.Format("Stealth     %d", State.player.stealthRange); HudRailText(CR_DARKGRAY, x, y, text.GetChars()); y += HudSize(22);
	text.Format("Turn        %llu", (unsigned long long)State.absoluteTurn); HudRailText(CR_DARKGRAY, x, y, text.GetChars()); y += HudSize(26);

	static const char *statusNames[] = {"Searching", "Donning", "Weakened", "Telepathic", "Hallucinating",
		"Levitating", "Slowed", "Hasted", "Confused", "Burning", "Paralyzed", "Poisoned", "Entangled",
		"Nauseous", "Discordant", "Fire immune", "Explosion immune", "Nutrition", "Entering level",
		"Enraged", "Afraid", "Entranced", "Darkness", "Lifespan", "Shielded", "Invisible", "Aggravating"};
	for (int status = 0; status < int(std::size(statusNames)); ++status)
	{
		if (status == 17 || !(State.player.statusFlags & (uint64_t(1) << status))) continue;
		HudRailText(status == 9 || status == 11 ? CR_RED : CR_LIGHTBLUE, x, y, statusNames[status]);
		y += HudSize(22);
		if (y > twod->GetHeight() / 2) break;
	}

	y = (std::max)(y + HudSize(8), twod->GetHeight() / 2);
	HudRailText(CR_GOLD, x, y, "VISIBLE"); y += HudSize(24);
	int shown = 0;
	for (uint32_t index = 0; index < State.creatureCount && shown < 8; ++index)
	{
		const BrogueBridgeCreatureState &creature = State.creatures[index];
		if (!creature.alive || creature.visibility == BROGUE_VISIBILITY_HIDDEN) continue;
		text.Format("%s  %d/%d", MonsterName(creature.presentationKind), creature.hp, creature.maxHp);
		HudRailText(creature.isAlly ? CR_GREEN : CR_RED, x, y, text.GetChars()); y += HudSize(22); ++shown;
	}
	if (shown == 0) { HudRailText(CR_DARKGRAY, x, y, "No creatures in sight"); y += HudSize(22); }
	for (uint32_t index = 0; index < State.itemCount && shown < 11; ++index)
	{
		const BrogueBridgeItemState &item = State.items[index];
		if (item.carried || !item.visible) continue;
		text.Format("* %s", item.displayName); HudRailText(CR_LIGHTBLUE, x, y, text.GetChars()); y += HudSize(22); ++shown;
	}
}

struct WrappedTextRange
{
	size_t begin = 0;
	size_t end = 0;
};

std::vector<WrappedTextRange> WrapTextRanges(const char *source, int maxWidth, size_t maxLines)
{
	std::vector<WrappedTextRange> lines;
	std::string input = source != nullptr ? source : "";
	size_t at = 0;
	while (at < input.size() && lines.size() < maxLines)
	{
		// One newline ends the current source line. Consecutive newlines create
		// the blank paragraph rows used by Brogue's detail panes.
		if (input[at] == '\n')
		{
			lines.push_back({ at, at });
			++at;
			continue;
		}

		size_t end = at;
		size_t lastSpace = std::string::npos;
		while (end < input.size() && input[end] != '\n')
		{
			const std::string candidate = input.substr(at, end - at + 1);
			if (GetBrogueUiFont()->StringWidth(candidate.c_str()) * HudScale() > maxWidth) break;
			if (input[end] == ' ') lastSpace = end;
			++end;
		}
		if (end == at) ++end;
		else if (end < input.size() && input[end] != '\n'
			&& lastSpace != std::string::npos && lastSpace > at) end = lastSpace;
		size_t visibleEnd = end;
		while (visibleEnd > at && (input[visibleEnd - 1] == ' ' || input[visibleEnd - 1] == '\t')) --visibleEnd;
		lines.push_back({ at, visibleEnd });

		if (end < input.size() && input[end] == '\n')
		{
			at = end + 1;
		}
		else
		{
			at = end;
			while (at < input.size() && (input[at] == ' ' || input[at] == '\t')) ++at;
		}
	}
	return lines;
}

std::vector<std::string> WrapTextPixels(const char *source, int maxWidth, size_t maxLines)
{
	const std::string input = source != nullptr ? source : "";
	std::vector<std::string> lines;
	for (const WrappedTextRange &range : WrapTextRanges(source, maxWidth, maxLines))
		lines.push_back(input.substr(range.begin, range.end - range.begin));
	return lines;
}

void DrawWrappedText(int color, int x, int &y, const char *text, int width, int rowStep, size_t maxLines)
{
	for (const std::string &line : WrapTextPixels(text, width, maxLines))
	{
		HudText(color, x, y, line.c_str());
		y += rowStep;
	}
}

PalEntry LookSpanColor(const BrogueBridgeTextColorSpan &span)
{
	return PalEntry(255,
		(uint8_t) ((uint32_t(span.red) * 255u) / 100u),
		(uint8_t) ((uint32_t(span.green) * 255u) / 100u),
		(uint8_t) ((uint32_t(span.blue) * 255u) / 100u));
}

void DrawStyledLookText(int x, int &y, const BrogueBridgeLookResult &look,
	int width, int rowStep, size_t maxLines)
{
	const std::string detail = look.detail;
	for (const WrappedTextRange &line : WrapTextRanges(look.detail, width, maxLines))
	{
		size_t at = line.begin;
		int drawX = x;
		while (at < line.end)
		{
			const BrogueBridgeTextColorSpan *active = nullptr;
			size_t pieceEnd = line.end;
			for (uint32_t index = 0; index < look.detailColorSpanCount; ++index)
			{
				const BrogueBridgeTextColorSpan &span = look.detailColorSpans[index];
				const size_t spanBegin = span.offset;
				const size_t spanEnd = spanBegin + span.length;
				if (at >= spanBegin && at < spanEnd)
				{
					active = &span;
					pieceEnd = (std::min)(pieceEnd, spanEnd);
					break;
				}
				if (spanBegin > at) pieceEnd = (std::min)(pieceEnd, spanBegin);
			}
			const std::string piece = detail.substr(at, pieceEnd - at);
			HudTextColor(active != nullptr ? LookSpanColor(*active) : HudColor(CR_TAN),
				drawX, y, piece.c_str());
			drawX += int(GetBrogueUiFont()->StringWidth(piece.c_str()) * HudScale());
			at = pieceEnd;
		}
		y += rowStep;
	}
}

void DrawInventory()
{
	if (!InventoryOpen) return;
	const std::vector<uint32_t> inventory = CarriedInventoryIndices();
	const int width = (std::min)(twod->GetWidth() - 80, 920);
	const int height = (std::min)(twod->GetHeight() - 70, 560);
	const int x = (twod->GetWidth() - width) / 2;
	const int y = (twod->GetHeight() - height) / 2;
	const int split = x + width * 43 / 100;
	const int inset = HudSize(10);
	const int headerY = y + HudSize(8);
	const int bodyY = y + HudSize(32);
	const int rowStep = HudSize(23);
	const int footerHeight = HudSize(36);
	const int footerTop = y + height - footerHeight;
	Dim(twod, 0x00000000, .88f, x, y, width, height);
	Dim(twod, 0x0075502d, .95f, x, y, width, 2);
	Dim(twod, 0x0075502d, .95f, split, y, 2, height);
	Dim(twod, 0x00000000, .96f, x, footerTop, width, footerHeight);
	Dim(twod, 0x0075502d, .95f, x, footerTop, width, 1);
	HudText(CR_GOLD, x + inset, headerY, "INVENTORY");
	if (inventory.empty())
	{
		HudText(CR_DARKGRAY, x + inset, bodyY, "Your pack is empty.");
		HudText(CR_TAN, x + inset, footerTop, "I / Esc: close");
		return;
	}
	InventorySelection = (std::clamp)(InventorySelection, 0, int(inventory.size()) - 1);
	int rowY = bodyY;
	const size_t maxRows = size_t((std::max)(1, (footerTop - bodyY - HudSize(4)) / rowStep));
	for (size_t row = 0; row < inventory.size() && row < maxRows; ++row)
	{
		const BrogueBridgeItemState &item = State.items[inventory[row]];
		if (int(row) == InventorySelection) Dim(twod, 0x00634a27, .7f, x + HudSize(5), rowY - HudSize(1), split - x - HudSize(10), rowStep);
		FString line;
		line.Format("%c) %s%s", item.inventoryLetter ? item.inventoryLetter : '?', item.displayName,
			item.equipped ? " (equipped)" : "");
		HudText(int(row) == InventorySelection ? CR_WHITE : CR_TAN, x + inset, rowY, line.GetChars());
		rowY += rowStep;
	}
	const BrogueBridgeItemState &selected = State.items[inventory[InventorySelection]];
	HudText(CR_GOLD, split + inset, headerY, selected.displayName);
	rowY = bodyY;
	const int detailWidth = x + width - (split + inset) - inset;
	DrawWrappedText(CR_TAN, split + inset, rowY, selected.detailText, detailWidth, rowStep, maxRows);
	FString actions = "Arrows/Wheel Select";
	if (selected.actionFlags & BROGUE_ITEM_ACTION_EQUIP) actions += "  |  Enter/E Equip";
	if (selected.actionFlags & BROGUE_ITEM_ACTION_UNEQUIP) actions += "  |  Enter/E Remove";
	if (selected.actionFlags & BROGUE_ITEM_ACTION_APPLY) actions += "  |  Enter/U Use";
	if (selected.actionFlags & BROGUE_ITEM_ACTION_DROP) actions += "  |  D Drop";
	if (selected.actionFlags & BROGUE_ITEM_ACTION_THROW) actions += "  |  T Throw";
	actions += "  |  I/Esc Close";
	HudText(CR_LIGHTBLUE, x + inset, footerTop + HudSize(7), actions.GetChars());
}

void DrawApplyOverlay()
{
	if (ApplyUi == ApplyUiMode::None || twod == nullptr) return;
	const int width = (std::min)(twod->GetWidth() - HudSize(80), HudSize(620));
	const int rowStep = HudSize(23);
	const int choiceRows = ApplyUi == ApplyUiMode::SelectItem
		? (std::min)(int(ApplyChoiceIds.size()), 10) : 0;
	const int height = HudSize(100) + choiceRows * rowStep;
	const int x = (twod->GetWidth() - width) / 2;
	const int y = (twod->GetHeight() - height) / 2;
	const int inset = HudSize(12);
	Dim(twod, 0x00000000, .97f, x, y, width, height);
	Dim(twod, 0x00916d24, .95f, x, y, width, 2);
	Dim(twod, 0x00916d24, .95f, x, y + height - 2, width, 2);
	HudText(CR_GOLD, x + inset, y + HudSize(10),
		ApplyPrompt.IsEmpty() ? "Use item?" : ApplyPrompt.GetChars());
	if (ApplyUi == ApplyUiMode::Confirm)
	{
		HudText(CR_LIGHTBLUE, x + inset, y + height - HudSize(31),
			"Y / Enter: confirm    N / Esc: cancel");
		return;
	}
	int rowY = y + HudSize(39);
	for (int index = 0; index < choiceRows; ++index)
	{
		const BrogueBridgeItemState *choice = FindItem(ApplyChoiceIds[index]);
		if (choice == nullptr) continue;
		if (index == ApplyChoiceSelection)
			Dim(twod, 0x00634a27, .75f, x + HudSize(6), rowY - HudSize(1), width - HudSize(12), rowStep);
		FString line;
		line.Format("%c) %s%s", choice->inventoryLetter ? choice->inventoryLetter : '?',
			choice->displayName, choice->equipped ? " (equipped)" : "");
		HudText(index == ApplyChoiceSelection ? CR_WHITE : CR_TAN, x + inset, rowY, line.GetChars());
		rowY += rowStep;
	}
	HudText(CR_LIGHTBLUE, x + inset, y + height - HudSize(31),
		"Arrows / Wheel / Letter: select    Enter / U: use (selection required)");
}

void DrawCommandConfirmationOverlay()
{
	if (!CommandConfirmationOpen || twod == nullptr) return;
	const int width = (std::min)(twod->GetWidth() - HudSize(80), HudSize(620));
	const int height = HudSize(112);
	const int x = (twod->GetWidth() - width) / 2;
	const int y = (twod->GetHeight() - height) / 2;
	const int inset = HudSize(14);
	Dim(twod, 0x00000000, .97f, x, y, width, height);
	Dim(twod, 0x00916d24, .95f, x, y, width, 2);
	Dim(twod, 0x00916d24, .95f, x, y + height - 2, width, 2);
	HudText(CR_GOLD, x + inset, y + HudSize(12), "CONFIRM ACTION");
	int textY = y + HudSize(40);
	DrawWrappedText(CR_TAN, x + inset, textY,
		CommandConfirmationPrompt.IsEmpty() ? "Proceed?" : CommandConfirmationPrompt.GetChars(),
		width - inset * 2, HudSize(23), 2);
	HudText(CR_LIGHTBLUE, x + inset, y + height - HudSize(28),
		"Y / Enter: yes    N / Esc: no");
}

void DrawGameOverOverlay()
{
	if (!State.player.gameHasEnded || twod == nullptr) return;
	const int screenWidth = twod->GetWidth();
	const int screenHeight = twod->GetHeight();
	const int width = (std::min)(screenWidth - HudSize(60), HudSize(760));
	const int height = (std::min)(screenHeight - HudSize(60), HudSize(390));
	const int x = (screenWidth - width) / 2;
	const int y = (screenHeight - height) / 2;
	const int inset = HudSize(24);
	const int rowStep = HudSize(25);

	Dim(twod, 0x00000000, .94f, 0, 0, screenWidth, screenHeight);
	Dim(twod, 0x00000000, .98f, x, y, width, height);
	Dim(twod, 0x00916d24, 1.0f, x, y, width, 2);
	Dim(twod, 0x00916d24, 1.0f, x, y + height - 2, width, 2);

	const char *heading = State.gameResult.outcome == BROGUE_GAME_OUTCOME_QUIT
		? "THE ADVENTURE ENDS" : "YOU DIE...";
	const int headingWidth = int(GetBrogueUiFont()->StringWidth(heading) * HudScale());
	HudText(State.gameResult.outcome == BROGUE_GAME_OUTCOME_QUIT ? CR_GOLD : CR_RED,
		x + (width - headingWidth) / 2, y + HudSize(24), heading);

	int textY = y + HudSize(78);
	DrawWrappedText(CR_TAN, x + inset, textY,
		State.gameResult.summary[0] != '\0' ? State.gameResult.summary : "The run has ended.",
		width - inset * 2, rowStep, 4);

	textY += HudSize(22);
	FString stats;
	stats.Format("Score: %lld    Gold: %llu    Deepest depth: %d    Turns: %llu",
		(long long)State.gameResult.score,
		(unsigned long long)State.player.gold,
		State.gameResult.deepestDepth > 0 ? State.gameResult.deepestDepth : State.depth,
		(unsigned long long)(State.gameResult.turn > 0 ? State.gameResult.turn : State.absoluteTurn));
	HudText(CR_GOLD, x + inset, textY, stats.GetChars());

	const char *instruction = "Space / Enter / Esc: return to main menu";
	const int instructionWidth = int(GetBrogueUiFont()->StringWidth(instruction) * HudScale());
	HudText(CR_LIGHTBLUE, x + (width - instructionWidth) / 2,
		y + height - HudSize(43), instruction);
}

void DrawWeaponMenu()
{
	if (WeaponUi != WeaponUiMode::Equip && WeaponUi != WeaponUiMode::ThrowSelect) return;
	const bool throwing = WeaponUi == WeaponUiMode::ThrowSelect;
	const std::vector<uint32_t> weapons = CarriedWeaponIndices();
	const int count = int(weapons.size()) + (throwing ? 0 : 1);
	const int width = (std::min)(twod->GetWidth() - 80, 860);
	const int height = (std::min)(twod->GetHeight() - 90, 500);
	const int x = (twod->GetWidth() - width) / 2;
	const int y = (twod->GetHeight() - height) / 2;
	const int split = x + width * 42 / 100;
	const int inset = HudSize(10);
	const int headerY = y + HudSize(8);
	const int bodyY = y + HudSize(38);
	const int rowStep = HudSize(23);
	const int footerHeight = HudSize(36);
	const int footerTop = y + height - footerHeight;
	Dim(twod, 0x00000000, .9f, x, y, width, height);
	Dim(twod, 0x0075502d, .95f, x, y, width, 2);
	Dim(twod, 0x0075502d, .95f, split, y, 2, height);
	Dim(twod, 0x00000000, .96f, x, footerTop, width, footerHeight);
	Dim(twod, 0x0075502d, .95f, x, footerTop, width, 1);
	HudText(CR_GOLD, x + inset, headerY, throwing ? "THROW WEAPON" : "WEAPONS");

	if (count <= 0)
	{
		HudText(CR_DARKGRAY, x + inset, bodyY, "You have no throwable weapons.");
		return;
	}
	WeaponSelection = (std::clamp)(WeaponSelection, 0, count - 1);
	int rowY = bodyY;
	if (!throwing)
	{
		if (WeaponSelection == 0) Dim(twod, 0x00634a27, .7f, x + HudSize(5), rowY - HudSize(1), split - x - HudSize(10), rowStep);
		HudText(WeaponSelection == 0 ? CR_WHITE : CR_TAN, x + inset, rowY, "-  Empty hands");
		rowY += rowStep;
	}
	for (size_t index = 0; index < weapons.size(); ++index)
	{
		const BrogueBridgeItemState &item = State.items[weapons[index]];
		const int selection = int(index) + (throwing ? 0 : 1);
		if (selection == WeaponSelection) Dim(twod, 0x00634a27, .7f, x + HudSize(5), rowY - HudSize(1), split - x - HudSize(10), rowStep);
		FString line;
		line.Format("%c) %s%s", item.inventoryLetter ? item.inventoryLetter : '?', item.displayName,
			item.equipped ? "  [equipped]" : "");
		HudText(selection == WeaponSelection ? CR_WHITE : CR_TAN, x + inset, rowY, line.GetChars());
		rowY += rowStep;
	}

	if (!throwing && WeaponSelection == 0)
	{
		HudText(CR_GOLD, split + inset, headerY, "Empty hands");
		HudText(CR_TAN, split + inset, bodyY, "Fight without an equipped weapon.");
	}
	else
	{
		const int weaponIndex = WeaponSelection - (throwing ? 0 : 1);
		const BrogueBridgeItemState &item = State.items[weapons[weaponIndex]];
		HudText(CR_GOLD, split + inset, headerY, item.displayName);
		rowY = bodyY;
		FString stats;
		stats.Format("Damage %d-%d   Strength %d   Enchantment %+d",
			item.damageLower, item.damageUpper, item.strengthRequired, item.enchantment);
		HudText(CR_CYAN, split + inset, rowY, stats.GetChars());
		rowY += rowStep + HudSize(4);
		const int detailWidth = x + width - (split + inset) - inset;
		const size_t maxRows = size_t((std::max)(1, (footerTop - rowY) / rowStep));
		DrawWrappedText(CR_TAN, split + inset, rowY, item.detailText, detailWidth, rowStep, maxRows);
	}
	HudText(CR_LIGHTBLUE, x + inset, footerTop + HudSize(7),
		throwing
			? "Arrows/Wheel Select  |  Enter/E Aim  |  T/Esc Close"
			: "Arrows/Wheel Select  |  Enter/E Equip  |  Q/Esc Close");
}

void DrawLookOverlay()
{
	if (WeaponUi != WeaponUiMode::Look) return;
	const int railWidth = StatusRailWidth();
	const int availableWidth = twod->GetWidth() - railWidth;
	const int width = (std::max)(HudSize(320), (std::min)(availableWidth - HudSize(36), HudSize(760)));
	const int height = (std::max)(HudSize(280),
		(std::min)(twod->GetHeight() - HudSize(100), HudSize(520)));
	const int x = railWidth + (availableWidth - width) / 2;
	const int y = twod->GetHeight() - HudSize(28) - height - HudSize(14);
	const int inset = HudSize(12);
	const int rowStep = HudSize(23);
	const int footerHeight = HudSize(36);
	const int footerTop = y + height - footerHeight;
	const PalEntry border(255, 137, 111, 39);
	Dim(twod, 0x00000000, .91f, x, y, width, height);
	Dim(twod, border, 1.f, x, y, width, 2);
	Dim(twod, border, 1.f, x, y, 2, height);
	Dim(twod, border, 1.f, x + width - 2, y, 2, height);
	Dim(twod, 0x00000000, .97f, x, footerTop, width, footerHeight);
	Dim(twod, border, 1.f, x, footerTop, width, 1);

	FString coordinate;
	coordinate.Format("LOOK  %d,%d", TargetX, TargetY);
	const int coordinateWidth = int(GetBrogueUiFont()->StringWidth(coordinate.GetChars()) * HudScale());
	HudText(CR_DARKGRAY, x + width - inset - coordinateWidth, y + HudSize(9), coordinate.GetChars());

	const bool hasBrogueDetail = LookResult.detail[0] != '\0'
		&& (LookResult.kind == BROGUE_LOOK_ITEM || LookResult.kind == BROGUE_LOOK_CREATURE);
	int textY = y + HudSize(12);
	if (hasBrogueDetail)
	{
		const size_t rows = size_t((std::max)(1, (footerTop - textY - HudSize(5)) / rowStep));
		DrawStyledLookText(x + inset, textY, LookResult,
			width - inset * 2, rowStep, rows);
	}
	else
	{
		int titleColor = CR_TAN;
		if (LookResult.kind == BROGUE_LOOK_PLAYER) titleColor = CR_GREEN;
		const char *title = LookResult.title[0] != '\0' ? LookResult.title : "Unknown";
		HudText(titleColor, x + inset, textY, title);
		textY += rowStep + HudSize(3);
		const size_t rows = size_t((std::max)(1, (footerTop - textY - HudSize(5)) / rowStep));
		DrawWrappedText(CR_WHITE, x + inset, textY, LookResult.summary,
			width - inset * 2, rowStep, rows);
	}
	HudText(CR_LIGHTBLUE, x + inset, footerTop + HudSize(7),
		"Move Cursor  |  Tab/Wheel Next  |  L/Space/Esc Close");
}
}

// Development-only semantic smoke command. This exercises the same native
// bridge path as keyboard input without depending on Windows raw-input
// injection, which is intentionally not synthesized by the test harness.
CCMD(brg_wait)
{
	PendingWait = true;
	if (!IsBrogueMap())
	{
		Printf("Brogue bridge: brg_wait queued until a BRG map is loaded.\n");
		return;
	}
	PerformQueuedWait();
}

// Deterministic in-engine bridge smoke harness. It is intentionally semantic
// (N/NE/E/SE/S/SW/W/NW/WAIT), so it exercises the same Brogue authority path
// as physical input without synthesizing OS keyboard events.
CCMD(brg_actions)
{
	PendingActions.clear();
	PendingActionIndex = 0;
	for (int index = 1; index < argv.argc(); ++index)
	{
		BrogueBridgeAction action;
		if (!ParseActionName(argv[index], action))
		{
			Printf("Brogue bridge: unknown scripted action '%s'.\n", argv[index]);
			PendingActions.clear();
			return;
		}
		PendingActions.push_back(action);
	}
	Printf("Brogue bridge: queued %u scripted actions.\n", unsigned(PendingActions.size()));
}

// Lists the presentation-safe item view. Unknown Brogue identities deliberately
// report kind=-1 and use the category model instead of exposing the true kind.
CCMD(brg_pickups)
{
	if (!EnsureStarted()) return;
	SyncItems();
	Printf("Brogue pickups: %u authoritative item records, %u floor proxies.\n",
		State.itemCount, unsigned(ItemProxies.size()));
	for (uint32_t index = 0; index < State.itemCount; ++index)
	{
		const BrogueBridgeItemState &item = State.items[index];
		if (item.carried) continue;
		Printf("  id=%llu category=%d kind=%d cell=%d,%d visible=%s class=%s\n",
			(unsigned long long)item.id, item.category, PickupVisualKind(item), item.x, item.y,
			item.visible ? "true" : "false", PickupClassName(item).GetChars());
	}
}

CCMD(brg_monsters)
{
	if (!EnsureStarted()) return;
	SyncMonsters();
	Printf("Brogue monsters: %u authoritative creatures, %u stable frontend proxies.\n",
		State.creatureCount, unsigned(MonsterProxies.size()));
	for (uint32_t index = 0; index < State.creatureCount; ++index)
	{
		const BrogueBridgeCreatureState &creature = State.creatures[index];
		Printf("  id=%llu kind=%d presentation=%d cell=%d,%d hp=%d/%d visibility=%d ally=%s\n",
			(unsigned long long)creature.id, creature.kind, creature.presentationKind,
			creature.x, creature.y, creature.hp, creature.maxHp, int(creature.visibility),
			creature.isAlly ? "true" : "false");
	}
}

CCMD(brg_inventory)
{
	InventoryOpen = !InventoryOpen;
	InventorySelection = 0;
}

void BrogueBridge_DrawHud(void)
{
	if (!IsBrogueMap() || !EnsureStarted() || twod == nullptr || SmallFont == nullptr) return;
	DrawStatusRail();
	DrawBrogueMinimap();
	const int railWidth = StatusRailWidth();
	for (uint32_t line = 0; line < State.messageCount && line < 3; ++line)
		HudText(line == 0 ? CR_WHITE : CR_TAN, railWidth + HudSize(10), HudSize(8) + int(line) * HudSize(23), State.messages[line]);
	const BrogueBridgeCellState *cell = FindStateCell(State.player.x, State.player.y);
	FString footer;
	footer.Format("%s  |  Cell %d,%d  |  L Look  |  I Inventory  |  Q Weapons  |  T Throw  |  Space Wait",
		CellDescription(cell).GetChars(), State.player.x, State.player.y);
	const int footerHeight = HudSize(28);
	Dim(twod, 0x00000000, .62f, railWidth, twod->GetHeight() - footerHeight, twod->GetWidth() - railWidth, footerHeight);
	HudText(CR_TAN, railWidth + HudSize(10), twod->GetHeight() - HudSize(24), footer.GetChars());
	DrawInventory();
	DrawApplyOverlay();
	DrawWeaponMenu();
	DrawLookOverlay();
	DrawCommandConfirmationOverlay();
	DrawGameOverOverlay();
}

bool HandleGameOverInput(const event_t *event)
{
	if (!State.player.gameHasEnded) return false;
	if (event->type == EV_KeyDown
		&& (event->data1 == KEY_ENTER || event->data1 == KEY_SPACE
			|| event->data1 == KEY_ESCAPE || event->data1 == KEY_MOUSE1))
	{
		C_DoCommand("menu_main");
	}
	return true;
}

bool HandleCommandConfirmationInput(const event_t *event)
{
	if (!CommandConfirmationOpen) return false;
	if (event->type == EV_KeyUp) return true;
	if (event->type != EV_KeyDown) return true;
	if (event->data1 == KEY_ENTER || event->data2 == 'y' || event->data2 == 'Y')
	{
		BrogueBridgeCommand command = CommandConfirmationCommand;
		const FString source = CommandConfirmationSource;
		if (command.confirmed < 255) ++command.confirmed;
		ClearCommandConfirmation();
		SubmitConfirmableCommand(command, source.GetChars());
	}
	else if (event->data1 == KEY_ESCAPE || event->data1 == KEY_MOUSE2
		|| event->data2 == 'n' || event->data2 == 'N')
	{
		ClearCommandConfirmation();
	}
	return true;
}

bool BrogueBridge_HandleInput(const event_t *event)
{
	if (event == nullptr || !IsBrogueMap()) return false;
	if (!EnsureStarted()) return false;
	if (HandleGameOverInput(event)) return true;
	if (HandleCommandConfirmationInput(event)) return true;
	if (event->data1 == KEY_MOUSE2 && WeaponUi != WeaponUiMode::None)
	{
		if (event->type == EV_KeyDown) CloseWeaponUi();
		return true;
	}
	if (HandleInventoryInput(event)) return true;
	if (HandleWeaponUiInput(event)) return true;
#ifdef _WIN32
	// Comparison mode samples numpad edges globally in PrepareTiccmd so one
	// key drives both windows regardless of which one currently has focus.
	if (brg_compare_pid > 0 && IsComparisonScanCode(event->data1)) return true;
#endif

	BrogueBridgeAction action;
	if (event->data1 == KEY_MOUSE1)
	{
		const int facing = FacingOctant();
		if (facing < 0) return true;
		action = FacingActions[facing];
	}
	else if (!MapKeyToAction(event->data1, action)) return false;

	// Consume both edges so GZDoom's button map cannot retain or execute a
	// normal Doom movement command. Platform input filtering removes OS
	// key-repeat events before they reach event_t.
	if (event->type == EV_KeyUp) return true;
	if (event->type != EV_KeyDown) return false;

	if (MonsterAnimationsActive() || Projectile.actor != nullptr)
	{
		if (!HasBufferedAction)
		{
			BufferedAction = action;
			HasBufferedAction = true;
		}
		return true;
	}
	PerformAction(action, "input");
	return true;
}

void BrogueBridge_PrepareTiccmd(ticcmd_t *cmd)
{
	if (cmd == nullptr || !IsBrogueMap()) return;
	EnsureStarted();
	if (!Started) return;
	if (!InventoryOpen && WeaponUi == WeaponUiMode::None && !CommandConfirmationOpen) PollComparisonInput();
	// A Brogue-driven map change is applied by GZDoom after the action returns.
	// Project the authoritative landing coordinate as soon as that map is live.
	if (primaryLevel->levelnum == State.depth)
	{
		SyncPlayer();
		SyncFallShaftMarker();
		SyncDoorMarkers();
		SyncItems();
		SyncMonsters();
	}
	// GZDoom's levelnum is not guaranteed to match MAPINFO during the first
	// player setup tics. Weapon projection only depends on the live pawn and
	// authoritative inventory, so retry it independently until initialized.
	SyncWeaponView();
	if (State.player.gameHasEnded)
	{
		PendingWait = false;
		PendingActions.clear();
		PendingActionIndex = 0;
		HasBufferedAction = false;
		cmd->ucmd.forwardmove = 0;
		cmd->ucmd.sidemove = 0;
		cmd->ucmd.upmove = 0;
		cmd->ucmd.buttons = 0;
		return;
	}
	const bool animating = TickMonsterAnimations();
	const bool projectileAnimating = TickProjectile();
	if (!CommandConfirmationOpen && !animating && !projectileAnimating && HasBufferedAction)
	{
		const BrogueBridgeAction action = BufferedAction;
		HasBufferedAction = false;
		BufferedAction = BROGUE_ACTION_WAIT;
		PerformAction(action, "buffered-input");
	}
	if (!CommandConfirmationOpen && !MonsterAnimationsActive() && Projectile.actor == nullptr) PerformQueuedWait();
	if (!CommandConfirmationOpen && !MonsterAnimationsActive() && Projectile.actor == nullptr && PendingActionIndex < PendingActions.size())
	{
		PerformAction(PendingActions[PendingActionIndex++], "brg_actions");
		if (PendingActionIndex == PendingActions.size())
		{
			Printf("Brogue bridge: scripted action queue complete.\n");
			PendingActions.clear();
			PendingActionIndex = 0;
		}
	}

	// View angle/pitch remain GZDoom presentation controls. Prevent every
	// gameplay-affecting Doom command and all translational movement.
	cmd->ucmd.forwardmove = 0;
	cmd->ucmd.sidemove = 0;
	cmd->ucmd.upmove = 0;
	cmd->ucmd.buttons = 0;
}

void BrogueBridge_Shutdown(void)
{
	// Shutdown can be invoked after FLevelLocals has already destroyed its
	// actors. Never dereference presentation pointers from this callback.
	DetachLevelPresentation();
	if (Api.shutdown != nullptr && Started)
		Api.shutdown();
	Started = false;
	PendingWait = false;
	PendingActions.clear();
	PendingActionIndex = 0;
	BufferedAction = BROGUE_ACTION_WAIT;
	HasBufferedAction = false;
	WeaponUi = WeaponUiMode::None;
	LookResult = {};
	InventoryOpen = false;
	InventorySelection = 0;
	ApplyUi = ApplyUiMode::None;
	ApplyItemId = 0;
	ApplyChoiceIds.clear();
	ApplyChoiceSelection = 0;
	ApplyPrompt = "";
	ClearCommandConfirmation();
#ifdef _WIN32
	ComparisonWindow = nullptr;
	std::fill(std::begin(ComparisonKeysDown), std::end(ComparisonKeysDown), false);
#endif
	ThrowItemId = 0;
	Loaded = false;
#ifdef _WIN32
	if (Api.module != nullptr)
		FreeLibrary(Api.module);
	Api = {};
#endif
}
