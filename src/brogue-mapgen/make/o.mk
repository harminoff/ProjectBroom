$(sort $(sources:.c=.o) $(bridge_sources:.c=.o)): %.o: %.c src/brogue/Rogue.h src/brogue/Globals.h src/brogue/GlobalsBase.h src/brogue/BrogueBridge.h src/brogue/BrogueBridgeInternal.h vars/cppflags vars/cflags make/o.mk
	$(CC) $(cppflags) $(cflags) -c $< -o $@

src/variants/GlobalsBrogue.o src/variants/GlobalsRapidBrogue.o src/variants/GlobalsBulletBrogue.o: vars/extra_version
src/variants/GlobalsBrogue.o src/variants/GlobalsRapidBrogue.o src/variants/GlobalsBulletBrogue.o: cppflags += -DBROGUE_EXTRA_VERSION='"$(extra_version)"'

src/brogue/Recordings.o: src/brogue/RecordingIO.h
src/brogue/BrogueBridge.o: src/brogue/BridgePersistence.h
src/brogue/Items.o src/brogue/ItemCommandFrame.o tools/bridge-main.o: src/brogue/ItemCommandFrame.h
