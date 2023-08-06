from typing import Protocol, Optional, TypeVar, List, Generic, no_type_check
from dataclasses import dataclass

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class Symbol(Generic[A, B]):
    # Either a list of at least one address or None if not defined for the region.
    addresses: A
    # Like addresses but memory-absolute
    absolute_addresses: A
    # None for most functions. Data fields should generally have a length defined.
    length: B
    description: str

    @property
    @no_type_check
    def address(self) -> int:
        """First / main address. Raises an IndexError/TypeError if no address is defined."""
        return self.addresses[0]

    @property
    @no_type_check
    def absolute_address(self) -> int:
        """First / main address (absolute). Raises an IndexError/TypeError if no address is defined."""
        return self.absolute_addresses[0]


T = TypeVar("T")
U = TypeVar("U")
L = TypeVar("L")


class SectionProtocol(Protocol[T, U, L]):
    name: str
    description: str
    loadaddress: L
    length: int
    functions: T
    data: U


class Arm9FunctionsProtocol(Protocol):

    InitMemAllocTable: Symbol[
        List[int],
        None,
    ]

    SetMemAllocatorParams: Symbol[
        List[int],
        None,
    ]

    GetAllocArenaDefault: Symbol[
        List[int],
        None,
    ]

    GetFreeArenaDefault: Symbol[
        List[int],
        None,
    ]

    InitMemArena: Symbol[
        List[int],
        None,
    ]

    MemAllocFlagsToBlockType: Symbol[
        List[int],
        None,
    ]

    FindAvailableMemBlock: Symbol[
        List[int],
        None,
    ]

    SplitMemBlock: Symbol[
        List[int],
        None,
    ]

    MemAlloc: Symbol[
        List[int],
        None,
    ]

    MemFree: Symbol[
        List[int],
        None,
    ]

    MemArenaAlloc: Symbol[
        List[int],
        None,
    ]

    CreateMemArena: Symbol[
        List[int],
        None,
    ]

    MemLocateSet: Symbol[
        List[int],
        None,
    ]

    MemLocateUnset: Symbol[
        List[int],
        None,
    ]

    RoundUpDiv256: Symbol[
        List[int],
        None,
    ]

    MultiplyByFixedPoint: Symbol[
        List[int],
        None,
    ]

    UMultiplyByFixedPoint: Symbol[
        List[int],
        None,
    ]

    GetRngSeed: Symbol[
        Optional[List[int]],
        None,
    ]

    SetRngSeed: Symbol[
        Optional[List[int]],
        None,
    ]

    Rand16Bit: Symbol[
        List[int],
        None,
    ]

    RandInt: Symbol[
        List[int],
        None,
    ]

    RandRange: Symbol[
        List[int],
        None,
    ]

    Rand32Bit: Symbol[
        List[int],
        None,
    ]

    RandIntSafe: Symbol[
        List[int],
        None,
    ]

    RandRangeSafe: Symbol[
        List[int],
        None,
    ]

    WaitForever: Symbol[
        List[int],
        None,
    ]

    InitMemAllocTableVeneer: Symbol[
        List[int],
        None,
    ]

    MemZero: Symbol[
        List[int],
        None,
    ]

    MemcpySimple: Symbol[
        List[int],
        None,
    ]

    TaskProcBoot: Symbol[
        List[int],
        None,
    ]

    EnableAllInterrupts: Symbol[
        List[int],
        None,
    ]

    GetTime: Symbol[
        List[int],
        None,
    ]

    DisableAllInterrupts: Symbol[
        List[int],
        None,
    ]

    SoundResume: Symbol[
        List[int],
        None,
    ]

    CardPullOutWithStatus: Symbol[
        List[int],
        None,
    ]

    CardPullOut: Symbol[
        List[int],
        None,
    ]

    CardBackupError: Symbol[
        List[int],
        None,
    ]

    HaltProcessDisp: Symbol[
        List[int],
        None,
    ]

    OverlayIsLoaded: Symbol[
        List[int],
        None,
    ]

    LoadOverlay: Symbol[
        List[int],
        None,
    ]

    UnloadOverlay: Symbol[
        List[int],
        None,
    ]

    EuclideanNorm: Symbol[
        Optional[List[int]],
        None,
    ]

    ClampComponentAbs: Symbol[
        List[int],
        None,
    ]

    KeyWaitInit: Symbol[
        List[int],
        None,
    ]

    DataTransferInit: Symbol[
        List[int],
        None,
    ]

    DataTransferStop: Symbol[
        List[int],
        None,
    ]

    FileInitVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    FileOpen: Symbol[
        List[int],
        None,
    ]

    FileGetSize: Symbol[
        List[int],
        None,
    ]

    FileRead: Symbol[
        List[int],
        None,
    ]

    FileSeek: Symbol[
        List[int],
        None,
    ]

    FileClose: Symbol[
        List[int],
        None,
    ]

    LoadFileFromRom: Symbol[
        List[int],
        None,
    ]

    GetDebugFlag1: Symbol[
        List[int],
        None,
    ]

    SetDebugFlag1: Symbol[
        List[int],
        None,
    ]

    AppendProgPos: Symbol[
        List[int],
        None,
    ]

    DebugPrintTrace: Symbol[
        List[int],
        None,
    ]

    DebugPrint0: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDebugFlag2: Symbol[
        List[int],
        None,
    ]

    SetDebugFlag2: Symbol[
        List[int],
        None,
    ]

    DebugPrint: Symbol[
        List[int],
        None,
    ]

    FatalError: Symbol[
        List[int],
        None,
    ]

    IsAuraBow: Symbol[
        List[int],
        None,
    ]

    SprintfStatic: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMoneyCarried: Symbol[
        List[int],
        None,
    ]

    IsBagFull: Symbol[
        List[int],
        None,
    ]

    CountItemTypeInBag: Symbol[
        List[int],
        None,
    ]

    AddItemToBag: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x39: Symbol[
        List[int],
        None,
    ]

    CountItemTypeInStorage: Symbol[
        List[int],
        None,
    ]

    RemoveItemsTypeInStorage: Symbol[
        List[int],
        None,
    ]

    AddItemToStorage: Symbol[
        List[int],
        None,
    ]

    SetMoneyStored: Symbol[
        List[int],
        None,
    ]

    GetExclusiveItemOffset: Symbol[
        List[int],
        None,
    ]

    ApplyExclusiveItemStatBoosts: Symbol[
        List[int],
        None,
    ]

    SetExclusiveItemEffect: Symbol[
        List[int],
        None,
    ]

    ExclusiveItemEffectFlagTest: Symbol[
        List[int],
        None,
    ]

    ApplyGummiBoostsGroundMode: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveTargetAndRange: Symbol[
        List[int],
        None,
    ]

    GetMoveType: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveBasePower: Symbol[
        List[int],
        None,
    ]

    GetMoveAccuracyOrAiChance: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMaxPp: Symbol[
        List[int],
        None,
    ]

    GetMoveCritChance: Symbol[
        List[int],
        None,
    ]

    IsRecoilMove: Symbol[
        Optional[List[int]],
        None,
    ]

    IsPunchMove: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveCategory: Symbol[
        List[int],
        None,
    ]

    LoadWteFromRom: Symbol[
        List[int],
        None,
    ]

    LoadWteFromFileDirectory: Symbol[
        List[int],
        None,
    ]

    UnloadWte: Symbol[
        List[int],
        None,
    ]

    HandleSir0Translation: Symbol[
        List[int],
        None,
    ]

    HandleSir0TranslationVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    GetLanguageType: Symbol[
        List[int],
        None,
    ]

    GetLanguage: Symbol[
        List[int],
        None,
    ]

    PreprocessString: Symbol[
        List[int],
        None,
    ]

    StrcpySimple: Symbol[
        List[int],
        None,
    ]

    StrncpySimple: Symbol[
        List[int],
        None,
    ]

    StringFromMessageId: Symbol[
        List[int],
        None,
    ]

    SetScreenWindowsColor: Symbol[
        List[int],
        None,
    ]

    SetBothScreensWindowsColor: Symbol[
        List[int],
        None,
    ]

    GetNotifyNote: Symbol[
        Optional[List[int]],
        None,
    ]

    SetNotifyNote: Symbol[
        Optional[List[int]],
        None,
    ]

    InitMainTeamAfterQuiz: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x3: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x4: Symbol[
        List[int],
        None,
    ]

    NoteSaveBase: Symbol[
        List[int],
        None,
    ]

    NoteLoadBase: Symbol[
        List[int],
        None,
    ]

    GetGameMode: Symbol[
        Optional[List[int]],
        None,
    ]

    InitScriptVariableValues: Symbol[
        List[int],
        None,
    ]

    InitEventFlagScriptVars: Symbol[
        Optional[List[int]],
        None,
    ]

    ZinitScriptVariable: Symbol[
        List[int],
        None,
    ]

    LoadScriptVariableRaw: Symbol[
        List[int],
        None,
    ]

    LoadScriptVariableValue: Symbol[
        List[int],
        None,
    ]

    LoadScriptVariableValueAtIndex: Symbol[
        List[int],
        None,
    ]

    SaveScriptVariableValue: Symbol[
        List[int],
        None,
    ]

    SaveScriptVariableValueAtIndex: Symbol[
        List[int],
        None,
    ]

    LoadScriptVariableValueSum: Symbol[
        List[int],
        None,
    ]

    LoadScriptVariableValueBytes: Symbol[
        List[int],
        None,
    ]

    SaveScriptVariableValueBytes: Symbol[
        List[int],
        None,
    ]

    ScriptVariablesEqual: Symbol[
        List[int],
        None,
    ]

    EventFlagBackup: Symbol[
        List[int],
        None,
    ]

    DumpScriptVariableValues: Symbol[
        List[int],
        None,
    ]

    RestoreScriptVariableValues: Symbol[
        List[int],
        None,
    ]

    InitScenarioScriptVars: Symbol[
        List[int],
        None,
    ]

    SetScenarioScriptVar: Symbol[
        List[int],
        None,
    ]

    GetSpecialEpisodeType: Symbol[
        List[int],
        None,
    ]

    ScenarioFlagBackup: Symbol[
        List[int],
        None,
    ]

    InitWorldMapScriptVars: Symbol[
        List[int],
        None,
    ]

    InitDungeonListScriptVars: Symbol[
        List[int],
        None,
    ]

    SetDungeonTipShown: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDungeonTipShown: Symbol[
        Optional[List[int]],
        None,
    ]

    MonsterSpawnsEnabled: Symbol[
        List[int],
        None,
    ]

    SetAdventureLogStructLocation: Symbol[
        List[int],
        None,
    ]

    SetAdventureLogDungeonFloor: Symbol[
        List[int],
        None,
    ]

    GetAdventureLogDungeonFloor: Symbol[
        List[int],
        None,
    ]

    ClearAdventureLogStruct: Symbol[
        List[int],
        None,
    ]

    SetAdventureLogCompleted: Symbol[
        List[int],
        None,
    ]

    IsAdventureLogNotEmpty: Symbol[
        List[int],
        None,
    ]

    GetAdventureLogCompleted: Symbol[
        List[int],
        None,
    ]

    IncrementNbDungeonsCleared: Symbol[
        List[int],
        None,
    ]

    GetNbDungeonsCleared: Symbol[
        List[int],
        None,
    ]

    IncrementNbFriendRescues: Symbol[
        List[int],
        None,
    ]

    GetNbFriendRescues: Symbol[
        List[int],
        None,
    ]

    IncrementNbEvolutions: Symbol[
        List[int],
        None,
    ]

    GetNbEvolutions: Symbol[
        List[int],
        None,
    ]

    IncrementNbSteals: Symbol[
        List[int],
        None,
    ]

    IncrementNbEggsHatched: Symbol[
        List[int],
        None,
    ]

    GetNbEggsHatched: Symbol[
        List[int],
        None,
    ]

    GetNbPokemonJoined: Symbol[
        List[int],
        None,
    ]

    GetNbMovesLearned: Symbol[
        List[int],
        None,
    ]

    SetVictoriesOnOneFloor: Symbol[
        List[int],
        None,
    ]

    GetVictoriesOnOneFloor: Symbol[
        List[int],
        None,
    ]

    SetPokemonJoined: Symbol[
        List[int],
        None,
    ]

    SetPokemonBattled: Symbol[
        List[int],
        None,
    ]

    GetNbPokemonBattled: Symbol[
        List[int],
        None,
    ]

    IncrementNbBigTreasureWins: Symbol[
        List[int],
        None,
    ]

    SetNbBigTreasureWins: Symbol[
        List[int],
        None,
    ]

    GetNbBigTreasureWins: Symbol[
        List[int],
        None,
    ]

    SetNbRecycled: Symbol[
        List[int],
        None,
    ]

    GetNbRecycled: Symbol[
        List[int],
        None,
    ]

    IncrementNbSkyGiftsSent: Symbol[
        List[int],
        None,
    ]

    SetNbSkyGiftsSent: Symbol[
        List[int],
        None,
    ]

    GetNbSkyGiftsSent: Symbol[
        List[int],
        None,
    ]

    ComputeSpecialCounters: Symbol[
        List[int],
        None,
    ]

    RecruitSpecialPokemonLog: Symbol[
        List[int],
        None,
    ]

    IncrementNbFainted: Symbol[
        List[int],
        None,
    ]

    GetNbFainted: Symbol[
        List[int],
        None,
    ]

    SetItemAcquired: Symbol[
        List[int],
        None,
    ]

    GetNbItemAcquired: Symbol[
        List[int],
        None,
    ]

    SetChallengeLetterCleared: Symbol[
        List[int],
        None,
    ]

    GetSentryDutyGamePoints: Symbol[
        List[int],
        None,
    ]

    SetSentryDutyGamePoints: Symbol[
        List[int],
        None,
    ]

    SubFixedPoint: Symbol[
        List[int],
        None,
    ]

    BinToDecFixedPoint: Symbol[
        List[int],
        None,
    ]

    CeilFixedPoint: Symbol[
        List[int],
        None,
    ]

    DungeonGoesUp: Symbol[
        List[int],
        None,
    ]

    GetMaxRescueAttempts: Symbol[
        Optional[List[int]],
        None,
    ]

    JoinedAtRangeCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    ShouldCauseGameOverOnFaint: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterGender: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpriteSize: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpriteFileSize: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterPreEvolution: Symbol[
        Optional[List[int]],
        None,
    ]

    GetEvolutions: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterIdFromSpawnEntry: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterLevelFromSpawnEntry: Symbol[
        List[int],
        None,
    ]

    GetMonsterGenderVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    IsUnown: Symbol[
        List[int],
        None,
    ]

    IsShaymin: Symbol[
        List[int],
        None,
    ]

    IsCastform: Symbol[
        List[int],
        None,
    ]

    IsCherrim: Symbol[
        List[int],
        None,
    ]

    IsDeoxys: Symbol[
        List[int],
        None,
    ]

    IsMonsterOnTeam: Symbol[
        List[int],
        None,
    ]

    GetTeamMemberData: Symbol[
        Optional[List[int]],
        None,
    ]

    SetTeamSetupHeroAndPartnerOnly: Symbol[
        List[int],
        None,
    ]

    SetTeamSetupHeroOnly: Symbol[
        List[int],
        None,
    ]

    GetPartyMembers: Symbol[
        List[int],
        None,
    ]

    IqSkillFlagTest: Symbol[
        List[int],
        None,
    ]

    GetExplorerMazeMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSosMailCount: Symbol[
        List[int],
        None,
    ]

    DungeonRequestsDone: Symbol[
        List[int],
        None,
    ]

    DungeonRequestsDoneWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    AnyDungeonRequestsDone: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x3D: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x3E: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x17: Symbol[
        List[int],
        None,
    ]

    ItemAtTableIdx: Symbol[
        List[int],
        None,
    ]

    WaitForInterrupt: Symbol[
        List[int],
        None,
    ]

    FileInit: Symbol[
        List[int],
        None,
    ]

    Abs: Symbol[
        List[int],
        None,
    ]

    Mbtowc: Symbol[
        List[int],
        None,
    ]

    TryAssignByte: Symbol[
        List[int],
        None,
    ]

    TryAssignByteWrapper: Symbol[
        List[int],
        None,
    ]

    Wcstombs: Symbol[
        List[int],
        None,
    ]

    Memcpy: Symbol[
        List[int],
        None,
    ]

    Memmove: Symbol[
        List[int],
        None,
    ]

    Memset: Symbol[
        List[int],
        None,
    ]

    Memchr: Symbol[
        List[int],
        None,
    ]

    Memcmp: Symbol[
        List[int],
        None,
    ]

    MemsetInternal: Symbol[
        List[int],
        None,
    ]

    VsprintfInternalSlice: Symbol[
        List[int],
        None,
    ]

    TryAppendToSlice: Symbol[
        List[int],
        None,
    ]

    VsprintfInternal: Symbol[
        List[int],
        None,
    ]

    Vsprintf: Symbol[
        List[int],
        None,
    ]

    Snprintf: Symbol[
        List[int],
        None,
    ]

    Sprintf: Symbol[
        List[int],
        None,
    ]

    Strlen: Symbol[
        List[int],
        None,
    ]

    Strcpy: Symbol[
        List[int],
        None,
    ]

    Strncpy: Symbol[
        List[int],
        None,
    ]

    Strcat: Symbol[
        List[int],
        None,
    ]

    Strncat: Symbol[
        List[int],
        None,
    ]

    Strcmp: Symbol[
        List[int],
        None,
    ]

    Strncmp: Symbol[
        List[int],
        None,
    ]

    Strchr: Symbol[
        List[int],
        None,
    ]

    Strcspn: Symbol[
        List[int],
        None,
    ]

    Strstr: Symbol[
        List[int],
        None,
    ]

    Wcslen: Symbol[
        List[int],
        None,
    ]

    AddFloat: Symbol[
        List[int],
        None,
    ]

    DivideFloat: Symbol[
        List[int],
        None,
    ]

    FloatToDouble: Symbol[
        List[int],
        None,
    ]

    FloatToInt: Symbol[
        List[int],
        None,
    ]

    IntToFloat: Symbol[
        List[int],
        None,
    ]

    UIntToFloat: Symbol[
        List[int],
        None,
    ]

    MultiplyFloat: Symbol[
        List[int],
        None,
    ]

    Sqrtf: Symbol[
        List[int],
        None,
    ]

    SubtractFloat: Symbol[
        List[int],
        None,
    ]

    DivideInt: Symbol[
        List[int],
        None,
    ]

    DivideUInt: Symbol[
        List[int],
        None,
    ]

    DivideUIntNoZeroCheck: Symbol[
        List[int],
        None,
    ]


