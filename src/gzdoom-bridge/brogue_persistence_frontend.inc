// Native suspend/resume UI and regenerable map projection. Included in the
// frontend namespace after input/presentation helpers have been declared.
namespace fs = std::filesystem;
std::string Utf8Path(const fs::path &path) {
    auto text = path.u8string();
    return std::string(reinterpret_cast<const char *>(text.data()), text.size());
}

bool Persist(BrogueBridgePersistenceOperation op, const std::string &path = "", bool consume = false)
{
    BrogueBridgePersistenceRequest request{};
    request.apiVersion = BROGUE_BRIDGE_API_VERSION;
    request.operation = op;
    request.expectedRevision = Persistence.revision;
    request.expectedSession = Persistence.session;
    request.consumeSource = consume;
    if (path.size() >= sizeof(request.path)) return false;
    memcpy(request.path, path.c_str(), path.size() + 1);
    return Api.persistence(&request, &Persistence) == BROGUE_BRIDGE_OK;
}

fs::path SaveRoot()
{
    const char *overrideRoot = brg_save_root;
    if (overrideRoot && *overrideRoot) return fs::u8path(overrideRoot);
    wchar_t path[32768];
    DWORD count = GetEnvironmentVariableW(L"LOCALAPPDATA", path, 32768);
    if (!count || count >= 32768) throw std::runtime_error("Local application data is unavailable");
    return fs::path(path) / "ProjectBroom";
}

std::string UniqueRunName()
{
    static unsigned int serial = 0;
    return std::to_string(GetCurrentProcessId()) + "-" + std::to_string(GetTickCount64()) + "-" + std::to_string(++serial);
}

fs::path LatestSave()
{
    fs::path latest;
    fs::path folder = SaveRoot() / "saves";
    if (!fs::exists(folder)) return latest;
    for (const auto &entry : fs::directory_iterator(folder)) {
        if (!entry.is_regular_file() || entry.path().extension() != ".broguesave") continue;
        if (latest.empty() || entry.last_write_time() > fs::last_write_time(latest)) latest = entry.path();
    }
    return latest;
}

bool ConfigureWorkingRecording()
{
    try {
        fs::path folder = SaveRoot() / "working";
        fs::create_directories(folder);
        return Persist(BROGUE_PERSIST_STATUS)
            && Persist(BROGUE_PERSIST_CONFIGURE, Utf8Path(folder / (UniqueRunName() + ".broguesave")));
    } catch (const std::exception &error) {
        Printf("Could not prepare native recording: %s\n", error.what());
        return false;
    }
}

// Windows command-line quoting; never invoke a shell with save/cache paths.
std::wstring ProcessArgument(const std::wstring &value)
{
    std::wstring result = L"\"";
    size_t slashes = 0;
    for (wchar_t c : value) {
        if (c == L'\\') { ++slashes; continue; }
        result.append(slashes * (c == L'"' ? 2 : 1), L'\\');
        if (c == L'"') result += L'\\';
        result += c; slashes = 0;
    }
    result.append(slashes * 2, L'\\');
    return result + L'"';
}

bool PrepareRestoredMap()
{
    try {
        fs::path folder = SaveRoot() / "cache" / "restored" / std::to_string(GetCurrentProcessId());
        fs::create_directories(folder);
        fs::path json = folder / "current.json", wad = folder / "current.wad";
        if (!Persist(BROGUE_PERSIST_STATUS) || !Persist(BROGUE_PERSIST_EXPORT_LEVEL, Utf8Path(json))) return false;
        fs::path compiler = fs::u8path((const char *)brg_map_compiler);
        fs::path root = fs::u8path((const char *)brg_map_compiler_root);
        if (compiler.empty()) { Printf("The runtime map compiler was not configured by the launcher.\n"); return false; }
        std::wstring command = ProcessArgument(compiler.wstring());
        if (!root.empty()) command += L" -m tools.mapcompiler.cli";
        command += L" runtime --input " + ProcessArgument(json.wstring()) + L" --output " + ProcessArgument(wad.wstring());
        STARTUPINFOW startup{}; startup.cb = sizeof(startup);
        PROCESS_INFORMATION process{};
        if (!CreateProcessW(compiler.c_str(), &command[0], nullptr, nullptr, FALSE, CREATE_NO_WINDOW,
                            nullptr, root.empty() ? nullptr : root.c_str(), &startup, &process)) return false;
        // A failed presentation compiler must not strand the authoritative run.
        DWORD waitResult = WaitForSingleObject(process.hProcess, 30000);
        if (waitResult != WAIT_OBJECT_0) {
            TerminateProcess(process.hProcess, 1);
            WaitForSingleObject(process.hProcess, 5000);
            CloseHandle(process.hThread); CloseHandle(process.hProcess);
            Printf("Map reconstruction timed out; the native game is retained.\n");
            return false;
        }
        DWORD status = 1;
        GetExitCodeProcess(process.hProcess, &status);
        CloseHandle(process.hThread); CloseHandle(process.hProcess);
        if (status != 0 || !fs::exists(wad)) return false;
        RestoredMapPath = "file:" + Utf8Path(wad);
        return true;
    } catch (const std::exception &error) {
        Printf("Map reconstruction failed: %s\n", error.what());
        return false;
    }
}

