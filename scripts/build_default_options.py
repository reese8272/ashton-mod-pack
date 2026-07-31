#!/usr/bin/env python3
"""Generate config/defaultoptions/ from a reference Prism instance's options.txt.

WHY THIS EXISTS
---------------
Shipping options.txt in the pack overwrites every player's keybinds and settings
on every update. Instead the pack ships config/defaultoptions/, which the Default
Options mod applies on FIRST LAUNCH ONLY. A player who has rebound a key keeps
their bind; a player still on the vanilla default picks up the pack's.

Layout is defined by DefaultOptions 1.21.1 source
(DefaultOptionsContext.getDefaultOptionsFolder -> "config/defaultoptions"):

    config/defaultoptions/options.txt       non-keybind vanilla options
    config/defaultoptions/keybindings.txt   key_<name>:<key>:<modifiers>
    config/defaultoptions/extra/            copied only if the target is absent

Usage:  python3 scripts/build_default_options.py [path/to/instance/minecraft]
"""
import pathlib
import sys

DEFAULT_INSTANCE = pathlib.Path(
    "/home/reese/Terra Aeterna 1.5 Complete (7-22-2026)/minecraft"
)
PACK = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = PACK / "config" / "defaultoptions"

# Options the PACK legitimately decides for everyone: gameplay feel and UI
# behaviour that does not depend on the player's hardware or their body.
# Everything not listed here is deliberately left to the player.
PACK_LEVEL_OPTIONS = {
    "autoJump": "pack convention; almost universally disabled in modded",
    "toggleSprint": "pack convention",
    "toggleCrouch": "pack convention",
    "bobView": "pack convention",
    "attackIndicator": "pack convention",
    "mainHand": "pack convention",
    "advancedItemTooltips": "pack convention",
    "pauseOnLostFocus": "pack convention",
    "showSubtitles": "pack convention",
    "discrete_mouse_scroll": "pack convention",
    "skipMultiplayerWarning": "removes a nag screen on every server join",
    "hideMatchedNames": "pack convention",
    "chatColors": "pack convention",
    "chatLinks": "pack convention",
    "chatLinksPrompt": "pack convention",
    "operatorItemsTab": "pack convention",
    "darkMojangStudiosBackground": "cosmetic, matches the pack's intro",
    "hideLightningFlashes": "pack convention",
    "realmsNotifications": "pack has no Realms; suppress the notification",
    "narratorHotkey": "pack convention",
    "notificationDisplayTime": "pack convention",
}

# Documented so reviewers can see these were considered and rejected, not missed.
DELIBERATELY_EXCLUDED = {
    "hardware": [
        "fullscreenResolution", "fullscreen", "overrideWidth", "overrideHeight",
        "renderDistance", "simulationDistance", "maxFps", "graphicsMode",
        "mipmapLevels", "biomeBlendRadius", "entityDistanceScaling", "particles",
        "prioritizeChunkUpdates", "enableVsync", "gamma", "guiScale", "ao",
        "entityShadows", "renderClouds", "soundDevice", "glDebugVerbosity",
    ],
    "personal": [
        "mouseSensitivity", "mouseWheelSensitivity", "rawMouseInput",
        "invertYMouse", "touchscreen", "fov", "fovEffectScale",
        "screenEffectScale", "darknessEffectScale", "damageTiltStrength",
        "highContrast", "onboardAccessibility", "lang", "narrator",
        "chatVisibility", "chatOpacity", "chatScale", "chatWidth",
        "chatHeightFocused", "chatHeightUnfocused", "chatLineSpacing",
        "chatDelay", "textBackgroundOpacity", "menuBackgroundBlurriness",
    ],
    "per-account or transient state": [
        "lastServer", "tutorialStep", "joinedFirstServer", "hideBundleTutorial",
        "telemetryOptInExtra", "allowServerListing", "onlyShowSecureChat",
        "version", "resourcePacks", "incompatibleResourcePacks",
    ],
}


def main():
    instance = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INSTANCE
    src = instance / "options.txt"
    if not src.is_file():
        sys.exit(f"error: no options.txt at {src}")

    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    keybinds, options, skipped = [], [], []

    for line in lines:
        if not line.strip():
            continue
        if line.startswith("key_"):
            keybinds.append(line)
            continue
        key = line.split(":", 1)[0]
        # sound levels and skin layers are personal; never force them
        if key.startswith(("soundCategory_", "modelPart_")):
            skipped.append(key)
            continue
        (options if key in PACK_LEVEL_OPTIONS else skipped).append(
            line if key in PACK_LEVEL_OPTIONS else key
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "keybindings.txt").write_text("\n".join(keybinds) + "\n", encoding="utf-8")
    (OUT_DIR / "options.txt").write_text("\n".join(sorted(options)) + "\n", encoding="utf-8")

    print(f"source:        {src}")
    print(f"keybindings.txt  {len(keybinds)} binds")
    print(f"options.txt      {len(options)} pack-level options")
    print(f"left to player   {len(skipped)} options")
    print(f"\nwrote {OUT_DIR}")

    missing = sorted(set(PACK_LEVEL_OPTIONS) - {o.split(':', 1)[0] for o in options})
    if missing:
        print(f"\nnote: allowlisted but absent from source options.txt: {', '.join(missing)}")


if __name__ == "__main__":
    main()