class Arm9DataProtocol(Protocol):

    DEFAULT_MEMORY_ARENA_SIZE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    AURA_BOW_ID_LAST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    NUMBER_OF_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_MONEY_CARRIED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_MONEY_STORED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS_VALUES_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_ID_LIMIT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_RECRUITABLE_TEAM_MEMBERS: Symbol[
        Optional[List[int]],
        None,
    ]

    CART_REMOVED_IMG_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_STAT_BOOST_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_ATTACK_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_SPECIAL_ATTACK_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_DEFENSE_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_SPECIAL_DEFENSE_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_EFFECT_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_STAT_BOOST_DATA_INDEXES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECOIL_MOVE_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PUNCH_MOVE_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS_LOCALS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS: Symbol[
        List[int],
        int,
    ]

    DUNGEON_DATA_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_RESTRICTIONS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPECIAL_BAND_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MUNCH_BELT_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GUMMI_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MIN_IQ_EXCLUSIVE_MOVE_USER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    WONDER_GUMMI_IQ_GAIN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    AURA_BOW_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MIN_IQ_ITEM_MASTER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEF_SCARF_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    POWER_BAND_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    WONDER_GUMMI_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ZINC_BAND_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TACTICS_UNLOCK_LEVEL_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OUTLAW_LEVEL_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OUTLAW_MINION_LEVEL_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IQ_SKILL_RESTRICTIONS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SECONDARY_TERRAIN_TYPES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SENTRY_MINIGAME_DATA: Symbol[
        Optional[List[int]],
        None,
    ]

    IQ_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IQ_GROUP_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IQ_GUMMI_GAIN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GUMMI_BELLY_RESTORE_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_CAPACITY_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPECIAL_EPISODE_MAIN_CHARACTERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GUEST_MONSTER_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RANK_UP_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_SPRITE_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MISSION_DUNGEON_UNLOCK_TABLE: Symbol[
        Optional[List[int]],
        None,
    ]

    EVENTS: Symbol[
        List[int],
        int,
    ]

    ENTITIES: Symbol[
        List[int],
        int,
    ]

    MAP_MARKER_PLACEMENTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MEMORY_ALLOCATION_ARENA_GETTERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PRNG_SEQUENCE_NUM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LOADED_OVERLAY_GROUP_0: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LOADED_OVERLAY_GROUP_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LOADED_OVERLAY_GROUP_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PACK_FILE_PATHS_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GAME_STATE_VALUES: Symbol[
        Optional[List[int]],
        None,
    ]

    DUNGEON_MOVE_TABLES: Symbol[
        Optional[List[int]],
        None,
    ]

    MOVE_DATA_TABLE_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LANGUAGE_INFO_DATA: Symbol[
        Optional[List[int]],
        None,
    ]

    NOTIFY_NOTE: Symbol[
        Optional[List[int]],
        None,
    ]

    DEFAULT_HERO_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_PARTNER_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GAME_MODE: Symbol[
        Optional[List[int]],
        None,
    ]

    ADVENTURE_LOG_PTR: Symbol[
        List[int],
        int,
    ]

    ITEM_TABLES_PTRS_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SMD_EVENTS_FUN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MEMORY_ALLOCATION_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_MEMORY_ARENA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_MEMORY_ARENA_BLOCKS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    JUICE_BAR_NECTAR_IQ_GAIN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TEXT_SPEED: Symbol[
        Optional[List[int]],
        None,
    ]

    HERO_START_LEVEL: Symbol[
        Optional[List[int]],
        None,
    ]

    PARTNER_START_LEVEL: Symbol[
        Optional[List[int]],
        None,
    ]


