---
sidebar_position: 9
title: "Personality & SOUL.md"
description: "Customize Kitsune Agent's personality with a global SOUL.md, built-in personalities, and custom persona definitions"
---

# Personality & SOUL.md

Kitsune Agent's personality is fully customizable. `SOUL.md` is the **primary identity** — it's the first thing in the system prompt and defines who the agent is.

- `SOUL.md` — a durable persona file that lives in `HERMES_HOME` and serves as the agent's identity (slot #1 in the system prompt)
- built-in or custom `/personality` presets — session-level system-prompt overlays

If you want to change who Kitsune is — or replace it with an entirely different agent persona — edit `SOUL.md`.

## How SOUL.md works now

Kitsune now seeds a default `SOUL.md` automatically in:

```text
~/.hermes/SOUL.md
```

More precisely, it uses the current instance's `HERMES_HOME`, so if you run Kitsune with a custom home directory, it will use:

```text
$HERMES_HOME/SOUL.md
```

### Important behavior

- **SOUL.md is the agent's primary identity.** It occupies slot #1 in the system prompt, replacing the hardcoded default identity.
- Kitsune creates a starter `SOUL.md` automatically if one does not exist yet
- Existing user `SOUL.md` files are never overwritten
- Kitsune loads `SOUL.md` only from `HERMES_HOME`
- Kitsune does not look in the current working directory for `SOUL.md`
- If `SOUL.md` exists but is empty, or cannot be loaded, Kitsune falls back to a built-in default identity
- If `SOUL.md` has content, that content is injected verbatim after security scanning and truncation
- SOUL.md is **not** duplicated in the context files section — it appears only once, as the identity

That makes `SOUL.md` a true per-user or per-instance identity, not just an additive layer.

## Why this design

This keeps personality predictable.

If Kitsune loaded `SOUL.md` from whatever directory you happened to launch it in, your personality could change unexpectedly between projects. By loading only from `HERMES_HOME`, the personality belongs to the Kitsune instance itself.

That also makes it easier to teach users:
- "Edit `~/.hermes/SOUL.md` to change Kitsune's default personality."

## Where to edit it

For most users:

```bash
~/.hermes/SOUL.md
```

If you use a custom home:

```bash
$HERMES_HOME/SOUL.md
```

## What should go in SOUL.md?

Use it for durable voice and personality guidance, such as:
- tone
- communication style
- level of directness
- default interaction style
- what to avoid stylistically
- how Kitsune should handle uncertainty, disagreement, or ambiguity

Use it less for:
- one-off project instructions
- file paths
- repo conventions
- temporary workflow details

Those belong in `AGENTS.md`, not `SOUL.md`.

## Good SOUL.md content

A good SOUL file is:
- stable across contexts
- broad enough to apply in many conversations
- specific enough to materially shape the voice
- focused on communication and identity, not task-specific instructions

### Example

```markdown
# Personality

You are a pragmatic senior engineer with strong taste.
You optimize for truth, clarity, and usefulness over politeness theater.

## Style
- Be direct without being cold
- Prefer substance over filler
- Push back when something is a bad idea
- Admit uncertainty plainly
- Keep explanations compact unless depth is useful

## What to avoid
- Sycophancy
- Hype language
- Repeating the user's framing if it's wrong
- Overexplaining obvious things

## Technical posture
- Prefer simple systems over clever systems
- Care about operational reality, not idealized architecture
- Treat edge cases as part of the design, not cleanup
```

## What Kitsune injects into the prompt

`SOUL.md` content goes directly into slot #1 of the system prompt — the agent identity position. No wrapper language is added around it.

The content goes through:
- prompt-injection scanning
- truncation if it is too large

If the file is empty, whitespace-only, or cannot be read, Kitsune falls back to a built-in default identity ("You are Kitsune Agent, built by Nous Research. Be direct: match the length of your reply to the weight of the ask..."). This fallback also applies when `skip_context_files` is set (e.g., in subagent/delegation contexts).

## Security scanning

`SOUL.md` is scanned like other context-bearing files for prompt injection patterns before inclusion.

That means you should still keep it focused on persona/voice rather than trying to sneak in strange meta-instructions.

## SOUL.md vs AGENTS.md

This is the most important distinction.

### SOUL.md
Use for:
- identity
- tone
- style
- communication defaults
- personality-level behavior

