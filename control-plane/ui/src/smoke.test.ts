import { describe, expect, it } from "vitest";
import { smokeLabel } from "./smoke.js";

describe("ui smoke", () => {
  it("returns the placeholder label", () => {
    expect(smokeLabel()).toBe("dcp-ui-ok");
  });
});
