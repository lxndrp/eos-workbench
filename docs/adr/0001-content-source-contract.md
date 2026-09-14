# ADR 0001: Verlustfreier Quellenvertrag für das Content-Repository

- Status: Vorgeschlagen – menschliches C4-Review erforderlich
- Datum: 2026-09-14
- Entscheidet: Lesende und schreibende Repository-Integration der EOS Workbench
- Geltungsbereich: Ein ausdrücklich konfiguriertes `eos-content`-Repository

## Kontext

`eos-content` ist die fachliche Single Source of Truth.
Die Workbench darf daher weder ein eigenes redaktionelles Modell noch einen
Hintergrundabgleich etablieren, der bestehende Darstellungen unbemerkt
vereinheitlicht oder überschreibt.
Freigabe und Veröffentlichung bleiben getrennte fachliche Vorgänge.

Die Untersuchung für [Issue #6](https://github.com/lxndrp/eos-workbench/issues/6)
hat den aktuellen `main`-Stand des konfigurierten Content-Repositorys,
dessen allgemeine Dokumentation, Vorlagenstruktur und das private Project
„Editorial System“ nur lesend ausgewertet.
Private Texte, Objektkennungen und personenbezogene Angaben sind nicht in
diese Entscheidung übernommen worden.

Die Befunde unterscheiden ausdrücklich beobachtete Repräsentationen von
dokumentierten Regeln:

| Befund | Einordnung |
| --- | --- |
| Observations und Topics liegen als Hugo-Dokumente mit allgemeinen Frontmatter-Feldern und verschachtelten `params` vor. | Beobachtet |
| Eine vorhandene Publikationsvorlage verwendet eine flache, ältere Feldform. | Beobachtet |
| `docs/METADATA-SCHEMA.md` beschreibt Hugo-Felder und kontrollierte Statuswerte. | Dokumentiert |
| `docs/PUBLICATION-MODEL.md` beschreibt abweichende flache Publikationsfelder und weitere Statuswerte. | Dokumentiert, aber nicht ohne Entscheidung als Schreibvertrag verwendbar |
| Das Editorial-Project besitzt eigene Workflow-, Format-, Risiko- und Planungsfelder. | Beobachtet |
| Ältere Architektur- und Workbench-Dokumente beschreiben eine historische, kombinierte Repository-Grenze. | Historischer Kontext, kein aktueller Quellenvertrag |

Damit ist eine verlustfreie Adaptergrenze erforderlich, bevor ein
Schreibbetrieb geplant werden kann.

## Entscheidungsvorschlag

Die Workbench behandelt jede vorhandene Content-Darstellung als erhaltenen
Quellbeleg und zeigt widersprüchliche Fakten nebeneinander an.
Sie leitet daraus keinen verdeckten Normalform-Datensatz ab und schreibt nie
in eine andere Darstellung zurück als die, die der Nutzer ausdrücklich
ausgewählt hat.

Für diese Entscheidung gelten die folgenden Regeln.

### Quellenhoheit

| Gegenstand | Führende Quelle | Verhalten der Workbench |
| --- | --- | --- |
| Persistierte redaktionelle Texte, bekannte und unbekannte Frontmatter-Felder, Dateipfade und Relationen | Aktueller Git-Stand von `eos-content` | Verlustfrei lesen; nur in die gewählte vorhandene Darstellung schreiben |
| Operativer Arbeitsfortschritt und Planungsfelder ohne gleichnamiges Content-Feld | Editorial-Project beziehungsweise dessen verknüpftes Artefakt | Als getrennten Kontext anzeigen, nicht beim Speichern eines Content-Dokuments ändern |
| Redaktionelle Freigabe | Expliziter, nachverfolgbarer Freigabebeleg im Content-Prozess | Als eigenes Faktum anzeigen; nicht aus Workflow-Status oder Publikationsdatum ableiten |
| Tatsächliche Veröffentlichung | Explizite Publikationsdaten und gegebenenfalls kanonische URL im Content-Dokument | Getrennt von Freigabe ausweisen; niemals durch Speichern oder Freigabe auslösen |
| Fachliche Identität | Vorhandene Identitätsangabe in der gewählten Content-Darstellung | Bei fehlender, mehrfacher oder kollidierender Angabe keine schreibende Aktion anbieten |

Ein Project-Status darf deshalb weder einen abweichenden Datei-Status löschen
noch eine Veröffentlichung behaupten.
Ein gespeichertes Content-Dokument aktualisiert umgekehrt keine Project-Felder.
Eine spätere, ausdrücklich beauftragte Project-Integration wäre ein eigener
Arbeitsvorgang mit eigenem Konfliktvertrag.

### Lesen, Anlegen und Ändern

| Vorgang | Erlaubtes Verhalten | Gesperrtes Verhalten |
| --- | --- | --- |
| Lesen | Rohdarstellung, bekannte Felder, unbekannte Felder und externe Kontextfakten quellmarkiert anzeigen | Verschiedene Status-, Datums- oder Relationsangaben zu einem stillschweigend bereinigten Wert verschmelzen |
| Anlegen | Eine ausdrücklich gewählte, im Content-Repository vorhandene und bestätigte Vorlage verwenden | Eine Mischvorlage aus abweichenden Feldformen erzeugen oder fehlende Regeln erraten |
| Ändern | Nur die explizit gewählte Repräsentation und die vom Vertrag abgedeckten Felder ändern; vor dem Commit einen Git-Diff vorlegen | Unbekannte Felder entfernen, inverse Relationen automatisch ergänzen oder Project-/Freigabefakten mitändern |

Eine schreibende Aktion setzt eine eindeutige Dokumentidentität, eine eindeutig
gewählte Repräsentation und einen aktuellen Git-Stand voraus.
Andernfalls bleibt sie gesperrt und benennt den konkreten Konflikt.

### Beziehungen und Vorlagen

Beziehungen bleiben zunächst dokumentlokale Angaben.
Eine einseitig vorhandene Beziehung ist sichtbar, aber keine Berechtigung, die
Gegenseite zu verändern.
Die Workbench kann sie als Konsistenzbefund markieren und einen menschlichen
Entscheidungs- oder Content-Änderungsauftrag verlinken.

Vorlagen sind Quellen, keine impliziten Migrationsregeln.
Solange die verschachtelte Hugo-Form und die flache ältere Form nicht im
Content-Repository ausdrücklich harmonisiert oder als parallele Verträge
bestätigt sind, muss der Anlegevorgang die Vorlage auswählen lassen oder
gesperrt bleiben.

## Konfliktverhalten

Die folgenden synthetischen Fälle definieren die Mindestanforderung an eine
spätere Integration.
Sie enthalten keine Daten aus dem Content-Repository.

| Synthetischer Konflikt | Anzeige | Schreibverhalten |
| --- | --- | --- |
| Feldalias-Kollision, etwa zwei unterschiedliche Namen für dieselbe vermutete Herkunftsrelation | Beide Rohwerte und ihre Quellen sichtbar; kein abgeleiteter Gesamtwert | Für die betroffene Relation sperren |
| Fehlender Project-Status bei vorhandenem Datei-Status | Fehlendes Project-Faktum separat ausweisen | Datei-Status erhalten; keine Ergänzung oder Löschung |
| Unbekannter Statuswert | Rohwert mit Hinweis auf den fehlenden Vertrag anzeigen | Statusänderung sperren; unbekannten Wert niemals entfernen |
| Einseitige Relation | Vorhandene und fehlende Gegenrichtung als Konsistenzbefund anzeigen | Keine automatische Gegenrelation schreiben |
| Freigabebeleg ohne Publikationsdatum | Freigegeben und nicht veröffentlicht getrennt anzeigen | Keine Veröffentlichung auslösen oder behaupten |
| Vorlagenkonflikt zwischen flacher und verschachtelter Feldform | Auswahl und Auswirkungen der Form sichtbar machen | Anlegen sperren, bis eine bestätigte Vorlage gewählt ist |

## Alternativen

1. **Darstellungen erhalten und Konflikte anzeigen** (empfohlen): Die
   Workbench bleibt ein verlustfreier Adapter und legt schreibende Aktionen
   bei Unklarheit still. Das schützt Git-Historie und bestehende Artefakte,
   verschiebt aber eine gewünschte Vereinheitlichung bewusst in das
   Content-Repository.
2. **Content-seitige Vereinheitlichung vor Schreibbetrieb:** Die Redaktion
   beschließt und migriert einen einheitlichen Vertrag in `eos-content`.
   Danach kann die Workbench einen kleineren, eindeutigeren Adapter erhalten.
   Das ist sinnvoll, falls die gegenwärtigen Darstellungen dauerhaft nicht
   parallel gepflegt werden sollen, ist aber eine fachliche Content-Änderung
   und nicht Gegenstand dieses Issues.
3. **Normalisiertes Workbench-Modell mit automatischer Rückübersetzung:**
   verworfen. Es würde unbekannte Felder, widersprüchliche Quellen und
   künftige Content-Erweiterungen gefährden und damit ein konkurrierendes
   Fachmodell etablieren.

Empfohlen wird Alternative 1 als sichere Übergangsgrenze.
Eine spätere Entscheidung für Alternative 2 kann diese ADR ablösen, nachdem
die Content-Migration eigenständig fachlich freigegeben und abgeschlossen ist.

## Konsequenzen und offene menschliche Entscheidungen

Die Workbench kann als Nächstes eine lesende Repository-Verbindung konzipieren,
aber noch keinen allgemeinen Schreibadapter zusagen.
Folgende Entscheidungen benötigen menschliche Freigabe im Content-Kontext:

1. Bestätigung, ob die beobachteten verschachtelten und flachen Formen
   parallele, weiterhin unterstützte Verträge oder ein Migrationsbefund sind.
2. Festlegung der fachlich zulässigen Statuswerte je Objektart und ihrer
   Zuordnung zu Project-Workflowwerten, ohne Freigabe und Veröffentlichung zu
   vermischen.
3. Festlegung, welcher nachverfolgbare Beleg eine redaktionelle Freigabe
   ausdrückt und ob die Workbench ihn künftig nur liest oder in einem
   gesonderten Vorgang pflegen darf.
4. Freigabe eines präzisen Vorlagenvertrags für Anlegen und einer
   feldweisen Schreibmatrix für Ändern.

Diese ADR erzeugt keine Content-Migration, keine Datenänderung, keinen
Anwendungsstack und keine GitHub-Project-Automation.

## Nachverfolgung

- [Issue #7](https://github.com/lxndrp/eos-workbench/issues/7) kann nach
  menschlicher Bestätigung den lesenden Integrationsvertrag und die
  Konfliktdarstellung konkretisieren.
- [Issue #8](https://github.com/lxndrp/eos-workbench/issues/8) bleibt bis
  zu einem bestätigten Vorlagen- und Schreibvertrag blockiert.
- [Issue #9](https://github.com/lxndrp/eos-workbench/issues/9) bewertet den
  Anwendungsstack erst gegen diesen Quellenvertrag und die daraus folgenden
  Sicherheitsgrenzen.
