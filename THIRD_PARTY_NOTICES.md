# Third-party notices

Project Broom combines and distributes free software from several projects.
Every binary release must include the complete license and credit files named
below. This document is a summary, not a replacement for those licenses.

| Component | Version or revision | Purpose | License |
| --- | --- | --- | --- |
| Brogue CE | commit `7f52dd93b7fa553dd6e354ccd44229a3c22d8a76` | Authoritative game simulation | AGPL-3.0-or-later |
| UZDoom (derived from GZDoom) | `5.0.0`, commit `292cf4203ebd3ced951cb67f6819180f588c1d44` | 3D frontend | GPL-3.0 and component licenses |
| ZMusic | 1.3.0, bundled in the pinned UZDoom source | UZDoom static music library | GPL-3.0-or-later and component licenses |
| libsndfile | 1.2.2, commit `72f6af15e8f85157bd622ed45b979025828b7001` | Audio-file runtime | LGPL-2.1-or-later |
| OpenAL Soft | 1.23.1, commit `d3875f333fb6abe2f39d82caca329414871ae53b` | 3D audio runtime | LGPL-2.0-or-later |
| Freedoom | 0.13.0 | Freely redistributable Doom-compatible IWAD | BSD 3-Clause |
| UltimateClassicMinimap | commit `0c690b839b333da1823b935e9d6db7fa9379cfd9` | Optional development minimap support | MIT |

Project Broom is an unofficial project and is not endorsed by the Brogue CE,
UZDoom, GZDoom, Doom, or Freedoom authors.

Community Chest 4 and Sunlust maps were used only as visual research during
development. Their map WADs, geometry, and scripts are not part of Project
Broom. The former CC4 resource WAD is not a runtime dependency and is not
included in the public source or release package.

Exact source URLs, hashes, and packaging policy are recorded in
`dependencies.lock.json`. Release archives include component license folders
and a machine-readable file manifest. The corresponding-source archive also
contains the pinned ZMusic, libsndfile, and OpenAL Soft sources for the audio
dependencies taken from the official UZDoom Windows package. ZMusic is built
from the bundled source; no separate ZMusic DLL is shipped.
