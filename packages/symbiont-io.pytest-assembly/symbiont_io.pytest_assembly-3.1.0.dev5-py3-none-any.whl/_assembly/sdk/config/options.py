CONFIG_OPTIONS = [
    [
        "--contract-path",
        str,
        "List of paths to look up contract files from",
        {"action": "append"},
    ],
    [
        "--timeout",
        int,
        "timeout",
    ],
    ["--connection-file", str, "network connection file with configuration details"],
    ["--network-config", str, "network connection file with configuration details"],
    ["--output-dir", str, "output location for any saved data"],
]
