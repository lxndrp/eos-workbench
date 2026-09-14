import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { safePreviewBlocks } from "./preview.ts";

const fixturePath = fileURLToPath(
  new URL("../../fixtures/read-only-workflow.json", import.meta.url),
);

test("keeps active fixture content out of the React preview model", async () => {
  const fixture = JSON.parse(await readFile(fixturePath, "utf8"));
  const blocks = safePreviewBlocks(fixture.document.preview.blocks);

  assert.deepEqual(
    blocks.map((block) => block.type),
    ["heading", "paragraph", "blocked", "blocked"],
  );
  assert.equal(blocks[2].label, "Raw HTML blocked");
  assert.equal(blocks[3].label, "External media blocked");
  assert.equal("source" in blocks[2], false);
  assert.equal("source" in blocks[3], false);
});
