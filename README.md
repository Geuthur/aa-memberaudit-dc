# Tax System module for AllianceAuth.<a name="aa-memberaudit-dc"></a>

![Release](https://img.shields.io/pypi/v/aa-memberaudit-dc?label=release)
![Licence](https://img.shields.io/github/license/geuthur/aa-memberaudit-dc)
![Python](https://img.shields.io/pypi/pyversions/aa-memberaudit-dc)
![Django](https://img.shields.io/pypi/frameworkversions/django/aa-memberaudit-dc.svg?label=django)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-memberaudit-dc/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-memberaudit-dc/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Geuthur/aa-memberaudit-dc/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-memberaudit-dc/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-memberaudit-dc/graph/badge.svg?token=YfJSsDECUm)](https://codecov.io/gh/Geuthur/aa-memberaudit-dc)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

A Doctrine Checker Addon for Memberaudit

______________________________________________________________________

- [AA Memberaudit Doctrine Checker](#aa-memberaudit-dc)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Screenshots](#screenshots)
  - [Installation](#features)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add the Scheduled Tasks and Settings](#step3)
    - [Step 4 - Migration to AA](#step4)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)

## Features<a name="features"></a>

- Memberaudit Doctrine Checker
  - Doctrine Overview
    - Check if Character met criteria for Doctrines
    - Ingame supported copy clipboard skill-queue

## Upcoming<a name="upcoming"></a>

- Account Overview
- Detailed Modal-Overview for missing Skills
- Optimize Search Field
- Ordering Doctrines
- Filter by Category example: (Capital, Black OP Group, Mining)

## Screenshots<a name="screenshots"></a>

## Installation<a name="installation"></a>

> [!NOTE]
> AA Tax System needs at least Alliance Auth v4.6.0
> Please make sure to update your Alliance Auth before you install this APP

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-memberaudit-dc
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

- Add `'allianceauth.corputils',` to `INSTALLED_APPS`
- Add `'eveuniverse',` to `INSTALLED_APPS`
- Add `'memberaudit',` to `INSTALLED_APPS`
- Add `'madc',` to `INSTALLED_APPS`

### Step 3 - Add the Scheduled Tasks<a name="step3"></a>

To set up the Scheduled Tasks add following code to your `local.py`

```python
```

### Step 3.1 - (Optional) Add own Logger File

To set up the Logger add following code to your `local.py`
Ensure that you have writing permission in logs folder.

```python
LOGGING["handlers"]["madc_file"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(BASE_DIR, "log/madc.log"),
    "formatter": "verbose",
    "maxBytes": 1024 * 1024 * 5,
    "backupCount": 5,
}
LOGGING["loggers"]["extensions.madc"] = {
    "handlers": ["madc_file", "console", "extension_file"],
    "level": "DEBUG",
}
```

### Step 4 - Migration to AA<a name="step4"></a>

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the Tax System

| ID                | Description                                                  |                                                        |
| :---------------- | :----------------------------------------------------------- | :----------------------------------------------------- |
| `basic_access`    | Can access the Memberaudit Doctrine Checker.                 | All Members with the Permission can access the MADC.   |
| `corp_access`     | Can view Characters from own Corporation.                    | Users with this can view all characters from own corp. |
| `alliance_access` | Can view Characters from own Alliance.                       | Users with this can view all characters from own ally. |
| `manage_access`   | Can manage this app, Memberaudit Doctrine Checker.           | Users with this permission can manage the MADC.        |
| `admin_access`    | Gives full access to this app, Memberaudit Doctrine Checker. | Users with this permission have full access.           |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

- AA_DC_APP_NAME: `"YOURNAME"` - Set the name of the APP

> [!NOTE]
> Contributing
> You want to improve the project?
> Just Make a [Pull Request](https://github.com/Geuthur/aa-memberaudit-dc/pulls) with the Guidelines.
> We Using pre-commit