### AGENTS.md
Use for:
- project architecture
- coding conventions
- tool preferences
- repo-specific workflows
- commands, ports, paths, deployment notes

A useful rule:
- if it should follow you everywhere, it belongs in `SOUL.md`
- if it belongs to a project, it belongs in `AGENTS.md`

## SOUL.md vs `/personality`

`SOUL.md` is your durable default personality.

`/personality` is a session-level overlay that changes or supplements the current system prompt.

So:
- `SOUL.md` = baseline voice
- `/personality` = temporary mode switch

Examples:
- keep a pragmatic default SOUL, then switch to a custom `teacher` personality (see [Custom personalities](#custom-personalities-in-config)) for a tutoring conversation
- keep a concise SOUL, then switch to a custom `brainstorm` personality for open-ended ideas

## Built-in personalities

Kitsune Agent ships one built-in personality, **Ryu**, and it is active by default. Tasuki and Nyx are planned.

| Personality | Character |
|---|---|
| **ryu** (default) | Calm, precise, slightly dry. Direct and technical, with no hype or filler. Says plainly when something is wrong or incomplete, sticks to what was asked, and never overrides your security choices. |

Ryu is active whenever `display.personality` is unset. `/personality none` turns the overlay off.

## Switching personalities with commands

### CLI

```text
/personality
/personality ryu
/personality none
```

### Messaging platforms

```text
/personality ryu
```

These are convenient overlays, but your global `SOUL.md` still gives Kitsune its persistent default personality unless the overlay meaningfully changes it.

## Custom personalities in config

Built-in personalities are always available on every surface (CLI, messaging platforms, TUI, and the desktop app). You can add your own — or override a built-in by reusing its name — in `~/.hermes/config.yaml` under `agent.personalities` (a top-level `personalities:` block works too; `agent.personalities` wins if the same name appears in both).

```yaml
agent:
  personalities:
    codereviewer: >
      You are a meticulous code reviewer. Identify bugs, security issues,
      performance concerns, and unclear design choices. Be precise and constructive.
```

Then switch to it with:

```text
/personality codereviewer
```

Your selection is stored as a name in `display.personality`. Personalities never touch `agent.system_prompt` — that field is reserved for a manual system prompt you write yourself, and it applies only when no personality is selected.

## Resetting to the default

To cancel the active personality overlay and return to base behavior (your `SOUL.md` persona, plus `agent.system_prompt` if you set one), use any of:

To return to the default personality (Ryu), use `/personality default`.

```text
/personality none
/personality neutral
```

Both of these clear the selection (`display.personality`) and the change takes effect on your next message. Running `/personality` with no arguments also lists `none` alongside the available presets and marks the active one.

:::note One-time reset on upgrade
Older Kitsune versions saved personality state inconsistently across surfaces, which could re-enable a personality you had previously turned off. On your first run after upgrading, any saved personality selection is reset to `none` once (the migration prints which personality was cleared). Re-enable it with `/personality <name>` if you still want it. Manual `agent.system_prompt` text is never touched.
:::

## Recommended workflow

A strong default setup is:

1. Keep a thoughtful global `SOUL.md` in `~/.hermes/SOUL.md`
2. Put project instructions in `AGENTS.md`
3. Use `/personality` only when you want a temporary mode shift

That gives you:
- a stable voice
- project-specific behavior where it belongs
- temporary control when needed

## How personality interacts with the full prompt

At a high level, the prompt stack includes:
1. **SOUL.md** (agent identity — or built-in fallback if SOUL.md is unavailable)
2. tool-aware behavior guidance
3. memory/user context
4. skills guidance
5. context files (`AGENTS.md`, `.cursorrules`)
6. timestamp
7. platform-specific formatting hints
8. optional system-prompt overlays such as `/personality`

`SOUL.md` is the foundation — everything else builds on top of it.

## Related docs

- [Context Files](./context-files.md)
- [Configuration](../configuration.md)
- [Tips & Best Practices](../../guides/tips.md)
- [SOUL.md Guide](../../guides/use-soul-with-hermes.md)

## CLI appearance vs conversational personality

Conversational personality and CLI appearance are separate:

- `SOUL.md`, `agent.system_prompt`, and `/personality` affect how Kitsune speaks
- `display.skin` and `/skin` affect how Kitsune looks in the terminal

For terminal appearance, see [Skins & Themes](./skins.md).
