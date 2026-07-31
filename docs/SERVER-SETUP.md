# Server setup — BisectHosting (8 GB)

Getting Terra Aeterna running on the box, and updating it later.

---

## 1. Set the game version

In the panel, set the server to **Minecraft 1.21.1** with **NeoForge 21.1.234**.

Nothing was preinstalled, so if the panel offers a NeoForge installer pick it and
choose those exact versions. If it only offers "NeoForge latest", still force
1.21.1 — **the loader version must match the pack**. A mismatch here produces
confusing mod-loading errors that look like broken mods.

Start the server once, let it generate its files, then **stop it**. Everything
below assumes it is stopped.

---

## 2. Accept the EULA

Open `eula.txt` in the file manager and set:

```
eula=true
```

---

## 3. Upload the mods

Build the server half locally:

```bash
python3 scripts/build_server_pack.py --zip
```

That produces `build/server-pack.zip` (~478 MB) containing 191 mods — every mod
marked `server` or `both`, hash-verified. Client-only mods are skipped, which is
why it is far smaller than the 1.15 GB players download.

Upload it via the panel's file manager or SFTP, then **extract it in the server
root**. You should end up with `mods/` alongside `server.properties`.

> Use SFTP for something this size. Browser uploads of ~500 MB tend to time out.

---

## 4. server.properties

```properties
# allow-flight MUST be true. Create Aeronautics, immersive aircraft, gliders and
# elytra all trigger the vanilla anti-cheat, which kicks players for "flying".
allow-flight=true

max-players=10
online-mode=true
difficulty=normal

# Server-side view distance. Keep this modest -- Distant Horizons renders long
# sightlines on the CLIENT, so a big server view-distance costs TPS for nothing.
view-distance=8
simulation-distance=6

motd=Terra Aeterna
spawn-protection=0
```

Bump `view-distance` later if TPS is comfortable. It is the first thing to lower
if it isn't.

---

## 5. Memory

**Do not set the heap to the full 8 GB.** The plan's 8 GB is the *container*
limit; the JVM needs room beyond the heap for metaspace, GC structures and
off-heap buffers. Ask for all of it and the server gets OOM-killed under load,
which looks like a random crash.

Set the heap to about **6.5 GB**, leaving ~1.5 GB of headroom:

```
-Xms6G -Xmx6656M -XX:+UseG1GC -XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC
-XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40
-XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5
-XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15
-XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5
-XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1
```

These are the widely-used G1GC server flags. **G1 here, not ZGC** — ZGC suits the
client's larger heap, while G1 with a tuned pause target behaves better for a
server's tick loop at this size.

If the panel manages memory itself, just make sure the heap lands near 6.5 GB.

---

## 6. First start

Start it and watch the console. Expect **several minutes** on first boot — 191
mods plus Terralith, Tectonic and Incendium generating a fresh world.

Healthy signs:

- `Done (Ns)! For help, type "help"`
- no `Failed to load mods` / missing-dependency errors

If it crashes, read the **first** error in the log, not the last. Modded stack
traces cascade; the top one is the real cause.

Once it is up, run `/spark tps` in console (spark is already in the pack). **20
TPS is perfect; below ~18 sustained means trouble.** Lower `view-distance` and
`simulation-distance` before anything else.

---

## 7. Give Ashton his own login

Panel → **Users** → **Add Subuser** → his email → tick permissions → Invite.

Give him file manager, console, and start/stop. Withhold billing and server
deletion. This is the whole point of the managed host: he administers the server
without touching your account.

Docs: <https://help.bisecthosting.com/hc/en-us/articles/40088608898203-How-to-Add-Sub-Users-on-the-Starbase-Panel>

---

## 8. Put the server in everyone's list automatically

Once you have the address, players should not have to type an IP.

1. In your own game, add the server in Multiplayer so it appears in your list.
2. Run `/defaultoptions saveAll` in-game — this captures `servers.dat`.
3. Copy the generated `config/defaultoptions/servers.dat` into the pack repo.
4. Commit and push.

On first launch, the server is simply *there* in their multiplayer list. Players
who already added it keep their own list unchanged.

---

## 9. Updating the server later

When Ashton publishes a pack update:

```bash
git pull
python3 scripts/build_server_pack.py --zip
```

Only changed mods download; the rest are reused from the previous build. Stop the
server, upload, extract, start.

> **Delete removed mods.** Extracting over the top adds and replaces files but
> never deletes. If an update removed a mod, its jar stays behind and will
> usually crash the server or desync clients. Compare `mods/` against
> `build/server/mods/` and delete anything extra.

Client and server must run the same pack version. Players auto-update on launch,
so **update the server first**, or players will briefly fail to join.

---

## Troubleshooting

**Players kicked "flying is not enabled"** — `allow-flight=true` in
`server.properties`.

**"Mod mismatch" / connection refused on join** — client and server are on
different pack versions. Update the server.

**Random crashes under load, no clear error** — the heap is too close to the
plan limit and the container is being OOM-killed. Lower `-Xmx`.

**TPS below 18** — lower `simulation-distance` first, then `view-distance`. Use
`/spark profiler start` to find the actual culprit before guessing.

**Server won't start after an update** — a removed mod's jar is still in `mods/`.
See the deletion warning above.
