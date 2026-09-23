# FHIR

[![Unit Tests](https://github.com/gematik/fhir-scripts/actions/workflows/unittest.yml/badge.svg)](https://github.com/gematik/fhir-scripts/actions/workflows/unittest.yml)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/gematik/fhir-scripts)

Simplifies and automates steps needed to be executed build and handle FHIR definitions and FHIR IGs.

## Setup

### uv

Install using uv as a tool

```bash
uv tool install git+https://github.com/gematik/fhir-scripts.git
```

### pipx (deprecated)

Install using pipx

```bash
pipx install "fhir_scripts @ git+https://github.com/gematik/fhir-scripts.git"
```

Optionally, one can provide addtional arguments for `pipx install`:

* `-f`, `--force`: overwrite an existing installation
* `--global`: install for all users (may need to be called using `sudo`)

**Warning:** If using *pipx* the scripts needs to be able to install required tools as global.

## Usage

The Tool allows to call different commands for various build steps

```bash
fhirscripts [command] ...
```

Get more information about the usage with

```bash
fhirscripts --help
```

## Configuration

The script uses a config file. [An example can be found here](./examples/fhirscripts.config.yaml). The default path for this file `./fhirscripts.config.yaml`. A different path can be defined

```bash
fhirscripts [--config <config>] [--output-color <color>] <command>
```

`--output-color` controls subprocess output without changing its layout. The default
`default` uses the terminal foreground color, `preserve` keeps colors emitted by the
subprocess, and a named color (`black`, `red`, `green`, `yellow`, `blue`, `cyan`,
`gray`, or `white`) overrides it.

### DotEnv and Environment Variables

For root CLI arguments (those between `fhirscripts` and the `<command>`) it is possible to specify the values in an `.env` file or as environment variable. The `.env` file can be placed in the current directory or in the home directory.

The priority here is `.env` in home < `.env` in cwd < environment variables < arguments passed directly (meaning the latter ones overwrite the previous ones).

The format is that the argument `--foo-bar` can also be specified with the environment variable `FHIRSCRIPT_FOO_BAR`. The format for the entries in `.env` files is the same. Arguments that are passed without a value are defined with an empty string as value for environment variables or in `.env` files.

## Commands

### Versions

Command `version`

List the versions of installed tools.

### Install

Command `install [arguments]`

Install one or multiple tools.

| Argument        | Required | Description                                                                        |
| :-------------- | :------- | :--------------------------------------------------------------------------------- |
| `--<tool>`      | False    | Install `<tool>`. Can be defined multiple times to install multiple tools at once. |
| `--config-file` | False    | Install the tools defined in the config file                                       |
| `--help`        | False    | List additional information about the command including the available tools.       |

In the config file the tools can be defined with the short version:

```yaml
install:
  - <tool>
  - <tool2>
```

The long version allows to explicilty define the version to install, otherwise the latest will be used:

```yaml
install:
  - name: <tool>
    version: <version>
```

### Update

Command `update`

Update each installed tool

### Cache

Command `cache <scope>`

Clear and rebuild caches that are used during different process steps.

*Requirements*:

* Firely Terminal or
* FHIR Pkg Tool

| Scope     | Optional Arguments           | Description                                                                                                            |
| :-------- | :--------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `package` |                              | Rebuild the local FHIR package cache                                                                                   |
|           | `--package-dir <packagedir>` | WIP: Use `<packagedir>` as local cache directory, that will be searched for packages first                             |
|           | `--no-clear`                 | Do not clear the FHIR package cache before installing required ones                                                    |
|           | `--new`                      | Switch to an alternative to Firely Terminal that is not the default currently. If not installed, fall back to default. |
| `build`   |                              | Clear the build cache. Can help with caching issues during build.                                                      |

### Build

Command `build`

Build the FHIR definitions and FHIR IG.

*Requirements*:

* IG Publisher
* FSH Sushi
* *optional*:
  * reqtools
  * epatools

Building happens in two stages: FHIR definitions and FHIR IG.

| Sub-Command       | Optional Arguments | Description                                                           |
| :---------------- | :----------------- | :-------------------------------------------------------------------- |
| *all sub-commands |                    |                                                                       |
|                   | `--update`         | Update tools before building                                          |
| `defs`            |                    | Only build definitions                                                |
|                   | `--req`            | Also process the requirements defined in the IG (requires *reqtools*) |
|                   | `--only-req`       | Only process the requirements defined in the IG (requires *reqtools*) |
|                   | `--cap`            | Also process the capability statements (requires *epatools*)          |
|                   | `--only-cap`       | Only process the capability statements (requires *epatools*)          |
| `ig`              |                    | Only builds IG                                                        |
|                   | `--oapi`           | Also produce OpenAPI definitions (requires *epatools*)                |
|                   | `--only-oapi`      | Only produce OpenAPI definitions (requires *epatools*)                |
| `all`             |                    | Builds definitions and IG                                             |
|                   | `--req`            | See above                                                             |
|                   | `--cap`            | See above                                                             |
|                   | `--oapi`           | See above                                                             |
| `pipeline`        |                    | Build the pipeline defined in the config file                         |

The config entry in the config file has the following format:

```yaml
build:
  pipeline:
    - <step>
    - <step>:<args>
```

For the steps the following builtin options are available:

| Step Name        | Arguments     | Description                                                                 |
| ---------------- | ------------- | --------------------------------------------------------------------------- |
| `sushi`          | None          | Run FSH Sushi                                                               |
| `igpub`          | None          | Run IG Publisher                                                            |
| `igpub_qa`       | None          | Display IG Publisher QA results                                             |
| `requirements`   | None          | Process requirements using _reqtools_                                       |
| `cap_statements` | None          | Process and merge CapabilityStatements using _epatools_                     |
| `openapi`        | None          | Generate OpenAPI definitions using _epatools_ and add the to the IG archive |
| `shell`          | Shell command | Execute a command on the shell, e.g. "touch file"                           |

### Publish

Command `publish`

Publish and therefore preparing information from either a FHIR project or a FHIR IG registry, e.g. [gematik FHIR IG Registry](https://github.com/gematik/fhir-ig-registry).

*Requirements*:

* publishtools

Publish a FHIR project from the current directory or `<projectdir>` if provided. This will generate JSON file containing the IG history and an HTML file representing the rendered history.

It will also update the FHIR IG registry in the `<igregistry>` directory. This will update a JSON file containing all versions of all IGs published by your organization, an HTML rendered version of it and update the `package-feed.xml` that can be used to publish your FHIR packages to the [official FHIR registry](https://registry.fhir.org).

| Arguments                    | Required | Description                                                                                       |
| :--------------------------- | :------- | :------------------------------------------------------------------------------------------------ |
| `--project-dir <projectdir>` | False    | Publish the project defined in `<projectdir>`; If not definied the current directory will be used |
| `--ig-registry <igregistry>` | True     | Local path to the IG registry to fill in the information about the artifact                       |

### Deploy

Command `deploy <env>`

Deploy a generated FHIR IG onto a Google Bucket named `<env>`.

*Requirements*:

* gcloud CLI

The config file needs to have a corresponding entry that defines the environment.

```yaml
deploy:
  env:
    <env>: <bucket name>
```

| Argument         | Description                                                                                                 |
| :--------------- | :---------------------------------------------------------------------------------------------------------- |
| *without*        | Deploy built FHIR IG, history page and package list of current project                                      |
| `--only-ig`      | Only deploy FHIR IG                                                                                         |
| `--only-history` | Only deploy history (and package list)                                                                      |
| `--ig-registry`  | Current directory the ig registry; deploy the corresponding files                                           |
| `-y`, `--yes`    | Confirm all checks with *yes* (check for correct target path and potentially overwriting of existing files) |

## github Workflows (WIP)

These are the available workflows from this repository:

### Build Profiles

Build (re-)build the FSH definition using the lastest version of _FSH Sushi_ and commit possible changes. To use this workflow

```yaml
name: Build Profiles

on:
  pull_request:
    paths:
      - "**/build-profiles.yml"
      - "**.fsh"
      - "**/sushi-config.yaml"
    branches:
      - main
      - develop

  push:
    paths:
      - "**/build-profiles.yml"
      - "**.fsh"
      - "**/sushi-config.yaml"
    branches:
      - main
      - develop
    tags:
      - v*


permissions:
  contents: write

jobs:
  build-profiles:
    uses: gematik/fhir-scripts/.github/workflows/build-profiles.yml@main
```

### Process Requirements

Process the requirements that are specified in the Markdown files using _reqtools_ and commit possible changes. To use the workflow

```yaml
name: Process Requirements

on:
  pull_request:
    paths:
      - "**/process-requirements.yml"
      - "**.md"
    branches:
      - main
      - develop

  push:
    paths:
      - "**/process-requirements.yml"
      - "**.md"
    branches:
      - main
      - develop

  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-profiles:
    uses: gematik/fhir-scripts/.github/workflows/process-requirements.yml@main
```

## License

Copyright 2025 gematik GmbH

Apache License, Version 2.0

See the [LICENSE](./LICENSE) for the specific language governing permissions and limitations under the License.

## Additional Notes and Disclaimer from gematik GmbH

1. Copyright notice: Each published work result is accompanied by an explicit statement of the license conditions for use. These are regularly typical conditions in connection with open source or free software. Programs described/provided/linked here are free software, unless otherwise stated.
2. Permission notice: Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    1. The copyright notice (Item 1) and the permission notice (Item 2) shall be included in all copies or substantial portions of the Software.
    2. The software is provided "as is" without warranty of any kind, either express or implied, including, but not limited to, the warranties of fitness for a particular purpose, merchantability, and/or non-infringement. The authors or copyright holders shall not be liable in any manner whatsoever for any damages or other claims arising from, out of or in connection with the software or the use or other dealings with the software, whether in an action of contract, tort, or otherwise.
    3. The software is the result of research and development activities, therefore not necessarily quality assured and without the character of a liable product. For this reason, gematik does not provide any support or other user assistance (unless otherwise stated in individual cases and without justification of a legal obligation). Furthermore, there is no claim to further development and adaptation of the results to a more current state of the art.
3. Gematik may remove published results temporarily or permanently from the place of publication at any time without prior notice or justification.
4. Please note: Parts of this code may have been generated using AI-supported technology. Please take this into account, especially when troubleshooting, for security analyses and possible adjustments.
