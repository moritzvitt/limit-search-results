# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows semantic versioning where practical.

## 0.2.0 - 2026-04-03

### Added

- Expanded `limit:x` support beyond Browser hooks so queries passed through `find_notes()` and `find_cards()` also respect the modifier.
- Ranked limited card results by queue state and due position so the add-on prefers cards you are likely to see sooner.
- Ranked limited note results by the earliest matching card attached to each note.

### Changed

- Replaced the starter template metadata and documentation with `Limit Search Results` add-on content.
- Simplified the add-on configuration to an empty default config because the add-on currently has no user-facing settings.
- Refreshed the README and release description to match the current search behavior and packaging flow.

## 0.1.0 - 2026-03-27

### Added

- Added a `limit:x` browser search modifier to show only the first matching results.
- Registered browser search hooks to strip the modifier before search and trim the returned ids afterward.
- Replaced starter template metadata and documentation with add-on-specific content.
