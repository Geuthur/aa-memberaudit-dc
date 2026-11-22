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

### Fixed

- React Query no longer retries 403, 404 and other 4xx answers three times, so the error shows at once instead of after about seven seconds (`createQueryClient` of `aa-geuthur-react` `^1.7.0`)

### Changed

- The menu entry now uses the `AA_DC_APP_NAME` setting (default "Doctrine Checker"); it was ignored before. The entry is no longer translated.
- Internal: i18next 27, react-i18next 18, stylelint 18 and stylelint-config-standard 41; the pre-commit stylelint hook sets `--config-basedir` because stylelint 18 no longer loads `extends` from global `node_modules`. Missing plural forms in a language now fall back to that language's `_other` form instead of English (no plural keys in this app).
- Internal: Node 26 in CI and pre-commit, npm packages updated (jsdom 31, jest-dom 8); stylelint 17, i18next 26, react-i18next 17 and TypeScript 5.9 stay.
- Internal: The frontend API calls are split by area into `Api/calls/{doctrines,overview,corporation,manage}.ts`, each with its own query keys, replacing `Api/ApiCalls.ts` and `Api/query.ts`.
- Internal: eslint now enforces the import order React, third party, `@/`, styles (CSS imports via `@/` belong to `// Styles`); the remaining relative imports in `frontend/src` use `@/`.

### Removed

- Internal: Unused `madc/decorators.py` (`log_timing`) with its test, and the empty `madc/tasks.py` and `madc/templatetags` stubs.
- Internal: Unused `IS_TESTING` constant in `madc/app_settings.py`.
- Internal: Unused `EVE_BASE_URL`, `EVE_API_URL`, `EVE_BASE_URL_REGEX` and `AA_MADC_TASKS_TIME_LIMIT` in `madc/app_settings.py`.

## [0.5.0] - 2026-11-20

> [!WARNING]
> Basic access is only granted by `basic_access`. Users with `corp_access`, `alliance_access`, `manage_access` or `admin_access` but without `basic_access` lose access to the API and the pages; give them `basic_access` as well.

### Added

- API endpoints to create, edit and delete skill lists, plus `menu/`, `user/` and corporation member audit with filters
- Optional extra `tests-allianceauth-development` (Alliance Auth 6 pre-release) with tox environment `allianceauth-development`, `make tox-tests-development` and a non-blocking CI job "AA Development"
- Tests that match all permission strings used in the code against `General.Meta.permissions` and check the `AppLogger` prefix

### Fixed

- Corporation endpoints showed the own corporation without `corp_access`
- `alliance_access` showed all characters and corporations without alliance if the main character has no alliance, and compared the wrong alliance ID for corporations
- Cached check results stayed up to 72 hours after a change of category, ordering, active flag or skills of a skill list
- Server errors for a skill list without skills and for the doctrines of a character without owner
- Category of a skill list could not be removed when editing
- Inline editing of a skill list lost the input when saving failed
- Bookmarks of the former template pages (e.g. `/madc/<id>/view/checker/`) redirect to the new pages
- Menu entry and overview tab of the corporations were missing with `alliance_access` only
- `__operations__` was an empty list, it now contains the public operation `GetStatus`; an empty filter makes `esi.client` raise an `AttributeError` with `DEBUG=False`
- `make coverage` exited with 0 when tests failed; it now exits with the status of the test run

### Changed

- Frontend rebuilt in React (aa-geuthur-react) on the base of aa-corptools-dc, with inline editing of skill lists
- API restructured like aa-corptools-dc; modal endpoints and overviews answer JSON
- Uniform error format of the API: every error response is `{"error": "<text>"}` (`ErrorSchema`) and every endpoint lists its 403 in the OpenAPI schema
- The whole API (`basic_access_required` around the API URLs) and all views require `basic_access`; without it every endpoint answers 403 `{"error": "Permission Denied"}`, also for characters of the own account
- Permissions are checked only through `General.objects` (`GeneralManager` in `managers/general.py` with `has_basic_access`, `has_corp_access`, `has_alliance_access`, `has_admin_access`, `has_full_access` and `has_management_access`) and the full string (e.g. `madc.basic_access`); codenames are unchanged, no migration needed, permission texts are translatable
- Logging: a single `AppLogger` in `madc/providers.py` replaces `LoggerAddTag` per module (logger name `madc.providers`); the shared `SkillListHandler` instance moved to `madc/helpers/skill_handler.py` (`skill_list_handler`)
- Raised `__esi_compatibility_date__` to `2026-08-18`
- Tests: unified test base like the template `aa-example` (`NoSocketsTestCase`, `AuthTestCase`, `UserMainFactory` based on `aa-evesde-factory`); the JSON loader `load_allianceauth` and `app_utils.testing` are no longer used
- Bumped dev dependency eslint to 10.15 (minimatch 11, fixes GHSA-g3hv-75wg-m249)

### Removed

- Django templates, jQuery scripts and x-editable; the old page URLs now open the React app

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
[0.4.0]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.3.4...v0.4.0 "v0.4.0"
[0.5.0]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.4.0...v0.5.0 "v0.5.0"
[in development]: https://github.com/Geuthur/aa-memberaudit-dc/compare/v0.5.0...HEAD "In Development"
