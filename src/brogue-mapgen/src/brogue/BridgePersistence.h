/* Included by the adapter: native recording lifecycle, no serialized snapshots. */
BrogueBridgeResult brogue_bridge_persistence(const BrogueBridgePersistenceRequest *request,
                                             BrogueBridgePersistenceState *out) {
    BrogueBridgeResult result = BROGUE_BRIDGE_OK;
    uint64_t seed = 0;
    unsigned long turns = 0;
    int mode = 0;
    if (!out) return BROGUE_BRIDGE_INVALID_STATE;
    memset(out, 0, sizeof(*out));
    out->apiVersion = BROGUE_BRIDGE_API_VERSION;
    if (!request || request->apiVersion != BROGUE_BRIDGE_API_VERSION
        || !memchr(request->path, 0, sizeof(request->path))) {
        result = BROGUE_BRIDGE_INVALID_STATE;
        goto done;
    }
    if (request->operation != BROGUE_PERSIST_PROBE && request->operation != BROGUE_PERSIST_STATUS
        && (request->expectedRevision != bridgeRevision || request->expectedSession != bridgeSession)) {
        result = BROGUE_BRIDGE_STALE_REVISION;
        goto done;
    }
    switch (request->operation) {
        case BROGUE_PERSIST_STATUS: break;
        case BROGUE_PERSIST_EXPORT_LEVEL:
            if (bridgePhase != BROGUE_SESSION_LIVE && bridgePhase != BROGUE_SESSION_LOAD_READY) {
                result = BROGUE_BRIDGE_INVALID_STATE; break;
            }
            if (exportCurrentLevelJson(request->path, out->error)) result = BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR;
            break;
        case BROGUE_PERSIST_CONFIGURE:
            if (bridgeGameStarted || !request->path[0] || strlen(request->path) >= sizeof(bridgeWorkingPath)) {
                result = BROGUE_BRIDGE_INVALID_STATE; break;
            }
            strcpy(bridgeWorkingPath, request->path);
            ++bridgeRevision;
            break;
        case BROGUE_PERSIST_PROBE:
            if (!bridgeInitialized) brogue_bridge_initialize();
            if (!inspectSavedGame(request->path, &seed, &turns, &mode, out->nativeVersion)) {
                result = BROGUE_BRIDGE_INVALID_STATE; break;
            }
            out->gameSeed = seed; out->totalTurns = turns; out->mode = mode;
            break;
        case BROGUE_PERSIST_SAVE:
            if (bridgePhase != BROGUE_SESSION_LIVE || rogue.gameHasEnded || !currentFilePath[0]) {
                result = BROGUE_BRIDGE_INVALID_STATE; break;
            }
            if (!saveGameToPath(request->path)) { result = BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR; break; }
            finishRepeatedSearch();
            bridgePhase = BROGUE_SESSION_SUSPENDED;
            ++bridgeRevision;
            result = captureState(&bridgeState);
            break;
        case BROGUE_PERSIST_LOAD_BEGIN:
            if (bridgeGameStarted || !bridgeWorkingPath[0]) { result = BROGUE_BRIDGE_INVALID_STATE; break; }
            if (!bridgeInitialized) brogue_bridge_initialize();
            if (!inspectSavedGame(request->path, &seed, &turns, &mode, out->nativeVersion)) {
                result = BROGUE_BRIDGE_INVALID_STATE; break;
            }
            currentConsole = nullConsole;
            serverMode = nonInteractivePlayback = true;
            hasGraphics = false;
            graphicsMode = TEXT_GRAPHICS;
            endConfirmationBroker();
            memset(&bridgeGameResult, 0, sizeof(bridgeGameResult));
            bridgePhase = BROGUE_SESSION_LOADING;
            bridgeGameStarted = true; /* Own allocations even if reconstruction fails. */
            ++bridgeSession; ++bridgeRevision;
            if (!beginSavedGameLoad(request->path)) {
                result = BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR;
                if (!levels) { bridgeGameStarted = false; bridgePhase = BROGUE_SESSION_IDLE; }
            }
            break;
        case BROGUE_PERSIST_LOAD_STEP: {
            if (bridgePhase != BROGUE_SESSION_LOADING) { result = BROGUE_BRIDGE_INVALID_STATE; break; }
            int status = stepSavedGameLoad(32);
            ++bridgeRevision;
            if (status < 0) { result = BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR; break; }
            if (status == 1) {
                bridgePhase = BROGUE_SESSION_LOAD_READY;
                beginIdentityCapture();
                result = captureState(&bridgeState);
                pruneIdentities();
            }
            break;
        }
        case BROGUE_PERSIST_LOAD_FINISH:
            if (bridgePhase != BROGUE_SESSION_LOAD_READY) { result = BROGUE_BRIDGE_INVALID_STATE; break; }
            if (!finishSavedGameLoad(bridgeWorkingPath, request->consumeSource)) {
                result = BROGUE_BRIDGE_INTERNAL_BROGUE_ERROR; break;
            }
            rogue.automationActive = true;
            bridgePhase = BROGUE_SESSION_LIVE;
            ++bridgeRevision;
            result = captureState(&bridgeState);
            break;
        case BROGUE_PERSIST_LOAD_CANCEL:
            if (bridgePhase != BROGUE_SESSION_LOADING && bridgePhase != BROGUE_SESSION_LOAD_READY) {
                result = BROGUE_BRIDGE_INVALID_STATE; break;
            }
            brogue_bridge_shutdown();
            currentFilePath[0] = '\0';
            break;
        default: result = BROGUE_BRIDGE_INVALID_ACTION; break;
    }
done:
    out->phase = bridgePhase;
    out->session = bridgeSession;
    out->revision = bridgeRevision;
    out->errorCode = result;
    if (bridgeGameStarted && request && request->operation != BROGUE_PERSIST_PROBE) {
        out->gameSeed = rogue.seed;
        out->completedTurns = rogue.playerTurnNumber;
        out->totalTurns = rogue.playbackMode ? rogue.howManyTurns : rogue.playerTurnNumber;
        out->mode = rogue.mode;
        copyText(out->nativeVersion, sizeof(out->nativeVersion), rogue.versionString);
    }
    if (result != BROGUE_BRIDGE_OK && !out->error[0]) copyText(out->error, sizeof(out->error),
        recordingLastError()[0] ? recordingLastError() : brogue_bridge_result_name(result));
    return result;
}
