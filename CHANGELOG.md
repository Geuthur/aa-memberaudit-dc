# Changelog

## [In Development] - Unreleased

<!--
> [!NOTE]
>

> [!TIP]
>

> [!IMPORTANT]
>

> [!WARNING]
>

> [!CAUTION]
>

Section Order:

### Added
### Fixed
### Changed
### Removed
-->

<!-- Your changes go here -->

### Changed

- `General` now defines a `Permission` enum (`TextChoices`), `Meta.permissions = Permission.choices` and the helpers `get_perm`, `has_perm`, `has_any_perm` and `has_management_access`. Views, API, menu hook and managers check permissions only through `General` instead of permission strings. Permission codenames are unchanged; migration `0005` only re-declares the permission list.
- Logging: a single `AppLogger` is created in `madc/providers.py` and imported by all modules via `from madc.providers import logger` (replaces `LoggerAddTag` per module; log records now use the logger name `madc.providers`)
- Tests for the `AppLogger` prefix
- The shared `SkillListHandler` instance moved from `madc/providers.py` to `madc/helpers/skill_handler.py` (`skill_list_handler`) to avoid a circular import

### Removed

- Unused module loggers in `decorators.py`, `models/general.py`, `models/skillchecker.py`, `api/helpers.py`, `api/admin/admin.py` and `api/skill/skillchecker.py`

### Added

- Optional extra `tests-allianceauth-development` (test packages plus the Alliance Auth 6 pre-release) for the tox environment `allianceauth-development` and `make tox-tests-development`; a non-blocking CI job "AA Development" runs it on Python 3.13 and 3.14

### Fixed

- Fixed `__operations__` being an empty list, it now contains the public operation `GetStatus`. An empty filter makes `esi.client` raise an `AttributeError` with `DEBUG=False`.
- Fixed `make coverage` exiting with 0 when tests failed. The reports are still created, and the target now exits with the status of the test run, or with the status of `coverage report` if the tests passed.

### Changed

- Raised `__esi_compatibility_date__` to `2026-08-18`.
- Tests: unified test base like the template `aa-example`. `madc/tests/__init__.py` now provides `NoSocketsTestCase` and `AuthTestCase`, users come from a `UserMainFactory` (`madc/tests/testdata/app.py`) based on `aa-evesde-factory`, which is added to the test extras. The JSON loader for Alliance Auth objects (`load_allianceauth`, `allianceauth.json`) and the use of `app_utils.testing` in the tests are removed.

## [0.4.0] - 2026-07-10

### Changed

- remove old BS template import

### Removed

- ESI Provider

## [0.3.4] - 2026-04-08

> [!WARNING]
>
> This will be the Last Version that will work with AAv4 and is not Compatible with AAv5

### Added

- AAv5 Dependency Check in Test Evniroement

### Removed

- Fittings Addon

## [0.3.3] - 2025-12-22

### Changed

- Updated German Translations
- Bump the npm-dependencies group with 2 updates
- Bump actions/checkout from 5 to 6

### Fixed

- Remove incorrect 'Adminstration' translations from multiple language files

## [0.3.2] - 2025-11-16

### Changed

- Downgrade `allianceauth-app-utils` to `>=1.30`

## [0.3.1] - 2025-11-13

### Changed

- Updated dependencies
  - `allianceauth-app-utils` to `>=2b2`
  - `allianceauth` to `>=4.10,<5`
  - `django-esi` to `8,<9`
  - `django-eveuniverse` to `>=1.6`
  - `aa-memberaudit` to `>=3.16`

### Removed

- csrf arg from `django-ninja`
- `django-ninja` dependency pin `<1.5`
- allow-direct-references

## [0.3.0] - 2025-11-13

### Added

- Temporary pin `django-ninja` to `django-ninja<=1.5`
  - https://github.com/vitalik/django-ninja/pull/1524

## [0.2.8] - 2025-10-29

### Added

- Application Tests
- Skill Overview from [Allianceauth Corp Tools](https://github.com/Solar-Helix-Independent-Transport/allianceauth-corp-tools/blob/master/corptools/templatetags/fittings_skill_tree.py)

### Fixed

- Level Check in `skillchecker`

### Removed

- Unused stuff

## [0.2.7] - 2025-10-21

### Changed

- Updated Makefile System
- Updated Contributing
- Updated Translations

## [0.2.6] - 2025-10-15

### Added

- Makefile System
- Automatic Release Workflow

### Changed

- Updated Translations
- Updated Dependencies

## [0.2.5] - 2025-08.06

### Fixed

- Wrong TemplateTag

## [0.2.4] - 2025-07-17

### Added

- Corporation Overview

### Fixed

- API schema Issue with 403 errors

## [0.2.3] - 2025-07-11

## Added

- `django-esi` dependency

## Changed

- Use `django-esi` new User Agent Guidelines

## [0.2.2] - 2025-07-08

### Changed

- Clean Code from Old Stuff

## [0.2.1] - 2025-07-07

### Changed

- Use Checkbox filtering instead of Dropdown
- Optimized CSS

### Added

- X-Editable 1.5.8
- Interactive Editing for Doctrine Administration
- dataTable CSS
- Doctrine Skills API
- Doctrine View for Doctrine Administration
- Category to Doctrine Administration

## Removed

- Debug Logs in API

### Fixed

- Modal Error Handling

## [0.2.0] - 2025-07-05

### Added

- Missing Skills Dialog

### Changed

- Optimized Form

## [0.1.0] - 2025-07-05

### Added

- Category Filter
- Form Update
  - Ordering Field
  - Category Field

### Changed

- Limit letters for Name and Category
- Optimized DataTable Search Field
- Disable Character Searching

## [0.0.5] - 2025-07-04

### Added

- Preview Images for Github

### Changed

- moved Main View to `header_nav_brand`

### Fixed

- README Naming Issues
- Missing Migration for `Remove Standard Permissions`

## [0.0.4] - 2025-07-04

### Added

- Account Overview #7
- Github Stuff #2

### Changed

- Update npm #4
- Update github #3

### Fixed

- Permissions #6 #1
- Tox #5

## [0.0.3] - 2025-07-04

### Changed

- Removed standard permissions from models

### Fixed

- Github badges

## [0.0.1] - 2025-07-03

- Initial Release

<!-- Links -->

[0.3.0]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.2.8...v0.3.0 "0.3.0"
[0.3.1]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.3.0...v0.3.1 "0.3.1"
[0.3.2]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.3.1...v0.3.2 "0.3.2"
[0.3.3]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.3.2...v0.3.3 "0.3.3"
[0.3.4]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.3.3...v0.3.4 "v0.3.4"
[in development]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.3.4...HEAD "In Development"
