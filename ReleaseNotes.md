<img align="right" width="250" height="47" src="img/Gematik_Logo_Flag_With_Background.png" /><br />

# Release Notes FHIR Scripts

## Release 0.23.0

* Check the Java version requirement during installation

## Release 0.22.0

* Allow to define an alternative directory for the generated FHIR IG for deployment using `--ig-output` (default `./output`)

## Release 0.21.1

* If _FHIR Package Snaphot Tool_ is not installed fall back to Firely Terminal for rebuilding the FHIR package cache

## Release 0.21.0

* Switch to [_FHIR Package Snapshot Tool_](https://github.com/Gefyra/fhir-pkg-tool) to restore the FHIR package cache
* _Firely Terminal_ can be used using the `--legacy` flag
* Check Java version for for dependend tooling

## Release 0.20.1

* Print IG Publisher output again

## Release 0.20.0

* Print output of commands

## Release 0.19.1

* Fix handling of `package.json` when using a local cache

## Release 0.19.0

* Option to only deploy IG meta data

## Release 0.18.0

* Option to update the script itself

## Release 0.17.0

* Make Dockerfile flexible for specific tools versions or latest
* Make `cache build` more verbose

## Release 0.16.1

* Fix update of Python tools installed using UV

## Release 0.16.0

* Command to clear the build caches

## Release 0.15.1

* Fix handling of not-existing FHIR cache when calling `cache package`
* Fix permissions of users `.fhir` folder in devcontainer image

## Release 0.15.0

* Support _uv_ and _pipx_ to install in isolated Python environments (_uv_ is default)
* Dry-run (`--dry-run`) option to simulate deployment
* Promote argument (`--promote-from`) to promote content from one environment to another
* First version of a unified Docker image

## Release 0.14.0

* Allow to define additional OpenAPI files to be added to the archive using the config file

## Release 0.13.0

* Rename default config name from `config.yaml` to `fhirscripts.config.yaml`

## Release 0.12.0

* Respect mirgated publish structure and package list (used for comparison)

## Release 0.11.0

* Add option to define the tools to install in the config using the `--config-file` argument
* Skip already installed tools
