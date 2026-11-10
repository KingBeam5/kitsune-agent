---
sidebar_position: 2
title: "Installation"
description: "How to get Kitsune Agent: pre-release status, installing from source, and what is not available yet"
---

# Installation

:::caution Pre-release
Kitsune Agent is under active development as part of Kitsune Linux. It has no public installer or packaged release yet. It will ship pre-installed on Kitsune Linux; until then it is installed from source.
:::

## What is available

| Method | Status |
|---|---|
| From source (this repository) | Available, for developers |
| Pre-installed on Kitsune Linux | Planned for the official release |
| Desktop packages (macOS, Windows), Docker image, Nix, Termux, hosted installer scripts | Not published for Kitsune Agent |

:::warning Do not use upstream's installers
The installer scripts, Desktop downloads, and Docker image shown in upstream Hermes Agent material belong to Nous Research and install **Hermes Agent**, not Kitsune Agent. See [Official Sources & Safety](./official-domains.md).
:::

## From source

```bash
git clone https://github.com/KingBeam5/kitsune-agent.git
cd kitsune-agent
```

The default branch is `kitsune`. Developer setup (Python environment, dependencies, running the tests) is described in [Contributing](../developer-guide/contributing.md). Those steps are inherited from upstream and are being re-verified for Kitsune Agent.

## Running it

The package defines a `kitsune` command. The inherited `hermes` command still exists and runs the same program.

```bash
kitsune --version
kitsune              # start a chat
kitsune dashboard    # web dashboard at http://127.0.0.1:9119
```

The first `kitsune dashboard` run builds the web UI, which takes several minutes on modest hardware. Later runs reuse the build.

## Where data lives

Configuration, sessions, skills, and memory are stored in `~/.hermes` (the `HERMES_HOME` directory). API keys and other secrets belong in `~/.hermes/.env`, not in `config.yaml`.

## Defaults

- Skin: **Ryu** (the only built-in skin). See [Skins & Themes](../user-guide/features/skins.md).
- Personality: **Ryu** (the default personality). See [Personality & SOUL.md](../user-guide/features/personality.md).
- Shared metrics: **off**, with no upload endpoint. Nothing is sent anywhere.
