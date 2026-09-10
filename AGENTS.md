# EOS Workbench: Regeln für Agenten

## Auftrag und Quellen

- Dieses Repository enthält die Anwendung und ihren Entwicklungsprozess.
  Das konfigurierte private Content-Repository bleibt die dauerhafte Quelle
  für redaktionelle Inhalte und das EOS-Fachmodell.
  Keine konkurrierende fachliche Datenhaltung oder automatische Veröffentlichung.
- GitHub Issues enthalten Ziel, Scope, Akzeptanzkriterien und Entscheidungen.
  Das private [Project eos-workbench Roadmap](https://github.com/users/lxndrp/projects/4)
  enthält Planung; PR und CI belegen Umsetzung und Prüfung.
  Code und technische Dokumentation bleiben im Repository maßgeblich.
- Vor Arbeit und Statusauskunft Issue, Kommentare, Git-/PR-Stand, Project,
  Abhängigkeiten und konkurrierende Umsetzungen aktuell lesen.
  Dauerhafte Entscheidungen im zuständigen Artefakt dokumentieren.
- Planung, Review und Diagnose bleiben lesend, sofern der Auftrag keine
  entsprechenden Änderungen umfasst.
  Für 1Password-Developer-Environments stets den 1Password-MCP-Server verwenden.

## Umsetzung

- `Implementiere Issue #<nummer>.` umfasst bei Umsetzungsreife Implementierung,
  Commit, Push, PR und Prüfungen.
  Fehlendes Ziel, fehlende Akzeptanzkriterien, `needs:refinement`,
  `needs:decision`, ungelöste Blocker oder konkurrierende Arbeit vorab klären.
- Nicht triviale Implementierungen erhalten eine eigene Aufgabe, einen
  Worktree und `codex/<issue>-<kurzer-name>`.
  Standardbranch ist `main`; dort nicht direkt implementieren.
  Zusammengehörige Prozessdokumentation und ihre Prüfungen dürfen einen
  gemeinsamen PR erhalten, wenn die beteiligten Issues dies ausdrücklich festhalten.
- Nur auftragsbezogene Dateien ändern und stagen; bestehende Änderungen erhalten.
  Commits auf Englisch, eigene deutsche Dokumentation mit korrekten Umlauten
  und Semantic Line Breaks schreiben.
- Langfristige technische Entscheidungen mit relevanten Alternativen als ADR
  festhalten; lokale Implementierungsdetails benötigen kein ADR.
  Die leere Anwendung startet mit Anforderungs-/Architekturreview, ohne
  verpflichtenden vollständigen Codebasis-Review vor jedem SemVer-Milestone.
- Private Inhalte, Geheimnisse und persönliche Konfiguration nicht in dieses
  öffentliche Repository, seine Tests, Logs oder Artefakte übernehmen.
  Beispiele und Tests sind synthetisch.

## Risiko und Prüfung

Das Project-Feld `Complexity` und seine Optionsbeschreibungen bestimmen die
Einstufung; diese Tabelle legt die Prüfkonsequenzen fest.

| Stufe | Prüfkonsequenz |
| --- | --- |
| C1 | Mechanische Änderung: betroffene Syntax-, Format- oder Dokumentationsprüfung. |
| C2 | Lokales Verhalten: betroffene Tests und angrenzende Schnittstelle prüfen. |
| C3 | Komponentenübergreifend: betroffene Integrations-, Toolchain- und CI-Verträge prüfen. |
| C4 | Architektur, Sicherheit, Schreibzugriffe oder Migration: Zerlegung prüfen und menschlichen Review dokumentieren. |

- Keine feste Modellzuordnung; das konfigurierte Modell verwenden.
  Bei fehlender oder unplausibler Einstufung vor Implementierung das Risiko
  begründet im Issue bewerten.
  Ein neues höheres Risiko erfordert entsprechende Prüfungen; Project-Werte
  nicht stillschweigend ändern.
- Die ausführbaren Prüfungen stehen ausschließlich im
  [Entwicklungsleitfaden](docs/development.md#prüfungen).
  Fehlende Prüfwerkzeuge konkret melden; keine Kommandos erfinden.
  Produkt-, Test- und Umgebungsfehler unterscheiden und einen unveränderten
  Umgebungsfehler nicht wiederholt mit derselben breiten Prüfung untersuchen.
- Nach relevanten Änderungen betroffene Prüfungen und CI erneut ausführen.
  Nachweise müssen zum aktuellen PR-Stand passen.
  Menschlicher Review bei C4 bleibt zusätzlich erforderlich.

## PR, Freigabe und Abschluss

- PRs verknüpfen vollständige Umsetzungen mit `Closes #<nummer>`;
  Teilumsetzungen referenzieren das Issue ohne schließende Verknüpfung.
  Vorhandene Assignees, Milestone und Project-Zuordnung übernehmen und danach prüfen.
- Alle relevanten Review-Threads, allgemeinen Kommentare, CI- und
  Sicherheitsbefunde prüfen.
  Threads erst nach inhaltlicher Klärung auflösen; Folgearbeit als Issue erfassen.
- Merge, Software-Release, Deployment und externe Aktivierung erfordern
  jeweils eine ausdrückliche Freigabe für den konkreten Stand.
  Ein Implementierungsauftrag oder grüner Check ersetzt diese Freigabe nicht.
- Nach freigegebenem Merge CI, Issue und Project erneut prüfen.
  Erst dann vollständig gelieferte Issues schließen und auf `Done` setzen.
  Vor dem Entfernen des eigenen Worktrees dessen Reständerungen prüfen;
  bei Reständerungen erhalten und eine Entscheidung einholen.
  Nur zugehörige saubere Arbeitsbereiche und Feature-Branches bereinigen.
  Aufgaben werden manuell archiviert.
- Goal-Metriken sind optional.
  Nur tatsächlich ausgewiesene Agentenlaufzeit und Tokenzahl dokumentieren;
  fehlende Werte bleiben leer und sind kein Abschlussblocker.
  Agentenlaufzeit ist kein vollständiger menschlicher Entwicklungsaufwand.

## Lokale Methoden

- `.agents/skills/eos-issue-delivery`: Issue-Umsetzung und PR-Abschluss.
- `.agents/skills/eos-quality-triage`: Auswahl angemessener Prüfungen.
- `.agents/skills/eos-review-triage`: Einordnung von Befunden.
- `.agents/skills/eos-roadmap-review`: lesende Planungsbewertung.

Die lokalen Skills werden erst nach bestätigter Bereitstellung gemeinsamer
Skills in einem gesonderten PR ersetzt.
