#!/bin/bash

# URLs
del_build_cache_url="https://raw.githubusercontent.com/cybernop/fhir-scripts/refs/heads/main/scripts/delete_build_cache.sh"
rebuild_fhir_cache_url="https://raw.githubusercontent.com/cybernop/fhir-scripts/refs/heads/main/scripts/rebuild_fhir_cache.sh"
update_pytools_url="https://raw.githubusercontent.com/cybernop/fhir-scripts/refs/heads/main/scripts/update_pytools.sh"

function update_script() {
    curl -L $1 -o "$2.new.sh" 2> /dev/null && mv "$2.new.sh" "$2.sh"
    chmod +x $2.sh
    echo "Updated $2.sh"
}

update_script $del_build_cache_url delete_build_cache
update_script $rebuild_fhir_cache_url rebuild_fhir_cache
update_script $update_pytools_url update_pytools
