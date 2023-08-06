# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Replace grams with `msre_id` and `amt` in `food_log` table
- Rename to use `.sqlite3` extension, instead of `nt.sqlite`

### Development

- Enhance lint tools
- Use `__main__.py` & `python -m sql` to package and build sqlite3 file

### Added

- SQL tables `bug` and `msg`, for bug reports & pushed message queue

## [0.0.4] - 2021-06-17

### Added

- Empty `__init__.py` file to make packageable with `cli` repo (as a `git submodule`)
- SQL table `custom_foods` and respective `cf_dat`

### Changed

- Build with `python sql/__init__.py` (removed root-level script `build.py`)
- Rename pre-populated `meals` table to `meal_name`

### Fixed

- Slight bash inconvenience when using `export.sh`

### Removed

- `food_costs` table

## [0.0.3] - 2021-05-24

### Added

- More dummy CSV data (not production ready)
- `tagname` column to `recipes` table

### Changed

- `date` column uses `INT` type now, instead of `date`
- Drop `created` and `updated` fields off of `rda` table, add them to `biometrics`

### Removed

- `last_sync` column (future release? Feature is planned, but not allotted)
- `guid` parameter from `functions.sql`

## [0.0.2] - 2021-05-24

### Added

`SCRIPT_DIR` in `sql/__init__.py` to help track `cwd`

### Removed

- `guid` columns (may return in a future release)

## [0.0.1] - 2021-05-21

### Added

- Version table
- Travis CI configuration file `.travis.yml`
- `functions.sql` for use in Python client
- [TODO] Placeholder for initial upgrade script (`sql/upgrade_scripts/0.0.1.sql`)
- `food_costs` table (lone table, functionality not yet implemented)

### Changed

- Use Python for import script (`build.py` replaced `import.sql`)

## [0.0.0] - 2020-09-22

### Added

- Initial release of table schema design
- Import script `import.sql` (SQL)
- Export script `export.sh` (Shell)
- Rudimentary dummy data in CSV files
    (e.g. `food_log.csv`, `biometric_log.csv`, `profiles.csv`)
- Database diagram generated via `docs/sqleton.sh`
