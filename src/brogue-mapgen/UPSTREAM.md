# Brogue CE map generator provenance

This directory is a tracked working snapshot of the Brogue CE source used by
the Brogue-to-GZDoom map pipeline.

- Upstream repository: https://github.com/tmewett/BrogueCE
- Pinned commit: `7f52dd93b7fa553dd6e354ccd44229a3c22d8a76`
- Variant: normal Brogue
- Dungeon version: `CE 1.11`

The upstream reference checkout at `../../tooling/source/BrogueCE` is kept
untouched. Local changes in this snapshot add a deterministic JSON export
command; the existing Brogue generation and RNG code remains authoritative.

Brogue CE is licensed under the GNU Affero General Public License, version 3.
The license text is included in `LICENSE.txt`.