Arm9Protocol = SectionProtocol[
    Arm9FunctionsProtocol,
    Arm9DataProtocol,
    int,
]


class Overlay5FunctionsProtocol(Protocol):

    pass


class Overlay5DataProtocol(Protocol):

    pass


Overlay5Protocol = SectionProtocol[
    Overlay5FunctionsProtocol,
    Overlay5DataProtocol,
    int,
]


class Overlay14FunctionsProtocol(Protocol):

    pass


class Overlay14DataProtocol(Protocol):

    FOOTPRINT_DEBUG_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay14Protocol = SectionProtocol[
    Overlay14FunctionsProtocol,
    Overlay14DataProtocol,
    int,
]


class Overlay27FunctionsProtocol(Protocol):

    pass


class Overlay27DataProtocol(Protocol):

    DISCARD_ITEMS_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DISCARD_ITEMS_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DISCARD_ITEMS_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DISCARD_ITEMS_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay27Protocol = SectionProtocol[
    Overlay27FunctionsProtocol,
    Overlay27DataProtocol,
    int,
]


class Overlay9FunctionsProtocol(Protocol):

    pass


class Overlay9DataProtocol(Protocol):

    TOP_MENU_RETURN_MUSIC_ID: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay9Protocol = SectionProtocol[
    Overlay9FunctionsProtocol,
    Overlay9DataProtocol,
    int,
]


