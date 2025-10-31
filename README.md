# FHIR Scripts

## Python Script

Install using pipx

```bash
pipx install "fhir_scripts @ git+https://github.com/gematik/fhir-scripts.git"
```

Optionally, one can provide addtional arguments for `pipx install`:

* `-f`, `--force`: overwrite an existing installation
* `--global`: install for all users (may need to be called using `sudo`)

Also there can optional compentens be defined to be also installed using `fhir_scripts[opt,...]`. These are Python packages that otherwise may be called using a shell. Available components are:

* `epatools`: Handle CapabilityStatements and OpenAPI
* `igtools`: Handle requirements
* `publishtools`: Support the publish workflow

Get information about the usage with

```bash
fhirscripts --help
```

### Config

The script uses a config file. [An example can be found here](./examples/config.yaml). The default path for this file `./config.yaml`. A different path can be defined

```bash
fhirscripts --config <config> <command>
```

### Versions

Get the version of installed tooling

```bash
fhirscripts versions
```

### Install

Install one or multiple tools

```bash
fhirscripts install --<tool> [--<tool> [...]]
```

Get a list of available tools to install

```bash
fhirscripts install --help
```

#### From Config File

Tools to be installed can also be defined in the config giving the name of the tool

```yaml
install:
  - <tool>
  - <tool2>
```

### Update

Update each installed tool

```bash
fhirscripts update
```

### Cache

Rebuild the local FHIR package cache

```bash
fhirscripts cache package [--package-dir <packagedir>] [--no-clear]
```

_(WIP)_ A local directory can be used as package cache. If `--package-dir <packagedir>` is provided, packages from `<packagedir>` will be installed instead and if not found, cached to this directory before installing them from there.

`--no-clear` allows to restore the FHIR package cache without clearing the directory in beforehand.

### Build

_Requirements:_

* IG Publisher
* FSH Sushi
* (optional igtools, either as component or using pipx)
* (optional epatools, either as component or using pipx)

Building happens in two stages: FHIR definitions and FHIR IG.

One can also update the tooling before building with `--update`.

Optional steps for the following steps can be defined using the `builtin` section in the config.

```yaml
build:
  builtin:
    igtools: true
    epatools:
      cap_statements: true
      openapi: true
    # 'epatools' can also be defined to enable or disable all steps
    # epatools: true
```

#### Definitions

Build the FHIR definitions

```bash
fhirscripts build defs [--req] [--only-req] [--cap] [--only-cap]
```

using FSH Sushi.

`--req` additionally processed requirements using _igtools_ before executing Sushi, while `--only-req` only performs this step. `--cap` also combines the CapabilityStatements using _epatools_, while `--only-cap` only performs this step.

#### IG

Build the FHIR IG using IG Publisher

```bash
fhirscripts build ig [--oapi] [--only-oapi]
```

using `--oapi` to also generate OpenAPI definitions using _epatools_, while `--only-oapi` only performs this step.

#### Everything together

Build the FHIR definitions and FHIR IG

```bash
fhirscripts build all [--req] [--cap] [--oapi]
```

with `--req`, `--cap` and `--oapi` additionally enabling the steps mentioned before.

#### Pipeline

Build from a pipeline defined in the configuration

```bash
fhirscripts build pipeline
```

The pipeline is defined like

```yaml
build:
  pipeline:
    - <step>
    - <step>:<args>
```

Available steps are:

| Step Name        | Arguments     | Description                                                                 |
| ---------------- | ------------- | --------------------------------------------------------------------------- |
| `sushi`          | None          | Run FSH Sushi                                                               |
| `igpub`          | None          | Run IG Publisher                                                            |
| `igpub_qa`       | None          | Display IG Publisher QA results                                             |
| `requirements`   | None          | Process requirements using _igtools_                                        |
| `cap_statements` | None          | Process and merge CapabilityStatements using _epatools_                     |
| `openapi`        | None          | Generate OpenAPI definitions using _epatools_ and add the to the IG archive |
| `shell`          | Shell command | Execute a command on the shell, e.g. "touch file"                           |

### Publish

_Requirements:_

* publishtools, either as component or using pipx

Publish and therefore preparing information from either a FHIR project or a FHIR IG registry, e.g. [gematik FHIR IG Registry](https://github.com/gematik/fhir-ig-registry).

#### FHIR Project

Publish a FHIR project

```bash
fhirscripts publish [--project-dir <projectdir>] --ig-registry <igregistry>
```

from the current directory or `<projectdir>` if provided. This will generate JSON file containing the IG history and an HTML file representing the rendered history.

It will also update the FHIR IG registry in the `<igregistry>` directory. This will update a JSON file containing all versions of all IGs published by your organization, an HTML rendered version of it and update the `package-feed.xml` that can be used to publish your FHIR packages to the [official FHIR registry](https://registry.fhir.org).

### Deploy

_Requirements:_

* gcloud CLI

Deploy a generated FHIR IG onto a Google Bucket

```bash
fhirscripts deploy <env> [-y|--yes] [--all|--only-ig|--only-history|--ig-registry]
```

in the environment named `<env>`. This nneds to match an environment defined in the config in the `deploy` section.

`-y`/`--yes` confirms all prompts with _yes_. Otherwise, the path to upload to and overwriting need to be confirmed.

By default the FHIR IG is deployed. With `--all` the IG and the IG history are deployed and with `--only-ig` or `--only-history` only the respective part is deployed.

If not an IG but a a FHIR registry should be deployed use `--ig-registry`.

## Bash script (outdated)

The documentation has been moved to [/scripts](/scripts).

## Re-usable github Workflows

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
    uses: gematik/fhir-scripts/.github/workflows/build-profiles.yml
```

### Process Requirements

Process the requirements that are specified in the Markdown files using _igtools_ and commit possible changes. To use the workflow

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
    uses: gematik/fhir-scripts/.github/workflows/process-requirements.yml
```
