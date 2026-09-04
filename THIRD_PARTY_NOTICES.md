# Third-party notices

Project Broom combines and distributes free software from several projects.
Every binary release must include the complete license and credit files named
below. This document is a summary, not a replacement for those licenses.

| Component | Version or revision | Purpose | License |
| --- | --- | --- | --- |
| Brogue CE | commit `7f52dd93b7fa553dd6e354ccd44229a3c22d8a76` | Authoritative game simulation | AGPL-3.0-or-later |
| GZDoom | `g4.14.2`, commit `99aa489d09015a95bb78df2b30ede29f328cc874` | 3D frontend | GPL-3.0 and component licenses |
| ZMusic | 1.1.14, commit `89f3d65734470fb7ec0c1e69f73a0cfcc88ed557` | GZDoom music runtime | GPL-3.0-or-later and component licenses |
| libsndfile | 1.2.2, commit `72f6af15e8f85157bd622ed45b979025828b7001` | Audio-file runtime | LGPL-2.1-or-later |
| OpenAL Soft | 1.23.1, commit `d3875f333fb6abe2f39d82caca329414871ae53b` | 3D audio runtime | LGPL-2.0-or-later |
| Freedoom | 0.13.0 | Freely redistributable Doom-compatible IWAD | BSD 3-Clause |
| UltimateClassicMinimap | commit `0c690b839b333da1823b935e9d6db7fa9379cfd9` | Optional development minimap support | MIT |

Project Broom is an unofficial project and is not endorsed by the Brogue CE,
GZDoom, Doom, or Freedoom authors.

Community Chest 4 and Sunlust maps were used only as visual research during
development. Their map WADs, geometry, and scripts are not part of Project
Broom. The former CC4 resource WAD is not a runtime dependency and is not
included in the public source or release package.

Exact source URLs, hashes, and packaging policy are recorded in
`dependencies.lock.json`. Release archives include component license folders
and a machine-readable file manifest. The corresponding-source archive also
contains the pinned ZMusic, libsndfile, and OpenAL Soft sources for the audio
DLLs taken from the official GZDoom Windows package.
