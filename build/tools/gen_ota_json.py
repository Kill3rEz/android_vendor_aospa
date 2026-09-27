#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Project PenguinOS
# SPDX-License-Identifier: Apache-2.0
#
"""Writes the updater's JSON for a signed OTA package.

Everything but the download URL is read out of the package itself, so the feed
cannot drift from what was actually built and signed.
"""

import argparse
import hashlib
import json
import os
import sys
import zipfile


def read_metadata(ota_zip):
    """The package's metadata as a dict, from whichever copy the package has."""
    with zipfile.ZipFile(ota_zip) as zf:
        for name in ("META-INF/com/android/metadata", "metadata"):
            try:
                body = zf.read(name).decode()
            except KeyError:
                continue
            return dict(
                line.split("=", 1) for line in body.splitlines() if "=" in line
            )
    raise SystemExit(f"{ota_zip}: no metadata; is this an OTA package?")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ota_zip")
    parser.add_argument(
        "--url",
        required=True,
        help="Download URL. {filename}, {device} and {version} are substituted.",
    )
    parser.add_argument("--device", help="Defaults to the package's own device")
    parser.add_argument("--version", help="Defaults to the package's own version")
    parser.add_argument(
        "--type",
        dest="build_type",
        default="unofficial",
        help="Must match ro.aospa.build.variant on the devices being served",
    )
    parser.add_argument("-o", "--output", help="Defaults to <device>.json beside the package")
    args = parser.parse_args()

    meta = read_metadata(args.ota_zip)
    filename = os.path.basename(args.ota_zip)

    # A full package names the device it came from as pre-device; an incremental one also
    # carries post-device. A device that answers to more than one codename lists them all,
    # separated by pipes, and the first is the one the updater asks for.
    device = args.device or meta.get("pre-device") or meta.get("post-device", "")
    device = device.split("|")[0].strip()
    if not device:
        raise SystemExit("No device in the package metadata; pass --device")

    # PenguinOS-<version>-<date>[-gms]-<device>.zip
    parts = filename.removesuffix(".zip").split("-")
    version = args.version or (parts[1] if len(parts) > 3 else "")
    build_type = args.build_type

    entry = {
        "datetime": int(meta["post-timestamp"]),
        "filename": filename,
        "id": sha256_of(args.ota_zip),
        "romtype": build_type,
        "size": os.path.getsize(args.ota_zip),
        "url": args.url.format(filename=filename, device=device, version=version),
        "version": version,
    }

    update = {
        "datetime": entry["datetime"],
        "files": [
            {
                "filename": filename,
                # The updater drops any build whose sdk level is below the device's, and an
                # absent one reads as zero, so this is not optional.
                "os_sdk_level": int(meta.get("post-sdk-level", 0)),
                # Byte ranges into the package, which is what lets the updater stream the
                # install rather than download the whole zip first.
                "ota_property_files": meta.get("ota-property-files", "").strip(),
                "sha256": entry["id"],
                "size": entry["size"],
                "url": entry["url"],
            }
        ],
        "type": build_type,
        "version": version,
    }

    output = args.output or os.path.join(os.path.dirname(args.ota_zip) or ".", f"{device}.json")
    with open(output, "w") as f:
        json.dump([update], f, indent=2)
        f.write("\n")

    print(f"Wrote {output}")
    print(f"  device  {device}")
    print(f"  version {version}")
    print(f"  type    {build_type}")
    print(f"  sdk     {update['files'][0]['os_sdk_level']}")
    print(f"  size    {entry['size']}")
    if not update["files"][0]["ota_property_files"]:
        print("  note    no ota-property-files; the updater will not stream this one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
