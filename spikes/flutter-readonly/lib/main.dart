import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  if (kIsWeb) {
    SemanticsBinding.instance.ensureSemantics();
  }
  runApp(const SpikeApp());
}

Future<Map<String, dynamic>> loadFixture() async {
  final source = await rootBundle.loadString('../fixtures/read-only-workflow.json');
  return jsonDecode(source) as Map<String, dynamic>;
}

List<Map<String, dynamic>> previewBlocks(Map<String, dynamic> fixture) {
  final document = fixture['document'] as Map<String, dynamic>;
  final preview = document['preview'] as Map<String, dynamic>;
  return (preview['blocks'] as List<dynamic>).cast<Map<String, dynamic>>();
}

class SpikeApp extends StatelessWidget {
  const SpikeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'EOS read-only Flutter spike',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff075a9c)),
        scaffoldBackgroundColor: const Color(0xfff4f6f8),
        useMaterial3: true,
      ),
      home: FutureBuilder<Map<String, dynamic>>(
        future: loadFixture(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return Scaffold(
              body: Center(
                child: Semantics(
                  label: 'Loading synthetic read-only fixture',
                  liveRegion: true,
                  child: CircularProgressIndicator(),
                ),
              ),
            );
          }
          return DocumentScreen(fixture: snapshot.data!);
        },
      ),
    );
  }
}

class DocumentScreen extends StatelessWidget {
  const DocumentScreen({required this.fixture, super.key});

  final Map<String, dynamic> fixture;

  @override
  Widget build(BuildContext context) {
    final repository = fixture['repository'] as Map<String, dynamic>;
    final document = fixture['document'] as Map<String, dynamic>;
    final knownMetadata = (document['knownMetadata'] as List<dynamic>)
        .cast<Map<String, dynamic>>();
    final relations = (document['relations'] as List<dynamic>)
        .cast<Map<String, dynamic>>();
    final findings = (document['findings'] as List<dynamic>)
        .cast<Map<String, dynamic>>();
    final integration = document['integration'] as Map<String, dynamic>;

    return Scaffold(
      appBar: AppBar(title: const Text('EOS Workbench · synthetic spike')),
      body: FocusTraversalGroup(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Semantics(
              header: true,
              child: Text(document['title'] as String,
                  style: Theme.of(context).textTheme.headlineMedium),
            ),
            const SizedBox(height: 8),
            Wrap(spacing: 8, children: [
              Chip(label: Text(document['kind'] as String)),
              Chip(label: Text(document['status'] as String)),
            ]),
            const SizedBox(height: 16),
            Semantics(
              liveRegion: true,
              label: 'Synthetic integration error: ${integration['message']}',
              child: Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: ListTile(
                  leading: const Icon(Icons.error_outline),
                  title: Text(integration['message'] as String),
                  subtitle: Text(integration['detail'] as String),
                ),
              ),
            ),
            _Section(
              title: 'Read-only source',
              child: _Facts(items: [
                ['Repository', repository['name'] as String],
                ['Revision', repository['revision'] as String],
                ['Path', repository['path'] as String],
                ['Origin', repository['source'] as String],
              ]),
            ),
            _Section(
              title: 'Metadata',
              child: _Facts(items: [
                ...knownMetadata.map((item) => [
                      item['label'] as String,
                      '${item['value']} (${item['source']})',
                    ]),
                [
                  'Unknown field: ${(document['unknownMetadata'] as Map<String, dynamic>)['key']}',
                  '${(document['unknownMetadata'] as Map<String, dynamic>)['value']} '
                      '(${(document['unknownMetadata'] as Map<String, dynamic>)['source']})',
                ],
              ]),
            ),
            _Section(
              title: 'Relationships',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ...relations.map((relation) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const Icon(Icons.account_tree_outlined),
                        title: Text('${relation['kind']}: ${relation['title']}'),
                        trailing: Chip(label: Text(relation['state'] as String)),
                      )),
                  ...findings.map((finding) => Semantics(
                        label: '${finding['severity']}: ${finding['message']}',
                        child: ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: const Icon(Icons.warning_amber_outlined),
                          title: Text(finding['message'] as String),
                        ),
                      )),
                ],
              ),
            ),
            _Section(
              title: 'Safe Markdown preview',
              semanticLabel: 'Safe Markdown preview',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: previewBlocks(fixture).map((block) {
                  if (block['type'] == 'heading') {
                    return Semantics(
                      header: true,
                      child: Text(block['text'] as String,
                          style: Theme.of(context).textTheme.titleLarge),
                    );
                  }
                  if (block['type'] == 'paragraph') {
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(block['text'] as String),
                    );
                  }
                  final isHtml = block['type'] == 'html';
                  return Semantics(
                    label: '${isHtml ? 'Raw HTML' : 'External media'} blocked: '
                        '${block['blocked']}',
                    child: Card(
                      key: ValueKey('blocked-${block['type']}'),
                      color: const Color(0xfffff7e6),
                      child: ListTile(
                        leading: const Icon(Icons.block),
                        title: Text(isHtml ? 'Raw HTML blocked' : 'External media blocked'),
                        subtitle: Text(block['blocked'] as String),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
            _Section(
              title: 'Unchanged raw source',
              child: Semantics(
                label: 'Unchanged raw Markdown source',
                child: Container(
                  key: const ValueKey('raw-source'),
                  color: const Color(0xff17212b),
                  padding: const EdgeInsets.all(12),
                  child: SelectableText(
                    document['rawMarkdown'] as String,
                    style: const TextStyle(
                      color: Color(0xfff4f6f8),
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.child, this.semanticLabel});

  final String title;
  final Widget child;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: semanticLabel,
      container: true,
      child: Card(
        margin: const EdgeInsets.only(top: 16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Semantics(
                header: true,
                child: Text(title, style: Theme.of(context).textTheme.titleLarge),
              ),
              const SizedBox(height: 8),
              child,
            ],
          ),
        ),
      ),
    );
  }
}

class _Facts extends StatelessWidget {
  const _Facts({required this.items});

  final List<List<String>> items;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: items
          .map((item) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: RichText(
                  text: TextSpan(
                    style: DefaultTextStyle.of(context).style,
                    children: [
                      TextSpan(
                        text: '${item.first}: ',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      TextSpan(text: item.last),
                    ],
                  ),
                ),
              ))
          .toList(),
    );
  }
}