class Overlay32FunctionsProtocol(Protocol):

    pass


class Overlay32DataProtocol(Protocol):

    pass


Overlay32Protocol = SectionProtocol[
    Overlay32FunctionsProtocol,
    Overlay32DataProtocol,
    int,
]


class Overlay17FunctionsProtocol(Protocol):

    pass


class Overlay17DataProtocol(Protocol):

    ASSEMBLY_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_5: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_6: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_7: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay17Protocol = SectionProtocol[
    Overlay17FunctionsProtocol,
    Overlay17DataProtocol,
    int,
]


class Overlay21FunctionsProtocol(Protocol):

    pass


class Overlay21DataProtocol(Protocol):

    SWAP_SHOP_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay21Protocol = SectionProtocol[
    Overlay21FunctionsProtocol,
    Overlay21DataProtocol,
    int,
]


class Overlay15FunctionsProtocol(Protocol):

    pass


class Overlay15DataProtocol(Protocol):

    BANK_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay15Protocol = SectionProtocol[
    Overlay15FunctionsProtocol,
    Overlay15DataProtocol,
    int,
]


class Overlay29FunctionsProtocol(Protocol):

    DungeonAlloc: Symbol[
        List[int],
        None,
    ]

    GetDungeonPtrMaster: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonZInit: Symbol[
        List[int],
        None,
    ]

    DungeonFree: Symbol[
        Optional[List[int]],
        None,
    ]

    RunDungeon: Symbol[
        List[int],
        None,
    ]

    EntityIsValid: Symbol[
        Optional[List[int]],
        None,
    ]

    GetFloorType: Symbol[
        List[int],
        None,
    ]

    TryForcedLoss: Symbol[
        List[int],
        None,
    ]

    FixedRoomIsSubstituteRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    ShouldGameOverOnImportantTeamMemberFaint: Symbol[
        Optional[List[int]],
        None,
    ]

    FadeToBlack: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTileAtEntity: Symbol[
        List[int],
        None,
    ]

    SubstitutePlaceholderStringTags: Symbol[
        List[int],
        None,
    ]

    UpdateMapSurveyorFlag: Symbol[
        Optional[List[int]],
        None,
    ]

    ItemIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    IsOnMonsterSpawnList: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterIdToSpawn: Symbol[
        List[int],
        None,
    ]

    GetMonsterLevelToSpawn: Symbol[
        List[int],
        None,
    ]

    GetLeader: Symbol[
        Optional[List[int]],
        None,
    ]

    TickStatusTurnCounter: Symbol[
        List[int],
        None,
    ]

    AdvanceFrame: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateDungeonRngSeed: Symbol[
        List[int],
        None,
    ]

    GetDungeonRngPreseed: Symbol[
        List[int],
        None,
    ]

    SetDungeonRngPreseed: Symbol[
        List[int],
        None,
    ]

    InitDungeonRng: Symbol[
        List[int],
        None,
    ]

    DungeonRand16Bit: Symbol[
        List[int],
        None,
    ]

    DungeonRandInt: Symbol[
        List[int],
        None,
    ]

    DungeonRandRange: Symbol[
        List[int],
        None,
    ]

    DungeonRandOutcome: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcStatusDuration: Symbol[
        List[int],
        None,
    ]

    DungeonRngUnsetSecondary: Symbol[
        List[int],
        None,
    ]

    DungeonRngSetSecondary: Symbol[
        List[int],
        None,
    ]

    DungeonRngSetPrimary: Symbol[
        Optional[List[int]],
        None,
    ]

    TrySwitchPlace: Symbol[
        List[int],
        None,
    ]

    RunFractionalTurn: Symbol[
        List[int],
        None,
    ]

    RunLeaderTurn: Symbol[
        Optional[List[int]],
        None,
    ]

    TrySpawnMonsterAndActivatePlusMinus: Symbol[
        List[int],
        None,
    ]

    IsFloorOver: Symbol[
        List[int],
        None,
    ]

    DecrementWindCounter: Symbol[
        Optional[List[int]],
        None,
    ]

    SetForcedLossReason: Symbol[
        Optional[List[int]],
        None,
    ]

    GetForcedLossReason: Symbol[
        Optional[List[int]],
        None,
    ]

    ResetDamageDesc: Symbol[
        List[int],
        None,
    ]

    GetSpriteIndex: Symbol[
        Optional[List[int]],
        None,
    ]

    FloorNumberIsEven: Symbol[
        List[int],
        None,
    ]

    GetKecleonIdToSpawnByFloor: Symbol[
        List[int],
        None,
    ]

    LoadMonsterSprite: Symbol[
        Optional[List[int]],
        None,
    ]

    EuFaintCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    HandleFaint: Symbol[
        Optional[List[int]],
        None,
    ]

    TryActivateSlowStart: Symbol[
        List[int],
        None,
    ]

    TryActivateArtificialWeatherAbilities: Symbol[
        List[int],
        None,
    ]

    DefenderAbilityIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    IsMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    TryActivateTruant: Symbol[
        List[int],
        None,
    ]

    RestorePpAllMovesSetFlags: Symbol[
        Optional[List[int]],
        None,
    ]

    MewSpawnCheck: Symbol[
        List[int],
        None,
    ]

    ExclusiveItemEffectIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTeamMemberWithIqSkill: Symbol[
        List[int],
        None,
    ]

    TeamMemberHasEnabledIqSkill: Symbol[
        List[int],
        None,
    ]

    TeamLeaderIqSkillIsEnabled: Symbol[
        List[int],
        None,
    ]

    HasLowHealth: Symbol[
        List[int],
        None,
    ]

    IsSpecialStoryAlly: Symbol[
        List[int],
        None,
    ]

    IsExperienceLocked: Symbol[
        List[int],
        None,
    ]

    InitTeam: Symbol[
        Optional[List[int]],
        None,
    ]

    SpawnMonster: Symbol[
        List[int],
        None,
    ]

    InitTeamMember: Symbol[
        Optional[List[int]],
        None,
    ]

    ExecuteMonsterAction: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcSpeedStage: Symbol[
        List[int],
        None,
    ]

    CalcSpeedStageWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNumberOfAttacks: Symbol[
        List[int],
        None,
    ]

    SprintfStatic: Symbol[
        List[int],
        None,
    ]

    NoGastroAcidStatus: Symbol[
        List[int],
        None,
    ]

    AbilityIsActive: Symbol[
        List[int],
        None,
    ]

    LevitateIsActive: Symbol[
        List[int],
        None,
    ]

    MonsterIsType: Symbol[
        List[int],
        None,
    ]

    IqSkillIsEnabled: Symbol[
        List[int],
        None,
    ]

    GetMoveTypeForMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMovePower: Symbol[
        List[int],
        None,
    ]

    AddExpSpecial: Symbol[
        List[int],
        None,
    ]

    EnemyEvolution: Symbol[
        Optional[List[int]],
        None,
    ]

    EvolveMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSleepAnimationId: Symbol[
        List[int],
        None,
    ]

    DisplayActions: Symbol[
        Optional[List[int]],
        None,
    ]

    EndFrozenClassStatus: Symbol[
        List[int],
        None,
    ]

    EndCringeClassStatus: Symbol[
        List[int],
        None,
    ]

    ApplyDamage: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTypeMatchup: Symbol[
        List[int],
        None,
    ]

    CalcDamage: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcRecoilDamageFixed: Symbol[
        List[int],
        None,
    ]

    CalcDamageFixed: Symbol[
        List[int],
        None,
    ]

    CalcDamageFixedNoCategory: Symbol[
        List[int],
        None,
    ]

    CalcDamageFixedWrapper: Symbol[
        List[int],
        None,
    ]

    ResetDamageCalcScratchSpace: Symbol[
        List[int],
        None,
    ]

    TrySpawnMonsterAndTickSpawnCounter: Symbol[
        List[int],
        None,
    ]

    AuraBowIsActive: Symbol[
        List[int],
        None,
    ]

    ExclusiveItemOffenseBoost: Symbol[
        Optional[List[int]],
        None,
    ]

    ExclusiveItemDefenseBoost: Symbol[
        Optional[List[int]],
        None,
    ]

    TickNoSlipCap: Symbol[
        List[int],
        None,
    ]

    TickStatusAndHealthRegen: Symbol[
        List[int],
        None,
    ]

    InflictSleepStatusSingle: Symbol[
        List[int],
        None,
    ]

    TryInflictSleepStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictNightmareStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictNappingStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictYawningStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictSleeplessStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictPausedStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictInfatuatedStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictBurnStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictBurnStatusWholeTeam: Symbol[
        List[int],
        None,
    ]

    TryInflictPoisonedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictBadlyPoisonedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictFrozenStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictConstrictionStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictShadowHoldStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictIngrainStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictWrappedStatus: Symbol[
        List[int],
        None,
    ]

    FreeOtherWrappedMonsters: Symbol[
        List[int],
        None,
    ]

    TryInflictPetrifiedStatus: Symbol[
        List[int],
        None,
    ]

    LowerOffensiveStat: Symbol[
        Optional[List[int]],
        None,
    ]

    LowerDefensiveStat: Symbol[
        List[int],
        None,
    ]

    BoostOffensiveStat: Symbol[
        List[int],
        None,
    ]

    BoostDefensiveStat: Symbol[
        List[int],
        None,
    ]

    ApplyOffensiveStatMultiplier: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyDefensiveStatMultiplier: Symbol[
        List[int],
        None,
    ]

    BoostHitChanceStat: Symbol[
        List[int],
        None,
    ]

    LowerHitChanceStat: Symbol[
        List[int],
        None,
    ]

    TryInflictCringeStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictParalysisStatus: Symbol[
        List[int],
        None,
    ]

    BoostSpeed: Symbol[
        List[int],
        None,
    ]

    BoostSpeedOneStage: Symbol[
        List[int],
        None,
    ]

    LowerSpeed: Symbol[
        List[int],
        None,
    ]

    TrySealMove: Symbol[
        List[int],
        None,
    ]

    BoostOrLowerSpeed: Symbol[
        List[int],
        None,
    ]

    ResetHitChanceStat: Symbol[
        List[int],
        None,
    ]

    TryActivateQuickFeet: Symbol[
        List[int],
        None,
    ]

    TryInflictConfusedStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictCoweringStatus: Symbol[
        List[int],
        None,
    ]

    TryIncreaseHp: Symbol[
        List[int],
        None,
    ]

    TryInflictLeechSeedStatus: Symbol[
        List[int],
        None,
    ]

    TryInflictDestinyBond: Symbol[
        List[int],
        None,
    ]

    IsBlinded: Symbol[
        List[int],
        None,
    ]

    RestoreMovePP: Symbol[
        List[int],
        None,
    ]

    SetReflectDamageCountdownTo4: Symbol[
        List[int],
        None,
    ]

    HasConditionalGroundImmunity: Symbol[
        List[int],
        None,
    ]

    Conversion2IsActive: Symbol[
        List[int],
        None,
    ]

    IsTargetInRange: Symbol[
        List[int],
        None,
    ]

    GetEntityMoveTargetAndRange: Symbol[
        List[int],
        None,
    ]

    ApplyItemEffect: Symbol[
        List[int],
        None,
    ]

    ViolentSeedBoost: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyGummiBoostsDungeonMode: Symbol[
        List[int],
        None,
    ]

    GetMaxPpWrapper: Symbol[
        List[int],
        None,
    ]

    MoveIsNotPhysical: Symbol[
        List[int],
        None,
    ]

    TryPounce: Symbol[
        List[int],
        None,
    ]

    TryBlowAway: Symbol[
        List[int],
        None,
    ]

    TryWarp: Symbol[
        List[int],
        None,
    ]

    MoveHitCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRandOutcomeUserTargetInteraction: Symbol[
        List[int],
        None,
    ]

    DungeonRandOutcomeUserAction: Symbol[
        List[int],
        None,
    ]

    UpdateMovePp: Symbol[
        List[int],
        None,
    ]

    LowerSshort: Symbol[
        List[int],
        None,
    ]

    DealDamageWithRecoil: Symbol[
        List[int],
        None,
    ]

    ExecuteMoveEffect: Symbol[
        Optional[List[int]],
        None,
    ]

    DealDamage: Symbol[
        List[int],
        None,
    ]

    CalcDamageProjectile: Symbol[
        List[int],
        None,
    ]

    CalcDamageFinal: Symbol[
        Optional[List[int]],
        None,
    ]

    GetApparentWeather: Symbol[
        List[int],
        None,
    ]

    TryWeatherFormChange: Symbol[
        List[int],
        None,
    ]

    GetTile: Symbol[
        List[int],
        None,
    ]

    GetTileSafe: Symbol[
        List[int],
        None,
    ]

    GravityIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSecretBazaar: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSecretRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSecretFloor: Symbol[
        List[int],
        None,
    ]

    GetDungeonGenInfoUnk0C: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMinimapData: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMinimapDataE447: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMinimapDataE447: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMinimapDataE448: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadFixedRoomDataVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    IsNormalFloor: Symbol[
        List[int],
        None,
    ]

    GenerateFloor: Symbol[
        List[int],
        None,
    ]

    GetTileTerrain: Symbol[
        List[int],
        None,
    ]

    DungeonRand100: Symbol[
        List[int],
        None,
    ]

    FlagHallwayJunctions: Symbol[
        List[int],
        None,
    ]

    GenerateStandardFloor: Symbol[
        List[int],
        None,
    ]

    GenerateOuterRingFloor: Symbol[
        List[int],
        None,
    ]

    GenerateCrossroadsFloor: Symbol[
        List[int],
        None,
    ]

    GenerateLineFloor: Symbol[
        List[int],
        None,
    ]

    GenerateCrossFloor: Symbol[
        List[int],
        None,
    ]

    GenerateBeetleFloor: Symbol[
        List[int],
        None,
    ]

    MergeRoomsVertically: Symbol[
        List[int],
        None,
    ]

    GenerateOuterRoomsFloor: Symbol[
        List[int],
        None,
    ]

    IsNotFullFloorFixedRoom: Symbol[
        List[int],
        None,
    ]

    GenerateFixedRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateOneRoomMonsterHouseFloor: Symbol[
        List[int],
        None,
    ]

    GenerateTwoRoomsWithMonsterHouseFloor: Symbol[
        List[int],
        None,
    ]

    GenerateExtraHallways: Symbol[
        List[int],
        None,
    ]

    GetGridPositions: Symbol[
        List[int],
        None,
    ]

    InitDungeonGrid: Symbol[
        List[int],
        None,
    ]

    AssignRooms: Symbol[
        List[int],
        None,
    ]

    CreateRoomsAndAnchors: Symbol[
        List[int],
        None,
    ]

    GenerateSecondaryStructures: Symbol[
        List[int],
        None,
    ]

    AssignGridCellConnections: Symbol[
        List[int],
        None,
    ]

    CreateGridCellConnections: Symbol[
        List[int],
        None,
    ]

    GenerateRoomImperfections: Symbol[
        List[int],
        None,
    ]

    CreateHallway: Symbol[
        List[int],
        None,
    ]

    EnsureConnectedGrid: Symbol[
        List[int],
        None,
    ]

    SetTerrainObstacleChecked: Symbol[
        List[int],
        None,
    ]

    FinalizeJunctions: Symbol[
        List[int],
        None,
    ]

    GenerateKecleonShop: Symbol[
        List[int],
        None,
    ]

    GenerateMonsterHouse: Symbol[
        List[int],
        None,
    ]

    GenerateMazeRoom: Symbol[
        List[int],
        None,
    ]

    GenerateMaze: Symbol[
        List[int],
        None,
    ]

    GenerateMazeLine: Symbol[
        List[int],
        None,
    ]

    SetSpawnFlag5: Symbol[
        List[int],
        None,
    ]

    IsNextToHallway: Symbol[
        List[int],
        None,
    ]

    ResolveInvalidSpawns: Symbol[
        List[int],
        None,
    ]

    ConvertSecondaryTerrainToChasms: Symbol[
        List[int],
        None,
    ]

    EnsureImpassableTilesAreWalls: Symbol[
        List[int],
        None,
    ]

    InitializeTile: Symbol[
        List[int],
        None,
    ]

    ResetFloor: Symbol[
        List[int],
        None,
    ]

    PosIsOutOfBounds: Symbol[
        List[int],
        None,
    ]

    ShuffleSpawnPositions: Symbol[
        List[int],
        None,
    ]

    SpawnNonEnemies: Symbol[
        List[int],
        None,
    ]

    SpawnEnemies: Symbol[
        List[int],
        None,
    ]

    SetSecondaryTerrainOnWall: Symbol[
        List[int],
        None,
    ]

    GenerateSecondaryTerrainFormations: Symbol[
        List[int],
        None,
    ]

    StairsAlwaysReachable: Symbol[
        List[int],
        None,
    ]

    ConvertWallsToChasms: Symbol[
        List[int],
        None,
    ]

    ResetInnerBoundaryTileRows: Symbol[
        List[int],
        None,
    ]

    SpawnStairs: Symbol[
        List[int],
        None,
    ]

    LoadFixedRoomData: Symbol[
        List[int],
        None,
    ]

    IsHiddenStairsFloor: Symbol[
        List[int],
        None,
    ]

    HasHeldItem: Symbol[
        List[int],
        None,
    ]

    IsOutlawOrChallengeRequestFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    IsCurrentMissionType: Symbol[
        List[int],
        None,
    ]

    IsCurrentMissionTypeExact: Symbol[
        List[int],
        None,
    ]

    IsOutlawMonsterHouseFloor: Symbol[
        List[int],
        None,
    ]

    IsGoldenChamber: Symbol[
        List[int],
        None,
    ]

    IsLegendaryChallengeFloor: Symbol[
        List[int],
        None,
    ]

    IsJirachiChallengeFloor: Symbol[
        List[int],
        None,
    ]

    IsDestinationFloorWithMonster: Symbol[
        List[int],
        None,
    ]

    MissionTargetEnemyIsDefeated: Symbol[
        List[int],
        None,
    ]

    SetMissionTargetEnemyDefeated: Symbol[
        List[int],
        None,
    ]

    IsDestinationFloorWithFixedRoom: Symbol[
        List[int],
        None,
    ]

    GetItemToRetrieve: Symbol[
        List[int],
        None,
    ]

    GetItemToDeliver: Symbol[
        List[int],
        None,
    ]

    GetSpecialTargetItem: Symbol[
        List[int],
        None,
    ]

    IsDestinationFloorWithItem: Symbol[
        List[int],
        None,
    ]

    IsDestinationFloorWithHiddenOutlaw: Symbol[
        List[int],
        None,
    ]

    IsDestinationFloorWithFleeingOutlaw: Symbol[
        List[int],
        None,
    ]

    GetMissionTargetEnemy: Symbol[
        List[int],
        None,
    ]

    GetMissionEnemyMinionGroup: Symbol[
        List[int],
        None,
    ]

    FloorHasMissionMonster: Symbol[
        List[int],
        None,
    ]

    LogMessageByIdWithPopupCheckUser: Symbol[
        List[int],
        None,
    ]

    LogMessageWithPopupCheckUser: Symbol[
        List[int],
        None,
    ]

    LogMessageByIdQuiet: Symbol[
        List[int],
        None,
    ]

    LogMessageQuiet: Symbol[
        List[int],
        None,
    ]

    LogMessageByIdWithPopupCheckUserTarget: Symbol[
        List[int],
        None,
    ]

    LogMessageWithPopupCheckUserTarget: Symbol[
        List[int],
        None,
    ]

    LogMessageByIdQuietCheckUserTarget: Symbol[
        List[int],
        None,
    ]

    LogMessageByIdWithPopupCheckUserUnknown: Symbol[
        List[int],
        None,
    ]

    LogMessageByIdWithPopup: Symbol[
        List[int],
        None,
    ]

    LogMessageWithPopup: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessage: Symbol[
        List[int],
        None,
    ]

    LogMessageById: Symbol[
        List[int],
        None,
    ]

    OpenMessageLog: Symbol[
        Optional[List[int]],
        None,
    ]

    RunDungeonMode: Symbol[
        List[int],
        None,
    ]

    DisplayDungeonTip: Symbol[
        Optional[List[int]],
        None,
    ]

    SetBothScreensWindowColorToDefault: Symbol[
        List[int],
        None,
    ]

    DisplayMessage: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayMessage2: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayMessageInternal: Symbol[
        Optional[List[int]],
        None,
    ]


