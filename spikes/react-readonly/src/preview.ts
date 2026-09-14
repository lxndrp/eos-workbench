export type FixturePreviewBlock = {
  type: "heading" | "paragraph" | "html" | "image";
  text?: string;
  blocked?: string;
};

export type SafePreviewBlock =
  | { type: "heading"; text: string }
  | { type: "paragraph"; text: string }
  | { type: "blocked"; label: string; detail: string };

export function safePreviewBlocks(
  blocks: FixturePreviewBlock[],
): SafePreviewBlock[] {
  return blocks.map((block) => {
    if (block.type === "html" || block.type === "image") {
      return {
        type: "blocked",
        label: block.type === "html" ? "Raw HTML blocked" : "External media blocked",
        detail: block.blocked ?? "Blocked content",
      };
    }

    if (block.type === "heading") {
      return { type: "heading", text: block.text ?? "" };
    }

    return { type: "paragraph", text: block.text ?? "" };
  });
}
