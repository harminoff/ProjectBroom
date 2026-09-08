ifeq ($(BRIDGE),YES)
src/brogue/BrogueBridge.o src/brogue/BrogueBridge.dll.o: src/brogue/BridgeTerrainAppearance.inc
tools/bridge-main.o tools/bridge-main.dll.o: tools/bridge-search-smoke.h tools/bridge-save-smoke.h tools/native-interaction-fixture.h tools/bridge-terrain-smoke.h tools/bridge-bloodwort-smoke.h

bin/brogue-bridge bin/brogue-bridge.exe: $(bridge_objects) vars/cflags vars/LDFLAGS vars/libs make/bridge.mk
	$(CC) $(cflags) $(LDFLAGS) -Wl,--stack,8388608 -o $@ $(bridge_objects) $(libs)

bin/brogue-bridge.dll: $(bridge_dll_objects) tools/brogue-bridge.def vars/cflags vars/LDFLAGS vars/libs make/bridge.mk
	$(CC) $(cflags) $(LDFLAGS) -shared -Wl,--out-implib=bin/brogue-bridge.dll.a -o $@ $(bridge_dll_objects) tools/brogue-bridge.def $(libs)

tools/bridge-main.dll.o: tools/bridge-main.c src/brogue/Rogue.h src/brogue/Globals.h src/brogue/GlobalsBase.h vars/cppflags vars/cflags make/bridge.mk
	$(CC) $(cppflags) $(cflags) -DBROGUE_BRIDGE_DLL -c $< -o $@
endif
