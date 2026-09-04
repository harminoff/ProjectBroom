ifeq ($(BRIDGE),YES)
bin/brogue-bridge bin/brogue-bridge.exe: $(bridge_objects) vars/cflags vars/LDFLAGS vars/libs make/bridge.mk
	$(CC) $(cflags) $(LDFLAGS) -Wl,--stack,8388608 -o $@ $(bridge_objects) $(libs)

bin/brogue-bridge.dll: $(bridge_dll_objects) tools/brogue-bridge.def vars/cflags vars/LDFLAGS vars/libs make/bridge.mk
	$(CC) $(cflags) $(LDFLAGS) -shared -Wl,--out-implib=bin/brogue-bridge.dll.a -o $@ $(bridge_dll_objects) tools/brogue-bridge.def $(libs)

tools/bridge-main.dll.o: tools/bridge-main.c src/brogue/Rogue.h src/brogue/Globals.h src/brogue/GlobalsBase.h vars/cppflags vars/cflags make/bridge.mk
	$(CC) $(cppflags) $(cflags) -DBROGUE_BRIDGE_DLL -c $< -o $@
endif
