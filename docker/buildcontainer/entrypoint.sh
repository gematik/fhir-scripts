#!/bin/sh

fhirscripts install --config-file
fhirscripts update

if [ -f ./package.json ]; then
    fhirscripts cache package
fi

fhirscripts $@
