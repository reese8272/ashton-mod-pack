# Playing Terra Aeterna

Minecraft **1.21.1**. You need a paid Minecraft Java account. Pick one path.

---

## Option A — Prism Launcher (recommended: updates itself)

Set this up once and the pack keeps itself current. Every time you launch, it
checks for changes and downloads **only what changed** — usually a few KB, not
the whole gigabyte.

1. Install [Prism Launcher](https://prismlauncher.org/) and sign in.
2. Download `terra-aeterna-<version>.mrpack` from
   [Releases](../../releases/latest) and drag it onto the Prism window.
3. Download `packwiz-installer-bootstrap.jar` from
   [here](https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest).
   Right-click the instance → **Folder**, then go **into the `minecraft`
   subfolder** and put the jar there — next to `mods/`, not beside
   `instance.cfg`. Prism runs the pre-launch command from `minecraft/`, so a jar
   in the instance root gives `Unable to access jarfile`.
4. Right-click the instance → **Edit** → **Settings** → **Custom commands**,
   tick **Custom commands**, and paste into **Pre-launch command**:

   ```
   "$INST_JAVA" -jar "$INST_MC_DIR/packwiz-installer-bootstrap.jar" https://raw.githubusercontent.com/reese8272/ashton-mod-pack/main/pack.toml
   ```

   `$INST_MC_DIR` points at the instance's `minecraft/` folder, so this works
   regardless of what Prism sets the working directory to.

That's it. Launch normally; updates arrive on their own.

## Option B — Modrinth App (simplest, manual updates)

1. Install the [Modrinth App](https://modrinth.com/app).
2. Download the `.mrpack` from [Releases](../../releases/latest) and open it.

You'll need to re-download the pack when a new version is released.

---

## Memory and Java settings

Right-click the instance → **Edit** → **Settings** → **Memory**, and untick
**Java installation** override so Prism picks Java for you.

Pick the row matching **your** RAM — not someone else's:

| Your system RAM | Allocate | Java arguments |
|---|---|---|
| 8 GB | 4 GB | `-XX:+UseG1GC -XX:+UseStringDeduplication` |
| 16 GB | 6–8 GB | `-XX:+UseZGC -XX:+ZGenerational -XX:SoftMaxHeapSize=6G -XX:+UseStringDeduplication -XX:ConcGCThreads=2 -XX:ParallelGCThreads=4` |
| 32 GB+ | 10–12 GB | `-XX:+UseZGC -XX:+ZGenerational -XX:SoftMaxHeapSize=10G -XX:+UseStringDeduplication -XX:ConcGCThreads=4 -XX:ParallelGCThreads=8` |

**Do not allocate more than half your total RAM.** More is not better — a larger
heap means longer garbage-collection pauses, which you feel as stutter.

`ParallelGCThreads` should be roughly your CPU's core count; `ConcGCThreads`
about half of that. If you don't know, the defaults above are fine.

---

## Your settings are yours

**Your keybinds, sensitivity, FOV, volumes, and video settings are never
overwritten by an update.** Rebind whatever you like — it survives.

The pack ships a set of default keybinds that apply on your **first launch
only**. If you change one, it stays changed forever. If you never touched a key,
you'll pick up the pack's default for it.

The pack deliberately does *not* set your render distance, FPS cap, resolution,
mouse sensitivity, FOV, or volume levels. Those are yours to tune.

---

## Optional extras

The pack includes a 456 MB animated intro video, **off by default** because it's
40% of the download for a startup animation. If you want it, enable
**Reimagined Intro** in the packwiz-installer options window when it appears.

---

## Troubleshooting

**"Hash invalid" on launch** — a pack file didn't match its checksum. Usually
transient; relaunch. If it persists, report it: someone likely committed a stale
index.

**Out of memory / crash on world load** — you allocated too little, or far too
much. Recheck the table above.

**Poor FPS** — lower render distance and simulation distance first (these matter
most), then turn off shaders. Distant Horizons is heavy; its LOD settings are
worth tuning before you blame the pack.

**Can't connect: "mod mismatch"** — your pack is out of date. On Option A,
relaunch. On Option B, download the latest `.mrpack`.
