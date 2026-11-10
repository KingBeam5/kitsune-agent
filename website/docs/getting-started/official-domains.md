---
title: Official Sources & Safety
description: Where Kitsune Agent comes from, and how to avoid installing the wrong software.
---

# Official Sources & Safety

Kitsune Agent is a fork of [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research (MIT licensed). The two share code and a documentation lineage, so make sure you are installing the one you mean to.

## Official Kitsune Agent sources

| Source | What it is |
|---|---|
| [github.com/KingBeam5/kitsune-agent](https://github.com/KingBeam5/kitsune-agent) | Source code and issue tracker. The default branch is `kitsune`. |

Kitsune Agent has no other official download location yet: no website installer, no Desktop packages, no container image.

## What is not Kitsune Agent

These belong to upstream Hermes Agent and Nous Research. They install or serve **Hermes Agent**:

- `hermes-agent.nousresearch.com`, including its `install.sh` and `install.ps1` scripts
- `hermes-assets.nousresearch.com` release artifacts
- the `nousresearch/hermes-agent` Docker image and the Hermes Termux package
- the Hermes Desktop downloads

**Nous Portal** (`portal.nousresearch.com`) is a Nous Research account and inference service. Kitsune Agent can use it as an optional model provider, but it is not part of Kitsune Agent.

## Staying safe

- Check the owner and repository name before you clone or run anything.
- Do not pipe a remote script into a shell unless you have read it and trust the host.
- Keep API keys in `~/.hermes/.env`. Do not paste them into issues, chats, or screenshots.
- Treat unsolicited messages offering "official" downloads, support, or airdrops as scams.