class Overlay29DataProtocol(Protocol):

    DUNGEON_STRUCT_SIZE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFSET_OF_DUNGEON_FLOOR_PROPERTIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_RAND_MAX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_LCG_MULTIPLIER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_LCG_INCREMENT_SECONDARY: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_MALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MSG_ID_SLOW_START: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXPERIENCE_POINT_GAIN_CAP: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    JUDGMENT_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    REGULAR_ATTACK_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEOXYS_ATTACK_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEOXYS_SPEED_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GIRATINA_ALTERED_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PUNISHMENT_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFENSE_STAT_MAX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PROJECTILE_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BELLY_LOST_PER_TURN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_HP_CAP: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVE_TARGET_AND_RANGE_SPECIAL_USER_HEALING: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PLAIN_SEED_VALUE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_ELIXIR_PP_RESTORATION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SLIP_SEED_VALUE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CASTFORM_NORMAL_FORM_MALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CASTFORM_NORMAL_FORM_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CHERRIM_SUNSHINE_FORM_MALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CHERRIM_OVERCAST_FORM_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CHERRIM_SUNSHINE_FORM_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FLOOR_GENERATION_STATUS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFSET_OF_DUNGEON_N_NORMAL_ITEM_SPAWNS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_GRID_COLUMN_BYTES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_MAX_POSITION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFSET_OF_DUNGEON_GUARANTEED_ITEM_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_TILE_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_REVISIT_OVERRIDES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_MONSTER_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_ITEM_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_ENTITY_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DIRECTIONS_XY: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FRACTIONAL_TURN_SEQUENCE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BELLY_DRAIN_IN_WALLS_INT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BELLY_DRAIN_IN_WALLS_THOUSANDTHS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPATK_STAT_IDX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ATK_STAT_IDX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CORNER_CARDINAL_NEIGHBOR_IS_OPEN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PTR_MASTER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEADER_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_STATE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_STATE_SECONDARY_VALUES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_WEATHER_ATK_SPEED_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_WEATHER_MOVE_SPEED_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_WEATHER_NO_STATUS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_EVASION_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_TILE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_DATA_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    NECTAR_IQ_BOOST: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay29Protocol = SectionProtocol[
    Overlay29FunctionsProtocol,
    Overlay29DataProtocol,
    int,
]