bool SaveAndExit(bool confirm)
{
    if (!Started || State.player.gameHasEnded || FinalizeLoad || LoadingSave) return true;
    CancelSearch(); CloseWeaponUi(); ClearCommandConfirmation();
    PendingActions.clear(); PendingWait = HasBufferedAction = false;
    if (confirm && MessageBoxW(nullptr, L"Save this game and exit?", L"Project Broom",
                              MB_YESNO | MB_ICONQUESTION) != IDYES) return false;
    try {
        fs::path folder = SaveRoot() / "saves";
        fs::create_directories(folder);
        Printf("SAVE_BEGIN turn=%llu depth=%d hash=%016llx\n", (unsigned long long)State.turn, State.depth, (unsigned long long)State.stateHash);
        if (!Persist(BROGUE_PERSIST_STATUS)
            || !Persist(BROGUE_PERSIST_SAVE, Utf8Path(folder / (UniqueRunName() + ".broguesave")))) {
            MessageBoxA(nullptr, Persistence.error, "Save failed - game remains open", MB_OK | MB_ICONERROR);
            return false;
        }
        Api.getState(&State);
        Printf("SAVE_COMPLETE turn=%llu\n", (unsigned long long)State.turn);
        return true;
    } catch (const std::exception &error) {
        MessageBoxA(nullptr, error.what(), "Save failed - game remains open", MB_OK | MB_ICONERROR);
        return false;
    }
}

void BeginLoad(const std::string &source, bool import)
{
    if (Started || LoadingSave) { Printf("Save and exit the current game before loading another.\n"); return; }
    if (!LoadBridge() || Api.initialize() != BROGUE_BRIDGE_OK || !ConfigureWorkingRecording()) return;
    try {
        fs::path path = fs::u8path(source);
        if (!Persist(BROGUE_PERSIST_PROBE, Utf8Path(path))) {
            MessageBoxA(nullptr, Persistence.error, "Cannot load save", MB_OK | MB_ICONERROR); return;
        }
        if (import) {
            fs::path folder = SaveRoot() / "saves";
            fs::create_directories(folder);
            fs::path copy = folder / ("import-" + UniqueRunName() + ".broguesave");
            fs::copy_file(path, copy);
            fs::permissions(copy, fs::perms::owner_write, fs::perm_options::add);
            path = copy;
        }
        if (!Persist(BROGUE_PERSIST_LOAD_BEGIN, Utf8Path(path))) {
            MessageBoxA(nullptr, Persistence.error, "Cannot load save", MB_OK | MB_ICONERROR);
            Persist(BROGUE_PERSIST_LOAD_CANCEL); return;
        }
        M_ClearMenus();
        LoadingSave = true;
        LastLoadTic = -1;
    } catch (const std::exception &error) { Printf("Cannot load save: %s\n", error.what()); }
}

void ConfigureSearchBindings()
{
	// defaultbind deliberately preserves Doom's saved +reload binding. Migrate
	// that obsolete default once, without replacing a customized search binding.
	if (int(brg_search_bindings_version) < 1) {
		const char *binding = Bindings.GetBind("R");
		if (binding && !strcmp(binding, "+reload")
			&& Bindings.GetKeysForCommand("brg_search").Size() == 0) {
			Bindings.DoBind("R", "brg_search");
			Printf(PRINT_NONOTIFY, "Project Broom: migrated R from reload to Search.\n");
		}
		brg_search_bindings_version = 1;
	}
}
