# Contributing

Hyprglass is a curated public subset of a real desktop, not a universal
Hyprland framework. Contributions should improve portability, correctness,
privacy or documentation without adding machine-specific data.

Before opening a pull request:

1. run `./tests/run.sh`;
2. run `shellcheck install.sh scripts/*.sh tests/*.sh .config/hypr/scripts/*.sh .config/waybar/scripts/*.sh`;
3. confirm screenshots, logs and fixtures contain no usernames, hostnames,
   network names, tokens or absolute personal paths;
4. document new required and optional dependencies in `PACKAGES.md`;
5. explain which hardware and Hyprland version were used for manual testing.

Do not submit credentials, network profiles or full copies of a home
directory. Keep changes focused and describe limitations honestly.
