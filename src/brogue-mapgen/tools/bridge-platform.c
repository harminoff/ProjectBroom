/* Platform globals shared by the headless bridge executable and native DLL. */
#include "Rogue.h"
#include "platform.h"

struct brogueConsole currentConsole;
char dataDirectory[BROGUE_FILENAME_MAX] = ".";
boolean serverMode = false;
boolean nonInteractivePlayback = true;
boolean hasGraphics = false;
enum graphicsModes graphicsMode = TEXT_GRAPHICS;
boolean isCsvFormat = false;
