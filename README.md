# FHIR Scripts

## Python Script (preferred)

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

The script uses a config file. An example can be found [here](./examples/config.yaml). The default path for this file `./config.yaml`. A different path can be defined

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

### Update

Update each installed tool

```bash
fhirscripts update
```

<!-- With the available parameters

| Top Level | Sub Level | Lowest Level | Description                                                             |
| :-------: | :-------: | :----------: | :---------------------------------------------------------------------- |
|   `all`   |           |              | Update everything                                                       |
|           |  `tools`  |              | Update tooling from the FHIR community, e.g. IG Publisher and FSH Sushi |
|           |           |   `sushi`    | Update FSH Sushi                                                        |
|           |           |   `igpub`    | Update IG Publisher                                                     |
|           | `pytools` |              | Update gematik's Python tooling, e.g. epatools, igtools, publishtools   | --> |

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

## Bash script

The FHIR Scripts scripts provide commands that support the develop process for FHIR profiles and IGs.

The following commands arw available:

| Command     | Description                                         |
| ----------- | --------------------------------------------------- |
| `update`    | Update the script itself                            |
| `pytools`   | Update the Python tools, e.g. *igtools*, *epatools* |
| `tools`     | Update Sushi and IG Publisher                       |
| `fhircache` | Rebuild FHIR cache                                  |
| `bdcache`   | Delete the build cache                              |
| `build`     | Build IG                                            |
| `deploy`    | Deploy an IG                                        |

### Update the script itself

Download the latest version of the script to the current directory.

## Update the Python tools

Install the latest version of the Python tools:

* [igtools](https://github.com/onyg/req-tooling)
* [epatools](https://github.com/onyg/epa-tools)

### Update Sushi and IG Publisher

Install the latest version of FSH Sushi and IG Publisher.

### Rebuild FHIR Cache

Clears the FHIR cache and rebuilds it from FHIR packages. Optionally it can install packages from a local directory and cache dependency packages in this directory.

```bash
./fhir_scripts.sh fhircache [<pkgdir>]
```

When `<pkgdir>` is provided, the dependencies from `package.json` are read and available packages from `<pkgdir>` will be installed. Additionally, direct dependencies that are not present in `<pkgdir>` will be downloaded for later usages.

### Delete the build cache

Delete cached schemas and TX from `input-cache/`.

### Build IG

Performs several steps to support the process of building a FHIR IG.

It is separated into two parts, building

* the FHIR definitions
* the FHIR IG

whereas, the optional argument `noig` only builds the definitions and `nodefs` only builds the IG.

#### FHIR Definitions

Steps:

* Track and update requirements and update release notes, if *igtools* are available
* Build FHIR definitions using FSH Sushi
* Merge CapabilityStatements, if *epatools* are available

#### FHIR IG

Steps:

* Build IG using IG Publisher
* Generate OpenAPI specifications, if *epatools* are available
* Update archived IG, if *epatools* are available

For building the IG `config.sh` needs to present in the current directory defining the publish URL for the IG Publisher as `PUBLISH_URL`. For updating the archive a list of files needs to be defined as `CONTENT_FILES`.

### Deploy an IG

Deploy the IG from the build directory (`output/`) to the webserver.

#### Google Cloud

Uses a gCloud as a target and requires the following tools:

* *gcloud*
* *gsutils*

The IG will be deployed to `<bucket>/<path>/<version>`. Depending on the argument `dev` or `prod` the respective bucket is used.

First, it is checked if logged in into a gcloud Account and starting the login process, if not. Then, the path in the bucket is checked if empty, cleared if not and the files copied afterwards.

The configuration is read from a `config.sh` file in the current directory defining:

```bash
TARGET=<version>
BUCKET_PATH=<path>
BUCKET_NAME_DEV=<dev-bucket>
BUCKET_NAME_PROD=<prod-ucket>
```
