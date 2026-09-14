import 'dart:convert';

import 'package:eos_flutter_readonly_spike/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final fixture = jsonDecode('''
{
  "repository": {"name": "eos-content (synthetic)", "revision": "4f7a9c2", "path": "topics/synthetic-workflow.md", "source": "Read-only fixture; no repository connection"},
  "document": {
    "kind": "Topic", "title": "Synthetic workflow observation", "status": "review",
    "knownMetadata": [],
    "unknownMetadata": {"key": "x-editorial-note", "value": "Retained without interpretation", "source": "unknown front-matter field"},
    "relations": [], "findings": [],
    "rawMarkdown": "<script>window.syntheticProbe = true</script>\\n![External probe](https://media.invalid/synthetic.png)",
    "preview": {"blocks": [
      {"type": "heading", "text": "Synthetic workflow observation"},
      {"type": "html", "source": "<script>window.syntheticProbe = true</script>", "blocked": "Raw HTML is shown only in the source view and is not rendered."},
      {"type": "image", "source": "https://media.invalid/synthetic.png", "blocked": "External media is not requested in the preview."}
    ]},
    "integration": {"state": "error", "message": "Synthetic permission failure", "detail": "No token, network client, or retry action."}
  }
}
''') as Map<String, dynamic>;

  test('preserves the two active-content boundaries in the preview model', () {
    final blocks = previewBlocks(fixture);

    expect(blocks.map((block) => block['type']), ['heading', 'html', 'image']);
    expect(blocks.where((block) => block['type'] == 'html'), hasLength(1));
    expect(blocks.where((block) => block['type'] == 'image'), hasLength(1));
  });

  testWidgets('shows source text but no active image widget', (tester) async {
    final semantics = tester.ensureSemantics();

    await tester.pumpWidget(MaterialApp(home: DocumentScreen(fixture: fixture)));

    await tester.scrollUntilVisible(find.byKey(const ValueKey('blocked-html')), 200);
    expect(find.text('Raw HTML blocked'), findsOneWidget);
    await tester.scrollUntilVisible(find.byKey(const ValueKey('blocked-image')), 200);
    expect(find.text('External media blocked'), findsOneWidget);
    await tester.scrollUntilVisible(find.byKey(const ValueKey('raw-source')), 200);
    expect(find.byType(Image), findsNothing);
    expect(find.bySemanticsLabel('Safe Markdown preview'), findsAtLeastNWidgets(1));
    expect(find.byKey(const ValueKey('raw-source')), findsOneWidget);
    semantics.dispose();
  });
}
