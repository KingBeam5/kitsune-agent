import { contrastRatio } from "@hermes/shared";
import { describe, expect, it } from "vitest";

import { BUILTIN_THEMES, defaultTheme } from "./presets";

// Kitsune Agent ships a single look, Ryu, in two sizes. The IDs stay `default`
// and `default-large` so they match the backend's _BUILTIN_DASHBOARD_THEMES.
describe("dashboard themes", () => {
  it("ships only Ryu (normal and large)", () => {
    expect(Object.keys(BUILTIN_THEMES).sort()).toEqual(["default", "default-large"]);
    expect(BUILTIN_THEMES.default.label).toBe("Ryu");
    expect(BUILTIN_THEMES["default-large"].label).toBe("Ryu (Large)");
  });

  it("uses the Kitsune near-black canvas and keeps text legible on it", () => {
    expect(defaultTheme.palette.background.hex).toBe("#0B0B10");
    expect(contrastRatio(defaultTheme.palette.midground.hex, defaultTheme.palette.background.hex)).toBeGreaterThanOrEqual(7);
  });
});
