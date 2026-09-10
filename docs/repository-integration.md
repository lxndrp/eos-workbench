# Bestandsaufnahme und Anforderungen an die Repository-Integration

Konzeptions-Pilot zu [Issue #4](https://github.com/lxndrp/eos-workbench/issues/4).
Stand der Prüfung: 10. September 2026.
Dies ist eine Integrationsanalyse, kein neues Metadatenschema und kein Architekturentscheid.
Der Anwendungsstack, die Authentifizierung und das Deployment bleiben offen.

## Quellen und Geltung

Geprüft wurde der kanonische `main`-Stand von `lxndrp/eos-content`,
Commit `de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f`, in einem separaten Checkout.
Der bereits vorhandene lokale Content-Checkout hat eine abweichende Historie;
er wurde weder aktualisiert noch als kanonische Quelle verwendet.
GitHub Issues und das private Project wurden zusätzlich live gelesen.
Diese GitHub-Metadaten sind nicht durch den Content-Commit versioniert.

Die folgenden Links benötigen Berechtigung auf das private Repository.
Sie führen bewusst auf technische Quellen, nicht auf einzelne redaktionelle Texte:

| Quelle am geprüften Commit | Bedeutung für die Integration |
| --- | --- |
| [Metadatendokumentation](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/docs/METADATA-SCHEMA.md) | Kontrollierte Werte, Quellenrollen, Synchronisationsregel |
| [Publikationsmodell](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/docs/PUBLICATION-MODEL.md) | Identität, Beziehungen, Veröffentlichung und Freigabe |
| [Redaktionsworkflow](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/docs/WORKFLOW.md) und [Agentenregeln](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/AGENTS.md) | Redaktionelle Entscheidungs- und Sicherheitsgrenzen |
| [Vorlagen](https://github.com/lxndrp/eos-content/tree/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/templates) und [weitere Artikelvorlage](https://github.com/lxndrp/eos-content/tree/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/content/_templates) | Tatsächliche Varianten für Neuanlage |
| [Content-Verzeichnis](https://github.com/lxndrp/eos-content/tree/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/content) | Tatsächlich vorhandene Darstellungen und Referenzen |
| [Topic-Issue-Vorlage](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/.github/ISSUE_TEMPLATE/topic.md) und [Editorial System](https://github.com/users/lxndrp/projects/3) | Diskussion und operative redaktionelle Planung |
| [Bisherige Architektur](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/docs/ARCHITECTURE.md) und [älteres Workbench-Konzept](https://github.com/lxndrp/eos-content/blob/de4c7fa11c85f5cecec9b8d48814ce18f1bc0f3f/docs/WORKBENCH-CONCEPT.md) | Historische Annahmen, auf Widersprüche zum neuen Auftrag geprüft |

Der neuere Projektauftrag und die [aktuellen Workbench-Regeln](../AGENTS.md)
geben die bereits vollzogene Repository-Trennung vor.
Das ältere Konzept beschreibt noch eine spätere Trennung, ein festes Framework,
Deployment und ein von der Anwendung geführtes Modell.
Diese technischen Festlegungen werden nicht als neue Architektur übernommen.
Fachliche Regeln bleiben im Content-Repository maßgeblich;
Widersprüche innerhalb dieser Regeln benötigen eine ausdrückliche Klärung.

## Vorhandene Objekte und Darstellungen

| Gegenstand | Beobachteter Bestand | Konsequenz |
| --- | --- | --- |
| Observation | Markdown unter `content/observations/`, YAML-Frontmatter mit redaktionellen Feldern unter `params` | Nicht nur die flache Darstellung aus der Metadatendokumentation lesen |
| Topic | Markdown-Dossier unter `content/topics/`, ebenfalls `params`; teilweise explizite Issue-Referenz | Dateimetadaten, redaktionelles Issue und Planung getrennt zeigen |
| Publication | Artikel, LinkedIn-Beiträge und Talks in eigenen Verzeichnissen; vorhandene Dateien verwenden `params` | Gemeinsame Arbeitsschritte mit formatspezifischen Inhalten erhalten |
| Podcast | Als Typ und Vorlage definiert, keine konkrete Publikationsdatei am geprüften Stand | Unterstützten Typ nicht mit vorhandener Instanz verwechseln |
| Serie | Optionales Metadatenfeld, im Bestand genutzt; zusätzliche Reihenfolgeangabe bei einem Format | Vorhandene Werte anbieten, keine neue Serienentität oder Stammdatenbank einführen |
| Gemeinsame Notizen | Passiver Bestand unter `knowledge/` und bestehende Referenzen | Erhalten und verlinken, nicht als neuen Kernprozess ausbauen |

Alle untersuchten Objektdateien besitzen lesbares YAML-Frontmatter.
Bei den geprüften Objektkennungen wurden keine Duplikate oder Abweichungen
zwischen Kennung und Dateinamenspräfix gefunden.
Das ist kein Nachweis vollständiger fachlicher Konsistenz.
Freie Markdown-Abschnitte und formatspezifische Metadaten sind Teil des Originals,
nicht aus einem Formular vollständig rekonstruierbare Nebenprodukte.

### Beziehungen

Der vorhandene Prozess erlaubt mehrere Observations pro Topic und mehrere
Topics pro Observation sowie Publications aus einem oder mehreren Topics.
Zusätzlich existieren direkte Observation-/Publication-Verweise,
Beziehungen zwischen Publications und zwischen Topics.
Die Anzeige muss die Richtung und Herkunft jeder gespeicherten Beziehung erkennen lassen.

Im Bestand verwenden Observations `params.relatedTopics`, während die
Metadatendokumentation `topicRefs` nennt.
Topics verwenden `params.sourceObservations`, während deren Quellentabelle
`observationRefs` nennt.
Publication-Referenzen werden in zwei dokumentierten Namenskonventionen beschrieben.
Das sind zu klärende Adaptergrenzen, keine Freigabe für pauschale Umbenennungen.

Die untersuchten strukturierten Referenzen zwischen Kernobjekten ließen sich auflösen.
Bei Observation-zu-Topic-Verweisen fehlen jedoch vereinzelt explizite Gegenverweise.
Daraus folgt weder automatisch ein Datenfehler noch die Erlaubnis, beide Seiten zu ergänzen:
Zuerst muss geklärt werden, ob Gegenrichtungen gespeichert oder nur abgeleitet werden.
Freitextlinks, externe Quellen und passive Wissensreferenzen wurden nicht vollständig validiert.

## Bestätigte Abweichungen und offene Vertragsfragen

Die folgenden Befunde sind Quellvergleiche, keine automatisch auszuführenden Reparaturen.
Private Texte, Seriennamen und einzelne Objektkennungen bleiben im Content-Repository.

| Befund und Quellen | Erforderliche Klärung vor schreibender Unterstützung |
| --- | --- |
| Historische Architektur und Agentenregeln beschreiben noch das gemeinsame Repository | Technische Altvorgaben ausdrücklich vom heutigen Auftrag abgrenzen; Content-Dokumentation nur separat beauftragt ändern |
| Metadatendokumentation, Publikationsmodell, Vorlagen und Objektdateien unterscheiden sich in Verschachtelung und Feldnamen | Unterstützte Darstellungen und Umgang mit gleichzeitig vorhandenen, widersprüchlichen Aliasfeldern festlegen |
| Eine Publikation verwendet einen nicht in der kontrollierten Wertemenge enthaltenen Status; das Publikationsmodell erwähnt zusätzlich historische Statusvarianten | Unbekannten Originalwert anzeigen und erhalten; keine automatische Umdeutung in einen erlaubten Status |
| Eine Publikation hat keine strukturierten Ursprungsthemen, obwohl das Publikationsmodell mindestens eines verlangt | Unvollständigkeit anzeigen; Ausnahme oder redaktionelle Ergänzung entscheiden lassen |
| Eine Observation enthält Freigabemetadaten, obwohl die Metadatendokumentation solche Felder dort ausschließt | Widerspruch markieren und Felder verlustfrei erhalten; nicht als erteilte Publikationsfreigabe interpretieren |
| Vorlagen existieren an zwei Stellen; die Artikelvorlagen unterscheiden sich strukturell, mehrere Formatvorlagen enthalten noch passive Wissensreferenzen | Führende Vorlage je Typ bestimmen, ohne vorhandene Dokumente zu migrieren oder Vorlagen in der Workbench zu duplizieren |
| Quellenmatrix und Synchronisationsregel setzen unterschiedliche Akzente bei Project, PR und Frontmatter für Status/Freigabe | Quellenhoheit je Merkmal und Lebensphase klären; kein pauschales Last-write-wins |
| Editorial System bietet weiterhin „Veröffentlicht“ als Status und weniger Risikoabstufungen als die Metadatendokumentation | Project-Werte nicht blind in redaktionelle Statuswerte oder Risikowerte übersetzen |
| Beim Live-Abruf waren an den Project-Einträgen keine Single-Select-Werte gesetzt | Fehlende Planungsdaten als fehlend anzeigen; vorhandene Dateimetadaten weder löschen noch als aktuelle Project-Werte ausgeben |
| Nicht jedes Topic-Dossier besitzt eine explizite Issue-Nummer | Fehlende Zuordnung sichtbar lassen; nicht durch Titelähnlichkeit automatisch ein Issue erzeugen oder verknüpfen |

Der Content-Commit und die Live-GitHub-Metadaten sind getrennte Momentaufnahmen.
Vor jeder Implementierung werden die betroffenen Quellen erneut geprüft.
Eine später korrigierte Content-Datei macht diesen historischen Befund nicht zum aktuellen Fehler.

## Anforderungen an die Integration

### Lesen, Übersicht und Vertraulichkeit

- Das konfigurierte Content-Repository desselben Accounts muss auch privat nutzbar sein.
  Zielrepository, Branch und gelesener Stand sind erkennbar;
  keine Schreib- oder Publikationsbefugnis entsteht allein durch Leseberechtigung.
- Jede Ansicht unterscheidet gespeicherte Daten, abgeleitete Beziehungen,
  fehlende Angaben, Validierungsbefunde und veraltete oder nicht lesbare Quellen.
  API-Fehler dürfen nicht als leerer Bestand erscheinen.
- Typen, Vorlagen und Serien werden aus dem unterstützten Content-Vertrag und Bestand bezogen.
  Technische Adapter und ein rekonstruierbarer Index sind keine führende Datenquelle.
  Ein Cache darf keine ausschließlich dort gespeicherten fachlichen Änderungen enthalten.
- Interne Arbeitsstände, Risiko- und Freigabehinweise bleiben sichtbar.
  Ein niedriges Kommunikationsrisiko ist keine allgemeine Öffentlichkeitsfreigabe.
  Private Inhalte und Tokens gehören nicht in Builds, öffentliche Tests, Telemetrie oder Logs.
  Vorschauinhalte dürfen keine aktiven Inhalte ausführen oder private Daten über externe Abrufe preisgeben.

### Verlustfreies Bearbeiten und Vorschau

- Öffnen und unverändertes Speichern erzeugen keinen Datei-Diff.
  Unbekannte Felder, Kommentare, Reihenfolge, leere Werte, Datumsdarstellungen,
  Zeilenenden und freie Markdown-Abschnitte bleiben erhalten.
- Eine gezielte Bearbeitung verändert nur die ausdrücklich gewählten Bereiche.
  Die Workbench generiert nicht die ganze Datei aus ihrem Formularwissen neu.
  Nicht sicher unterstützbare oder mehrdeutige Dateien bleiben für strukturierte Änderungen gesperrt;
  Diagnose und Lesen bleiben nach Möglichkeit verfügbar.
- Vor Speichern sind exakter Datei-Diff, Metadatenänderungen, betroffene Beziehungen
  und Konsistenzbefunde gemeinsam prüfbar.
  Neue Objekte erhalten nachvollziehbar vergebene, nicht wiederverwendete Kennungen.
  Eine Beziehungsänderung zeigt alle beabsichtigten Dateianpassungen.
- Die Vorschau gehört zu einer bestimmten Basisrevision und Änderungsmenge.
  Jede nachträgliche lokale oder relevante externe Änderung erfordert erneute Prüfung.

### Konflikte und Speichern

- Fremde Änderungen, Löschungen, Umbenennungen und parallel vergebene Kennungen
  dürfen nicht still überschrieben werden.
  Der gewählte Transport muss die Schreibvorbedingung tatsächlich durchsetzen;
  bloßes Nachlesen unmittelbar vor dem Schreiben verhindert kein Rennen.
- Mehrdatei-Änderungen müssen als zusammengehöriger Stand prüfbar sein.
  Für Git-Dateien und getrennte Issue-/Project-Schreibvorgänge darf keine
  gemeinsame Atomarität unterstellt werden.
  Teilerfolge, Wiederaufnahme und unklarer Erfolg nach Verbindungsabbruch benötigen ein explizites Konzept.
- Speichern meldet erst nach Verifikation Erfolg.
  Wiederholungen dürfen keine zusätzlichen Objekte, Commits oder PRs erzeugen.
  Bei Konflikten bleiben die eigenen Änderungen und die Basis für einen Vergleich verfügbar.
- Fachliche Freigabe, technischer Merge und tatsächliche Veröffentlichung sind getrennt.
  Ein Freigabestatus allein bedeutet nicht veröffentlicht.
  Veröffentlichungsmetadaten dürfen nicht aus `draft`, Datum der Erstellung,
  Merge oder einer kanonischen URL allein erfunden werden.
  Das Speichern löst weder Export noch Deployment aus.

## Technische Entscheidungsaufträge

Die Reihenfolge und Akzeptanzkriterien werden in GitHub Issues geführt;
diese Referenzen sind kein zusätzliches Markdown-Backlog.

1. [Quellenhoheit und Kompatibilität](https://github.com/lxndrp/eos-workbench/issues/6):
   die oben genannten Widersprüche mit Quellenbezug und menschlichem Entscheidungsreview behandeln.
2. [Architektur und Zugriff](https://github.com/lxndrp/eos-workbench/issues/7):
   technische Alternativen einschließlich privatem Repository, GitHub-Planungsdaten und Sicherheitsgrenzen bewerten.
3. [Verlustfreies Bearbeiten und Vorschau](https://github.com/lxndrp/eos-workbench/issues/8):
   Adapterstrategie und synthetische Abnahmefälle konkretisieren.
4. [Konfliktsicheres Speichern](https://github.com/lxndrp/eos-workbench/issues/9):
   Schreibvorbedingungen, Teilerfolge und Freigabegrenzen entwerfen.

Der erste Folgeauftrag ist nach freigegebenem Abschluss dieses Piloten bearbeitbar.
Er fordert einen begründeten Entscheidungsvorschlag, nicht eine bereits heimlich
getroffene fachliche Vereinheitlichung.

## Prüfung und Pilotabschluss

Geprüft wurden die führende Dokumentation, beide Vorlagenbereiche,
alle Markdown-Kernobjekte einschließlich ihres Frontmatters, strukturierte
Kernreferenzen sowie Issues und Project-Felder/-belegungen.
Ein temporärer lesender Inventurlauf unterstützte die Bestandsprüfung;
er ist kein neuer Validator oder Bestandteil der Prozess-CI.
Es wurden keine Content-Dateien, Issues oder redaktionellen Project-Werte geändert.

Für diesen Dokumentations-PR sind lokal Whitespace und lokale Links zu prüfen.
Die unveränderte CI läuft zusätzlich gemäß bestehendem Workflow.
Ein Quellen-/Anforderungsreview prüft besonders Datenschutz, Quellenhoheit,
Freigabetrennung, Verlustfreiheit und Konflikte; er ersetzt keinen späteren Funktionstest.
Menschlicher C4-Review und ausdrücklicher Merge bleiben offen bis zur PR-Abnahme.
Commitgebundene Prüfergebnisse und Closeout werden im PR und Issue dokumentiert.

Prozessrückmeldung des Maintainers: Den dauerhaften Nutzen und Umfang der
Prozess-CI, insbesondere des Python-Bausteins, später bewerten.
Der Pilot verändert diese CI nicht.
Vor der Methodenverallgemeinerung ist dieser Punkt einzuordnen;
er ist derzeit kein bestätigter technischer Defekt und kein Anlass für eine neue Werkzeugschicht.