class Overlay0FunctionsProtocol(Protocol):

    pass


class Overlay0DataProtocol(Protocol):

    TOP_MENU_MUSIC_ID: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay0Protocol = SectionProtocol[
    Overlay0FunctionsProtocol,
    Overlay0DataProtocol,
    int,
]


class Overlay20FunctionsProtocol(Protocol):

    pass


class Overlay20DataProtocol(Protocol):

    RECYCLE_MENU_CONFIRM_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MENU_CONFIRM_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MAIN_MENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay20Protocol = SectionProtocol[
    Overlay20FunctionsProtocol,
    Overlay20DataProtocol,
    int,
]


class Overlay13FunctionsProtocol(Protocol):

    pass


class Overlay13DataProtocol(Protocol):

    STARTERS_PARTNER_IDS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STARTERS_HERO_IDS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STARTERS_STRINGS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    QUIZ_QUESTION_STRINGS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    QUIZ_ANSWER_STRINGS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    UNKNOWN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay13Protocol = SectionProtocol[
    Overlay13FunctionsProtocol,
    Overlay13DataProtocol,
    int,
]


class Overlay11FunctionsProtocol(Protocol):

    FuncThatCallsCommandParsing: Symbol[
        List[int],
        None,
    ]

    ScriptCommandParsing: Symbol[
        List[int],
        None,
    ]

    SsbLoad2: Symbol[
        List[int],
        None,
    ]

    StationLoadHanger: Symbol[
        List[int],
        None,
    ]

    ScriptStationLoadTalk: Symbol[
        List[int],
        None,
    ]

    SsbLoad1: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcessCall: Symbol[
        List[int],
        None,
    ]

    GetSpecialRecruitmentSpecies: Symbol[
        List[int],
        None,
    ]

    PrepareMenuAcceptTeamMember: Symbol[
        List[int],
        None,
    ]

    InitRandomNpcJobs: Symbol[
        List[int],
        None,
    ]

    GetRandomNpcJobType: Symbol[
        List[int],
        None,
    ]

    GetRandomNpcJobSubtype: Symbol[
        List[int],
        None,
    ]

    GetRandomNpcJobStillAvailable: Symbol[
        List[int],
        None,
    ]

    AcceptRandomNpcJob: Symbol[
        List[int],
        None,
    ]

    GroundMainLoop: Symbol[
        List[int],
        None,
    ]

    GetAllocArenaGround: Symbol[
        List[int],
        None,
    ]

    GetFreeArenaGround: Symbol[
        List[int],
        None,
    ]

    GroundMainReturnDungeon: Symbol[
        List[int],
        None,
    ]

    GroundMainNextDay: Symbol[
        List[int],
        None,
    ]

    JumpToTitleScreen: Symbol[
        List[int],
        None,
    ]

    ReturnToTitleScreen: Symbol[
        List[int],
        None,
    ]

    ScriptSpecialProcess0x16: Symbol[
        List[int],
        None,
    ]

    SprintfStatic: Symbol[
        List[int],
        None,
    ]

    StatusUpdate: Symbol[
        List[int],
        None,
    ]


