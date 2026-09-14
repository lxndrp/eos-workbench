# React- und Flutter-Read-only-Spike

Dieser Spike implementiert denselben vollständig synthetischen EOS-Workflow
zweimal. Er ist eine Evidenzquelle für die noch offene Frameworkbewertung,
jedoch kein Architekturentscheid und keine Anwendungsvorlage.

## Gemeinsamer Vertrag

Die kanonische Fixture steht in
[`spikes/fixtures/read-only-workflow.json`](../../spikes/fixtures/read-only-workflow.json).
Beide Varianten zeigen:

- Repository, Basisrevision und Quellpfad als reine Herkunftsinformation;
- bekannte sowie unbekannte Metadaten ohne Interpretation des unbekannten Felds;
- Beziehungen, einen einseitigen Bezug und einen sichtbaren Konsistenzbefund;
- eine unveränderte Rohansicht neben einer sicheren Vorschau;
- einen synthetischen Berechtigungs-/Integrationsfehler ohne Retry oder Netzwerkpfad.

Die Fixture enthält absichtlich einen `script`-Tag und eine externe Bild-URL.
Sie erscheinen ausschließlich als Text in der Rohansicht. Die Vorschau baut
weder HTML noch ein Bild- oder Netzwerkelement, sondern zeigt beide Fälle
sichtbar als blockiert an.

## Lokaler Start

Die Anwendungen bleiben absichtlich voneinander und von der künftigen
Workbench getrennt.

```sh
cd spikes/react-readonly
npm ci
npm run dev
```

```sh
cd spikes/flutter-readonly
mise exec flutter@3.47.4 -- flutter pub get
mise exec flutter@3.47.4 -- flutter run -d chrome
```

Keiner der Befehle benötigt ein Content-Repository, Token oder eine
GitHub-Verbindung. Der Flutter-Aufruf setzt eine lokal verfügbare, temporär
über mise bereitgestellte SDK-Version voraus; er schreibt keine SDK-Vorgabe in
dieses Repository.

## Prüfgrenzen

Die jeweiligen Tests prüfen die sichere Vorschau modell- beziehungsweise
widgetnah. Der React-Build und der Flutter-Web-Build stellen den vollständigen
lokalen Produktionspfad der zwei Prototypen her. Ein Browserlauf ergänzt die
Sichtprüfung der semantischen Strukturen und des sichtbaren Fokus.

Die Tests belegen nicht die Sicherheit eines allgemeinen Markdown-Parsers.
Ein produktiver Editor benötigt dafür später einen eigenständigen,
risikogerechten Sicherheitsauftrag.

## Messergebnisse

Die folgenden Werte werden nach dem reproduzierbaren Build im zugehörigen PR
eingetragen. Sie vergleichen ausschließlich diese kleinen Prototypen; sie sind
keine Prognose für eine produktive Workbench.

| Nachweis | React Web | Flutter Web |
| --- | ---: | ---: |
| Produktionsartefakt | 204 KiB gesamt; JavaScript: 198.060 Byte (62,02 kB gzip) | 40.684 KiB gesamt einschließlich CanvasKit-/Wasm-Laufzeit |
| Verhaltenstest | 1 Test bestanden | 2 Tests bestanden |
| Produktionsbuild | `npm run build` bestanden | `flutter build web --release --no-source-maps` bestanden |
| Sichtprüfung semantischer Kernzustände | lokale Chrome-Headless-Sichtprüfung: sichtbar | Widgettest: Sperrhinweise, Semantiklabels und fehlendes `Image` nachgewiesen |

Die React-Sichtprüfung zeigt die Quellmarkierung, den synthetischen
Integrationsfehler, die Metadaten, den Beziehungsbefund sowie beide
Sperrhinweise. Ein lokaler Chrome-Headless-Versuch konnte den Flutter-
Canvas-/Wasm-Renderer auf diesem Host wegen CoreDisplay-/WebGL-Fehlern nicht
sichtbar abbilden. Das ist ein Umgebungsbefund; der Flutter-Web-Build und die
Widgettests waren erfolgreich. Eine spätere produktnahe UI-Prüfung muss mit
einem regulären Browser- und Screenreader-Setup erfolgen.

## Grenzen und nächste Einordnung

Es gibt keine Schreibfunktion, Persistenz, Authentifizierung, GitHub-API,
Token, echte Inhalte oder Veröffentlichung. Die Ergebnisse werden erst nach
dem Merge der getrennten Architektur-Diskussionsvorlage in deren ADR ergänzt.
Damit entsteht keine konkurrierende Änderung an einem noch offenen PR.
