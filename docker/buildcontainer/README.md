# Build Container

This image provides a simple way to build, publish and deploy FHIR IGs.

Build this image with

```bash
docker build --tag <image name>
```

Execute commands from fhirscripts with

```bash
docker run --rm [-t] -v <project dir>:/project [-v <custom config>:/project/fhirscripts.config.yaml] <image name> <command> [<args>...]
```

Note: Providing the `-t` argument allows to print the output of the commands during execution. Without the output is only printed at the end of the execution.