class Overlay11DataProtocol(Protocol):

    SCRIPT_OP_CODES: Symbol[
        List[int],
        int,
    ]

    C_ROUTINES: Symbol[
        List[int],
        Optional[int],
    ]

    OBJECTS: Symbol[
        List[int],
        int,
    ]

    RECRUITMENT_TABLE_LOCATIONS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECRUITMENT_TABLE_LEVELS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECRUITMENT_TABLE_SPECIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEVEL_TILEMAP_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OVERLAY11_OVERLAY_LOAD_TABLE: Symbol[
        Optional[List[int]],
        None,
    ]

    UNIONALL_RAM_ADDRESS: Symbol[
        Optional[List[int]],
        None,
    ]

    GROUND_STATE_MAP: Symbol[
        Optional[List[int]],
        None,
    ]

    GROUND_STATE_PTRS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay11Protocol = SectionProtocol[
    Overlay11FunctionsProtocol,
    Overlay11DataProtocol,
    int,
]


class Overlay28FunctionsProtocol(Protocol):

    pass


class Overlay28DataProtocol(Protocol):

    pass


Overlay28Protocol = SectionProtocol[
    Overlay28FunctionsProtocol,
    Overlay28DataProtocol,
    int,
]


class Overlay25FunctionsProtocol(Protocol):

    pass


class Overlay25DataProtocol(Protocol):

    APPRAISAL_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    APPRAISAL_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    APPRAISAL_SUBMENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay25Protocol = SectionProtocol[
    Overlay25FunctionsProtocol,
    Overlay25DataProtocol,
    int,
]


class Overlay4FunctionsProtocol(Protocol):

    pass


class Overlay4DataProtocol(Protocol):

    pass


Overlay4Protocol = SectionProtocol[
    Overlay4FunctionsProtocol,
    Overlay4DataProtocol,
    int,
]


class Overlay7FunctionsProtocol(Protocol):

    pass


class Overlay7DataProtocol(Protocol):

    pass


Overlay7Protocol = SectionProtocol[
    Overlay7FunctionsProtocol,
    Overlay7DataProtocol,
    int,
]


class Overlay1FunctionsProtocol(Protocol):

    pass


class Overlay1DataProtocol(Protocol):

    CONTINUE_CHOICE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SUBMENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_DEBUG_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_DEBUG_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay1Protocol = SectionProtocol[
    Overlay1FunctionsProtocol,
    Overlay1DataProtocol,
    int,
]


class Overlay6FunctionsProtocol(Protocol):

    pass


class Overlay6DataProtocol(Protocol):

    pass


Overlay6Protocol = SectionProtocol[
    Overlay6FunctionsProtocol,
    Overlay6DataProtocol,
    int,
]


class Overlay18FunctionsProtocol(Protocol):

    pass


class Overlay18DataProtocol(Protocol):

    MOVES_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_5: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_6: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_7: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay18Protocol = SectionProtocol[
    Overlay18FunctionsProtocol,
    Overlay18DataProtocol,
    int,
]


class Overlay2FunctionsProtocol(Protocol):

    pass


class Overlay2DataProtocol(Protocol):

    pass


Overlay2Protocol = SectionProtocol[
    Overlay2FunctionsProtocol,
    Overlay2DataProtocol,
    int,
]


class Overlay12FunctionsProtocol(Protocol):

    pass


class Overlay12DataProtocol(Protocol):

    pass


Overlay12Protocol = SectionProtocol[
    Overlay12FunctionsProtocol,
    Overlay12DataProtocol,
    int,
]


class Overlay22FunctionsProtocol(Protocol):

    pass


class Overlay22DataProtocol(Protocol):

    SHOP_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SHOP_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SHOP_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SHOP_MAIN_MENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay22Protocol = SectionProtocol[
    Overlay22FunctionsProtocol,
    Overlay22DataProtocol,
    int,
]


class Overlay10FunctionsProtocol(Protocol):

    SprintfStatic: Symbol[
        Optional[List[int]],
        None,
    ]


