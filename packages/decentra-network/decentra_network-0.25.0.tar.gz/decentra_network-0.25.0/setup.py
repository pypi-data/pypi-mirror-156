#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from setuptools import setup

setup(
    name="decentra_network",
    version="0.25.0",
    description=
    """This is an open source decentralized application network. In this network, you can develop and publish decentralized applications.""",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://decentra-network.github.io/Decentra-Network/",
    author="Decentra Network Developers",
    author_email="atadogan06@gmail.com",
    license="MPL-2.0",
    packages=[
        "",
        "accounts",
        "app",
        "blockchain",
        "blockchain.block",
        "blockchain.candidate_block",
        "consensus",
        "gui_lib",
        "gui_lib.libs",
        "gui_lib.libs.baseclass",
        "lib",
        "node",
        "transactions",
        "wallet",
    ],
    include_package_data=True,
    package_dir={"": "src"},
    entry_points={
        "console_scripts":
        ["dngui = gui:start", "dncli=cli:start", "dnapi=api:start"],
    },
    python_requires=">=3.8",
    zip_safe=False,
)
