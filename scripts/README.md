# FHIR Scripts

The FHIR Scripts scripts provide commands that support the develop process for FHIR profiles and IGs.

The following commands arw available:

| Command     | Description                                         |
| ----------- | --------------------------------------------------- |
| `update`    | Update the script itself                            |
| `pytools`   | Update the Python tools, e.g. _igtools_, _epatools_ |
| `tools`     | Update Sushi and IG Publisher                       |
| `fhircache` | Rebuild FHIR cache                                  |
| `bdcache`   | Delete the build cache                              |
| `build`     | Build IG                                            |
| `deploy`    | Deploy an IG                                        |

## Update the script itself

Download the latest version of the script to the current directory.

### Update the Python tools

Install the latest version of the Python tools:

* [igtools](https://github.com/onyg/req-tooling)
* [epatools](https://github.com/onyg/epa-tools)

## Update Sushi and IG Publisher

Install the latest version of FSH Sushi and IG Publisher.

## Rebuild FHIR Cache

Clears the FHIR cache and rebuilds it from FHIR packages. Optionally it can install packages from a local directory and cache dependency packages in this directory.

```bash
./fhir_scripts.sh fhircache [<pkgdir>]
```

When `<pkgdir>` is provided, the dependencies from `package.json` are read and available packages from `<pkgdir>` will be installed. Additionally, direct dependencies that are not present in `<pkgdir>` will be downloaded for later usages.

## Delete the build cache

Delete cached schemas and TX from `input-cache/`.

## Build IG

Performs several steps to support the process of building a FHIR IG.

It is separated into two parts, building

* the FHIR definitions
* the FHIR IG

whereas, the optional argument `noig` only builds the definitions and `nodefs` only builds the IG.

### FHIR Definitions

Steps:

* Track and update requirements and update release notes, if _igtools_ are available
* Build FHIR definitions using FSH Sushi
* Merge CapabilityStatements, if _epatools_ are available

### FHIR IG

Steps:

* Build IG using IG Publisher
* Generate OpenAPI specifications, if _epatools_ are available
* Update archived IG, if _epatools_ are available

For building the IG `config.sh` needs to present in the current directory defining the publish URL for the IG Publisher as `PUBLISH_URL`. For updating the archive a list of files needs to be defined as `CONTENT_FILES`.

## Deploy an IG

Deploy the IG from the build directory (`output/`) to the webserver.

### Google Cloud

Uses a gCloud as a target and requires the following tools:

* _gcloud_
* _gsutils_

The IG will be deployed to `<bucket>/<path>/<version>`. Depending on the argument `dev` or `prod` the respective bucket is used.

First, it is checked if logged in into a gcloud Account and starting the login process, if not. Then, the path in the bucket is checked if empty, cleared if not and the files copied afterwards.

The configuration is read from a `config.sh` file in the current directory defining:

```bash
TARGET=<version>
BUCKET_PATH=<path>
BUCKET_NAME_DEV=<dev-bucket>
BUCKET_NAME_PROD=<prod-ucket>
```
