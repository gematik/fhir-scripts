# FHIR Scripts

## Rebuild FHIR Cache

Clears the FHIR cache and rebuilds it from FHIR packages. Optionally it can install packages from a local directory and cache dependency packages in this directory.

```bash
./fhir_scripts.sh fhircache [<pkgdir>]
```

When `<pkgdir>` is provided, the dependencies from `package.json` are read and available packages from `<pkgdir>` will be installed. Additionally, direct dependencies that are not present in `<pkgdir>` will be downloaded for later usages.
