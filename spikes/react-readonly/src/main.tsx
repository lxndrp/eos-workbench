import { createRoot } from "react-dom/client";
import fixture from "../../fixtures/read-only-workflow.json";
import { safePreviewBlocks, type FixturePreviewBlock } from "./preview";
import "./styles.css";

type Metadata = { label: string; value: string; source: string };
type Relation = { kind: string; title: string; state: string };

const content = fixture.document;
const previewBlocks = safePreviewBlocks(
  content.preview.blocks as FixturePreviewBlock[],
);

function SourceDetails() {
  return (
    <section aria-labelledby="source-heading" className="panel">
      <h2 id="source-heading">Read-only source</h2>
      <dl className="facts">
        <div><dt>Repository</dt><dd>{fixture.repository.name}</dd></div>
        <div><dt>Revision</dt><dd><code>{fixture.repository.revision}</code></dd></div>
        <div><dt>Path</dt><dd><code>{fixture.repository.path}</code></dd></div>
        <div><dt>Origin</dt><dd>{fixture.repository.source}</dd></div>
      </dl>
    </section>
  );
}

function MetadataDetails() {
  return (
    <section aria-labelledby="metadata-heading" className="panel">
      <h2 id="metadata-heading">Metadata</h2>
      <dl className="facts">
        {(content.knownMetadata as Metadata[]).map((item) => (
          <div key={item.label}>
            <dt>{item.label}</dt>
            <dd>{item.value} <small>({item.source})</small></dd>
          </div>
        ))}
        <div>
          <dt>Unknown field: <code>{content.unknownMetadata.key}</code></dt>
          <dd>{content.unknownMetadata.value} <small>({content.unknownMetadata.source})</small></dd>
        </div>
      </dl>
    </section>
  );
}

function SafePreview() {
  return (
    <section aria-labelledby="preview-heading" className="panel" aria-label="Safe Markdown preview">
      <h2 id="preview-heading">Safe Markdown preview</h2>
      {previewBlocks.map((block, index) => {
        if (block.type === "heading") return <h3 key={index}>{block.text}</h3>;
        if (block.type === "paragraph") return <p key={index}>{block.text}</p>;
        return (
          <aside className="blocked" key={index} aria-label={block.label}>
            <strong>{block.label}</strong>
            <span>{block.detail}</span>
          </aside>
        );
      })}
    </section>
  );
}

function App() {
  return (
    <main tabIndex={-1}>
      <header>
        <p className="eyebrow">EOS Workbench · synthetic comparison spike</p>
        <h1>{content.title}</h1>
        <p><span className="tag">{content.kind}</span> <span className="tag">{content.status}</span></p>
      </header>

      <div role="alert" className="integration-error">
        <strong>{content.integration.message}</strong>
        <span>{content.integration.detail}</span>
      </div>

      <div className="grid">
        <SourceDetails />
        <MetadataDetails />
      </div>

      <section aria-labelledby="relations-heading" className="panel">
        <h2 id="relations-heading">Relationships</h2>
        <ul>
          {(content.relations as Relation[]).map((relation) => (
            <li key={relation.title}>{relation.kind}: {relation.title} <span className="tag">{relation.state}</span></li>
          ))}
        </ul>
        {content.findings.map((finding) => (
          <p className="finding" key={finding.message}><strong>{finding.severity}:</strong> {finding.message}</p>
        ))}
      </section>

      <SafePreview />

      <section aria-labelledby="raw-heading" className="panel">
        <h2 id="raw-heading">Unchanged raw source</h2>
        <pre aria-label="Unchanged raw Markdown source"><code>{content.rawMarkdown}</code></pre>
      </section>
    </main>
  );
}

createRoot(window.document.getElementById("root")!).render(<App />);
