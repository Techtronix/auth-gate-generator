#!/usr/bin/env python
"""
Generate an authentication gate using an IP list for InspIRCd

Copyright (c) 2024 Michael Hazell <michaelhazell@hotmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import requests
from sys import stderr, stdout
import uuid


parser = argparse.ArgumentParser(
    description="Generate an authentication gate configuration file for InspIRCd"
)
parser.add_argument(
    "-m",
    "--message",
    type=str,
    default="You need to identify via SASL to use this server.",
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    default="",
    help="Output file, where the configuration will be written. If not specified, output will be written to stdout.",
)
parser.add_argument(
    "-p",
    "--parent",
    type=str,
    default="main",
    help="Parent connect class to inherit from, e.g. main.",
)
parser.add_argument(
    "-u",
    "--url",
    type=str,
    required=False,
    default="https://raw.githubusercontent.com/X4BNet/lists_vpn/main/output/vpn/ipv4.txt",
    help="URL of the IP list. It is expected to be a plaintext list, one IP/CIDR per line.",
)


def main():
    # Parse args
    args = parser.parse_args()

    # Fetch the IP list from URL
    res = requests.get(args.url, timeout=10)
    if res.status_code != 200:
        print("URL request did not return OK status", file=stderr)
        print(res.text, file=stderr)

    # Parse IPs
    ip_addresses = list(res.iter_lines(decode_unicode=True))

    # Generate a unique (ish) class name in case this script is invoked multiple times with separate lists
    # InspIRCd will not accept name collisions
    class_name = f"auth-gate-{uuid.uuid4()}"

    # There will need to be two connect blocks:
    # 1. Allow registered connections with authentication
    # 2. Deny registered connections without authentication

    # The following strings will store the allow="" and deny="" entries
    allow = ""
    deny = ""

    # Build up allow and deny strings with formatting included
    for i, ip in enumerate(ip_addresses):
        # Yes, I can condense this, but this is better for readability
        if i < len(ip_addresses) - 1:
            allow += f'    allow="{ip}"\n'
            deny += f'    deny="{ip}"\n'
        else:
            allow += f'    allow="{ip}"'
            deny += f'    deny="{ip}"'

    # Final output will look akin to this:
    # <connect name="auth-gate-73494747-e19e-4cdf-bc3b-c0f5b94af2e2"
    #     allow="x.x.x.x/cidr"
    #     allow="y.y.y.y/cidr"
    #     registered="true"
    #     requireaccount="yes"
    #     parent="main">
    # <connect
    #     deny="x.x.x.x/cidr"
    #     deny="y.y.y.y/cidr"
    #     registered="true"
    #     reason="You need to identify via SASL to use this server.">
    allow_block = f'<connect name="{class_name}"\n{allow}\n    registered="true"\n    requireaccount="yes"\n    parent="{args.parent}">'
    deny_block = (
        f'<connect\n{deny}\n    registered="true"\n    reason="{args.message}">'
    )

    use_file: bool = len(args.output) != 0
    with open(args.output, "w", encoding="utf8") if use_file else stdout as f:
        f.write(
            "# Authentication gate configuration auto-generated by inspircd-auth-gate-generator.py\n"
        )
        f.write(allow_block)
        f.write("\n")
        f.write(deny_block)
        f.write("\n")


if __name__ == "__main__":
    main()