class Overlay10DataProtocol(Protocol):

    FIRST_DUNGEON_WITH_MONSTER_HOUSE_TRAPS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAD_POISON_DAMAGE_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PROTEIN_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_CAP_NO_MONSTER_HOUSE: Symbol[
        Optional[List[int]],
        None,
    ]

    OREN_BERRY_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SITRUS_BERRY_HP_RESTORATION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXP_ELITE_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_HOUSE_MAX_NON_MONSTER_SPAWNS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GOLD_THORN_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ORAN_BERRY_FULL_HP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LIFE_SEED_HP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    INTIMIDATOR_ACTIVATION_CHANCE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ORAN_BERRY_HP_RESTORATION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SITRUS_BERRY_FULL_HP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BURN_DAMAGE_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STICK_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_COOLDOWN_THIEF_ALERT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_HOUSE_MAX_MONSTER_SPAWNS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPEED_BOOST_TURNS: Symbol[
        Optional[List[int]],
        None,
    ]

    MIRACLE_CHEST_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    WONDER_CHEST_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_CAP_WITH_MONSTER_HOUSE: Symbol[
        Optional[List[int]],
        None,
    ]

    POISON_DAMAGE_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GEO_PEBBLE_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GRAVELEROCK_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RARE_FOSSIL_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GINSENG_CHANCE_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ZINC_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IRON_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CALCIUM_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CORSOLA_TWIG_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CACNEA_SPIKE_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GOLD_FANG_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SILVER_SPIKE_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IRON_THORN_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SLEEP_DURATION_RANGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    POWER_PITCHER_DAMAGE_MULTIPLIER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    AIR_BLADE_DAMAGE_MULTIPLIER: Symbol[
        Optional[List[int]],
        None,
    ]

    SPEED_BOOST_DURATION_RANGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFENSIVE_STAT_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFENSIVE_STAT_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RANDOM_MUSIC_ID_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MALE_ACCURACY_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MALE_EVASION_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FEMALE_ACCURACY_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FEMALE_EVASION_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MUSIC_ID_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TYPE_MATCHUP_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_MONSTER_SPAWN_STATS_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TILESET_PROPERTIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_PROPERTIES_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVE_ANIMATION_INFO: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay10Protocol = SectionProtocol[
    Overlay10FunctionsProtocol,
    Overlay10DataProtocol,
    int,
]


class Overlay34FunctionsProtocol(Protocol):

    pass


class Overlay34DataProtocol(Protocol):

    UNKNOWN_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_DEBUG_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay34Protocol = SectionProtocol[
    Overlay34FunctionsProtocol,
    Overlay34DataProtocol,
    int,
]


class Overlay3FunctionsProtocol(Protocol):

    pass


class Overlay3DataProtocol(Protocol):

    pass


Overlay3Protocol = SectionProtocol[
    Overlay3FunctionsProtocol,
    Overlay3DataProtocol,
    int,
]


class Overlay8FunctionsProtocol(Protocol):

    pass


class Overlay8DataProtocol(Protocol):

    pass


Overlay8Protocol = SectionProtocol[
    Overlay8FunctionsProtocol,
    Overlay8DataProtocol,
    int,
]


class Overlay30FunctionsProtocol(Protocol):

    pass


class Overlay30DataProtocol(Protocol):

    pass


Overlay30Protocol = SectionProtocol[
    Overlay30FunctionsProtocol,
    Overlay30DataProtocol,
    int,
]


class Overlay31FunctionsProtocol(Protocol):

    pass


class Overlay31DataProtocol(Protocol):

    DUNGEON_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_5: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_6: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay31Protocol = SectionProtocol[
    Overlay31FunctionsProtocol,
    Overlay31DataProtocol,
    int,
]


class Overlay16FunctionsProtocol(Protocol):

    pass


class Overlay16DataProtocol(Protocol):

    EVO_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EVO_SUBMENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EVO_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay16Protocol = SectionProtocol[
    Overlay16FunctionsProtocol,
    Overlay16DataProtocol,
    int,
]


class Overlay19FunctionsProtocol(Protocol):

    pass


class Overlay19DataProtocol(Protocol):

    BAR_MENU_CONFIRM_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_MENU_CONFIRM_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay19Protocol = SectionProtocol[
    Overlay19FunctionsProtocol,
    Overlay19DataProtocol,
    int,
]


class Overlay23FunctionsProtocol(Protocol):

    pass


class Overlay23DataProtocol(Protocol):

    STORAGE_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay23Protocol = SectionProtocol[
    Overlay23FunctionsProtocol,
    Overlay23DataProtocol,
    int,
]


class Overlay24FunctionsProtocol(Protocol):

    pass


class Overlay24DataProtocol(Protocol):

    DAYCARE_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DAYCARE_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay24Protocol = SectionProtocol[
    Overlay24FunctionsProtocol,
    Overlay24DataProtocol,
    int,
]


class Overlay26FunctionsProtocol(Protocol):

    pass


class Overlay26DataProtocol(Protocol):

    pass


Overlay26Protocol = SectionProtocol[
    Overlay26FunctionsProtocol,
    Overlay26DataProtocol,
    int,
]


class Overlay33FunctionsProtocol(Protocol):

    pass


class Overlay33DataProtocol(Protocol):

    pass


Overlay33Protocol = SectionProtocol[
    Overlay33FunctionsProtocol,
    Overlay33DataProtocol,
    int,
]


class Overlay35FunctionsProtocol(Protocol):

    pass


class Overlay35DataProtocol(Protocol):

    pass


Overlay35Protocol = SectionProtocol[
    Overlay35FunctionsProtocol,
    Overlay35DataProtocol,
    int,
]


class RamFunctionsProtocol(Protocol):

    pass


class RamDataProtocol(Protocol):

    DUNGEON_COLORMAP_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_STRUCT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVE_DATA_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FRAMES_SINCE_LAUNCH: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_ITEMS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_ITEM_QUANTITIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_SHOP_ITEMS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_SHOP_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    UNUSED_KECLEON_SHOP_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_WARES_ITEMS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_WARES_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    UNUSED_KECLEON_WARES_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONEY_CARRIED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONEY_STORED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LAST_NEW_MOVE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS_VALUES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_LEVEL: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEBUG_SPECIAL_EPISODE_NUMBER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PENDING_DUNGEON_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PENDING_STARTING_FLOOR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PLAY_TIME_SECONDS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PLAY_TIME_FRAME_COUNTER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TEAM_NAME: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    HERO_SPECIES_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    HERO_NICKNAME: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PARTNER_SPECIES_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEADER_IQ_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEADER_NICKNAME: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PARTY_MEMBER_2_IQ_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FRAMES_SINCE_LAUNCH_TIMES_THREE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TURNING_ON_THE_SPOT_FLAG: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FLOOR_GENERATION_STATUS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


RamProtocol = SectionProtocol[
    RamFunctionsProtocol,
    RamDataProtocol,
    int,
]


class AllSymbolsProtocol(Protocol):

    arm9: Arm9Protocol

    overlay5: Overlay5Protocol

    overlay14: Overlay14Protocol

    overlay27: Overlay27Protocol

    overlay9: Overlay9Protocol

    overlay32: Overlay32Protocol

    overlay17: Overlay17Protocol

    overlay21: Overlay21Protocol

    overlay15: Overlay15Protocol

    overlay29: Overlay29Protocol

    overlay0: Overlay0Protocol

    overlay20: Overlay20Protocol

    overlay13: Overlay13Protocol

    overlay11: Overlay11Protocol

    overlay28: Overlay28Protocol

    overlay25: Overlay25Protocol

    overlay4: Overlay4Protocol

    overlay7: Overlay7Protocol

    overlay1: Overlay1Protocol

    overlay6: Overlay6Protocol

    overlay18: Overlay18Protocol

    overlay2: Overlay2Protocol

    overlay12: Overlay12Protocol

    overlay22: Overlay22Protocol

    overlay10: Overlay10Protocol

    overlay34: Overlay34Protocol

    overlay3: Overlay3Protocol

    overlay8: Overlay8Protocol

    overlay30: Overlay30Protocol

    overlay31: Overlay31Protocol

    overlay16: Overlay16Protocol

    overlay19: Overlay19Protocol

    overlay23: Overlay23Protocol

    overlay24: Overlay24Protocol

    overlay26: Overlay26Protocol

    overlay33: Overlay33Protocol

    overlay35: Overlay35Protocol

    ram: RamProtocol
