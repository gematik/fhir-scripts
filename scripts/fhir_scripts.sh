#!/bin/bash

# URLs
fhir_scripts_url="https://raw.githubusercontent.com/cybernop/fhir-scripts/refs/heads/main/scripts/fhir_scripts.sh"

function delete_build_cache() {
    rm -rf input-cache/schemas
    rm -rf input-cache/txcache
    echo "✅ Build cache cleared."
}

function update_script() {
    curl -L $1 -o "$2.new.sh" 2> /dev/null && mv "$2.new.sh" "$2.sh"
    chmod +x $2.sh
    echo "✅ Updated $2.sh."
}

function update_fhir_script() {
    update_script $fhir_scripts_url fhir_scripts
}

function update_pytools() {
    sudo pipx install --global -f git+https://github.com/onyg/epa-tools.git
    sudo pipx install --global -f git+https://github.com/onyg/req-tooling.git
    echo
    echo "✅ Installed Python tooling."
}

function rebuild_fhir_cache() {
    rm -rf $HOME/.fhir/packages/*
    fhir restore
    echo
    echo "✅ FHIR cache rebuilt."
}

# Handle command-line argument or menu
case "$1" in
  update) update_fhir_script ;;
  pytools) update_pytools ;;
  fhircache) rebuild_fhir_cache ;;
  bdcache) delete_build_cache ;;
  exit) exit 0 ;;
  *)
    # Compute default choice
    default_choice=0 # Exit on default

    echo "Please select an option:"
    echo "1) Update script"
    echo "2) Update pytools"
    echo "3) Rebuild FHIR cache"
    echo "4) Delete build cache"
    echo "0) Exit"
    echo

    # Read with timeout, but default if nothing entered
    echo -n "Choose an option [default: $default_choice]: "
    read -t 5 choice || choice="$default_choice"
    choice="${choice:-$default_choice}"
    echo "You selected: $choice"

    case "$choice" in
      1) update_fhir_script ;;
      2) update_pytools ;;
      3) rebuild_fhir_cache ;;
      4) delete_build_cache ;;
      0) exit 0 ;;
      *) echo "Invalid option." ;;
    esac
  ;;

esac
