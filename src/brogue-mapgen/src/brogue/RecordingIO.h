/* Checked, UTF-8 native recording I/O. Shared by standalone and bridge paths. */
#include <errno.h>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <io.h>
#else
#include <unistd.h>
#endif

static char recordingError[256];
static boolean managedLoad;
static size_t playbackBufferBytes;

const char *recordingLastError(void) { return recordingError; }
void clearRecordingError(void) { recordingError[0] = '\0'; }
static boolean recordingFail(const char *operation) {
    snprintf(recordingError, sizeof(recordingError), "%s: %s", operation, strerror(errno));
    return false;
}

#ifdef _WIN32
static boolean recordingWide(const char *path, wchar_t *wide) {
    return MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, path, -1, wide, BROGUE_FILENAME_MAX) != 0;
}
#endif
FILE *openBrogueFile(const char *path, const char *mode) {
#ifdef _WIN32
    wchar_t wide[BROGUE_FILENAME_MAX], wideMode[8];
    if (!recordingWide(path, wide) || !MultiByteToWideChar(CP_UTF8, 0, mode, -1, wideMode, 8)) {
        errno = EINVAL; return NULL;
    }
    return _wfopen(wide, wideMode);
#else
    return fopen(path, mode);
#endif
}
static boolean recordingRemove(const char *path) {
#ifdef _WIN32
    wchar_t wide[BROGUE_FILENAME_MAX];
    return recordingWide(path, wide) && _wremove(wide) == 0;
#else
    return remove(path) == 0;
#endif
}
static boolean recordingReplace(const char *from, const char *to) {
#ifdef _WIN32
    wchar_t wfrom[BROGUE_FILENAME_MAX], wto[BROGUE_FILENAME_MAX];
    if (!recordingWide(from, wfrom) || !recordingWide(to, wto)) { errno = EINVAL; return false; }
    if (MoveFileExW(wfrom, wto, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) return true;
    errno = EACCES;
    return false;
#else
    return rename(from, to) == 0;
#endif
}
static boolean recordingSync(FILE *file) {
    if (fflush(file) != 0) return false;
#ifdef _WIN32
    return _commit(_fileno(file)) == 0;
#else
    return fsync(fileno(file)) == 0;
#endif
}

/* Never publish a partially written recording, or discard its buffered suffix. */
static boolean recordingPublish(const char *source, const char *destination,
                                unsigned long prefixBytes, const unsigned char *suffix,
                                size_t suffixBytes, const unsigned char *header) {
    char temporary[BROGUE_FILENAME_MAX];
    unsigned char buffer[16384];
    FILE *input = NULL, *output = NULL;
    boolean ok = false;
    if (!destination || !destination[0]
        || snprintf(temporary, sizeof(temporary), "%s.pending", destination) >= sizeof(temporary)) {
        errno = EINVAL; return recordingFail("Invalid recording path");
    }
    if (prefixBytes && !(input = openBrogueFile(source, "rb"))) return recordingFail("Open recording");
    output = openBrogueFile(temporary, "wb");
    if (!output) { if (input) fclose(input); return recordingFail("Create recording"); }
    for (unsigned long remaining = prefixBytes; remaining;) {
        size_t count = min(remaining, sizeof(buffer));
        if (fread(buffer, 1, count, input) != count || fwrite(buffer, 1, count, output) != count) goto done;
        remaining -= count;
    }
    if (suffixBytes && fwrite(suffix, 1, suffixBytes, output) != suffixBytes) goto done;
    if (header && (fseek(output, 0, SEEK_SET) || fwrite(header, 1, 36, output) != 36)) goto done;
    if (!recordingSync(output)) goto done;
    ok = true;
done:
    if (input && fclose(input)) ok = false;
    if (fclose(output)) ok = false;
    if (ok) ok = recordingReplace(temporary, destination);
    if (!ok) { recordingFail("Publish recording"); recordingRemove(temporary); }
    return ok;
}
