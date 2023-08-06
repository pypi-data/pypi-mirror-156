#!/usr/bin/env python

import os
from Manifests.sims import sims_cache_manifest

def sims():
    print("\nTargetting Sims Cache Files")
    separator = os.sep  # \ or / depending on macOS/Windows
    print("\nFetching Sims Cache File Manifest")
    (base_url, launcher_url, launcher_files, package_files) = sims_cache_manifest

    root_dir = os.getcwd()
    os.chdir(r'Electronic Arts')  # EA Root Directory
    ea_root_dir = os.getcwd()
    os.chdir(base_url)
    print("\nDeleting *.package files...")
    for file in package_files:
        os.remove(file)
    os.chdir(ea_root_dir)
    print("\nDeleted.\n")

    os.chdir(launcher_url)
    launcher_root_dir = os.getcwd()
    print("\nDeleting launcher cache files...")
    for k, v in launcher_files.items():
        os.chdir(k)
        for value in v:
            os.system(f"rm {value}")
        os.chdir(launcher_root_dir)
    print("\nDeleted.\n")
    print("\nDone.\n")


if __name__ == '__main__':
    # User Prompts
    cache_name = "sims"

    if cache_name == "sims":
        sims()
    else:
        print('Error')
