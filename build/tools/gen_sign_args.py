#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Project PenguinOS
# SPDX-License-Identifier: Apache-2.0
#
"""Prints the per-APEX signing arguments for a target files package.

sign_target_files_apks only remaps the keys it finds under the directory given
to -d. APEXes carry two keys of their own -- one for the payload image and one
for the container -- which have to be named on the command line, so the list is
built from the package being signed rather than kept as a list that goes stale
as APEXes come and go.
"""

import argparse
import os
import re
import sys
import zipfile

NAME_RE = re.compile(r'name="([^"]+)"')
PRESIGNED_RE = re.compile(r'private_key="PRESIGNED"')

# APKs that ship inside an APEX, and so are signed with a key of their own
# rather than one of the platform keys.
APEX_EMBEDDED_APKS = (
    "AdServicesApk.apk",
    "FederatedCompute.apk",
    "HalfSheetUX.apk",
    "HealthConnectBackupRestore.apk",
    "HealthConnectController.apk",
    "OsuLogin.apk",
    "SafetyCenterResources.apk",
    "ServiceConnectivityResources.apk",
    "ServiceUwbResources.apk",
    "ServiceWifiResources.apk",
    "TelecomServiceResources.apk",
    "TelecomUi.apk",
    "WebAppService.apk",
    "WifiDialog.apk",
    "com.android.appsearch.apk.apk",
)


def names_in(target_files, meta, skip_presigned=False):
    try:
        with zipfile.ZipFile(target_files) as zf:
            body = zf.read(meta).decode()
    except KeyError:
        return []
    names = []
    for line in body.splitlines():
        if not (m := NAME_RE.search(line)):
            continue
        if skip_presigned and PRESIGNED_RE.search(line):
            continue
        names.append(m.group(1))
    return names


def unlisted_apks(target_files, listed):
    with zipfile.ZipFile(target_files) as zf:
        apks = {os.path.basename(n) for n in zf.namelist()
                if n.endswith(".apk") and not n.startswith(("META/", "IMAGES/"))}
    return sorted(apks - set(listed))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target_files")
    parser.add_argument("certs_dir")
    args = parser.parse_args()

    certs = os.path.abspath(os.path.expanduser(args.certs_dir))
    out = []

    listed = names_in(args.target_files, "META/apkcerts.txt")
    for apk in listed:
        if apk in APEX_EMBEDDED_APKS:
            out.append(f"--extra_apks {apk}={certs}/releasekey")

    # Prebuilt APKs that are not app modules (e.g. prebuilt_overlay) are missing from
    # apkcerts.txt, and sign_target_files_apks refuses to sign a package with them.
    for apk in unlisted_apks(args.target_files, listed):
        out.append(f"--extra_apks {apk}={certs}/releasekey")

    missing = []
    for apex in names_in(args.target_files, "META/apexkeys.txt", skip_presigned=True):
        key = os.path.join(certs, apex.removesuffix(".apex").removesuffix(".capex"))
        if not os.path.exists(key + ".pk8"):
            missing.append(apex)
            continue
        out.append(f"--extra_apks {apex}={key}")
        out.append(f"--extra_apex_payload_key {apex}={key}.pem")

    if missing:
        print(
            "No signing key for: " + " ".join(missing) + "\n"
            "Generate them before signing, or they keep the build's test keys.",
            file=sys.stderr,
        )
        return 1

    print(" ".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
