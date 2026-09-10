# Entwicklung

Die verbindlichen Agentenregeln stehen in [AGENTS.md](../AGENTS.md).
Dieser Leitfaden beschreibt ihre Durchführung für Beiträge zur Anwendung.
Die Anwendungsarchitektur und der Anwendungsstack sind noch nicht entschieden.
Die hier verwendeten Werkzeuge dienen ausschließlich dem Entwicklungsprozess.

## Quellen und Zuständigkeiten

| Gegenstand | Führende Quelle |
| --- | --- |
| Entwicklungsauftrag und Entscheidungen | GitHub Issue in `lxndrp/eos-workbench` |
| Priorität, Complexity und Fortschritt | [eos-workbench Roadmap](https://github.com/users/lxndrp/projects/4) |
| Umsetzung und technische Prüfung | PR, aktuelle CI und Repository |
| Langfristige Architekturentscheidung | ADR im Repository |
| Redaktionelle Inhalte, Beziehungen und Metadaten | Konfiguriertes privates Content-Repository |
| Redaktionelle Freigabe und Veröffentlichung | Redaktioneller Prozess im Content-Repository |

Das Project verwendet `Todo`, `In Progress` und `Done`, Priority P0 bis P3
sowie `Deferred` und die vier Complexity-Kategorien.
Iterations-, Kapazitäts- und verpflichtende Metrikfelder sind zunächst nicht vorgesehen.
Das Project ist privat; die öffentlichen Issues bleiben als vollständige
Arbeitsaufträge auch ohne Project-Zugriff verständlich.

## Vom Auftrag zum Arbeitsbereich

Ein Issue beschreibt Nutzerwert oder technisches Ziel, Umfang und Nicht-Ziele,
prüfbare Akzeptanzkriterien sowie Entscheidungen und Abhängigkeiten.
Die Vorlagen für [Tasks](../.github/ISSUE_TEMPLATE/task.yml),
[Stories](../.github/ISSUE_TEMPLATE/story.yml) und
[Bugs](../.github/ISSUE_TEMPLATE/bug.yml) unterstützen diese Angaben.
`needs:refinement` und `needs:decision` kennzeichnen fehlende Reife.
Native Blockerbeziehungen bilden tatsächliche Voraussetzungen ab.
Stories und größere Zusammenhänge können über Parent-/Sub-Issues verbunden werden.
Eine kleine Aufgabe benötigt kein künstliches Epic.

Vor Beginn werden Issue, Kommentare, verknüpfte PRs, Project-Felder und
Arbeitsbereich gelesen, beispielsweise:

```sh
gh issue view ISSUE --repo lxndrp/eos-workbench --comments
gh issue view ISSUE --repo lxndrp/eos-workbench --json assignees,milestone,projectItems
gh pr list --repo lxndrp/eos-workbench --state open
git status --short --branch
git worktree list --porcelain
git fetch origin
```

`ISSUE` und weitere großgeschriebene Platzhalter werden durch die geprüften
Werte des Auftrags ersetzt.
Ein im privaten Project nicht lesbarer Wert wird nicht erfunden.
Die Risikobewertung kann nach den Regeln der AGENTS.md im Issue erfolgen.
Aus einem lesenden Auftrag wird dadurch kein Implementierungsauftrag.

Ein passender freier Worktree wird aus dem aktuellen `origin/main` angelegt:

```sh
git worktree add -b codex/ISSUE-kurzer-name ABSOLUTER_WORKTREE_PFAD origin/main
```

Vor einer Neuanlage auf bestehende Arbeit zum Issue prüfen.
Ein bereits vorhandener passender Arbeitsbereich wird nicht durch eine
konkurrierende Umsetzung ersetzt.
Die separate Implementierungsaufgabe bezieht ihren Auftrag unmittelbar aus GitHub.

## Einrichtung

[mise](https://mise.jdx.dev/) stellt die in `.mise.toml` gepinnten Werkzeuge bereit.
Python, uv und Lychee sind Prozesswerkzeuge; PyYAML wird durch `uv.lock` gebunden.
Persönliche Codex-Konfiguration, Zugangsdaten und Home-Skills gehören nicht hierher.

```sh
mise install
mise exec -- uv sync --locked
```

## Prüfungen

| Änderung | Prüfung |
| --- | --- |
| Eigene Dokumentation | Whitespace und lokale Links |
| Skill oder GitHub-Vorlage | Zusätzlich Strukturprüfung und betroffene Tests |
| Validator, Workflow oder Prozesswerkzeuge | Alle folgenden Prozessprüfungen |
| Spätere Anwendungsänderung | Im Architektur-/Implementierungsauftrag passende Fachtests ergänzen |

Die lokalen Befehle entsprechen den Schritten der CI:

```sh
git diff --check
git diff --cached --check
git diff --check origin/main...HEAD
mise exec -- uv run --locked python scripts/check_process.py
mise exec -- uv run --locked python -m unittest discover -s tests -v
mise exec -- lychee --offline --include-fragments README.md AGENTS.md 'docs/**/*.md' '.agents/skills/**/*.md' '.github/*.md'
```

Die Strukturprüfung erkennt beschädigte YAML-Daten, doppelte Schlüssel,
unvollständige Skill-Metadaten, unbrauchbare Issue-Formulare und nicht gepinnte
Action-Verweise.
Sie prüft außerdem den deaktivierten Ruleset-Vorschlag gegen die tatsächlich
vorhandenen Checknamen und den vereinbarten Geltungsbereich.
Lychee prüft nur lokale Ziele und Fragmente; externe URLs werden damit nicht verifiziert.
Ein dokumentierter Verhaltenstest prüft zusätzlich, ob ein Skill im konkreten
Auftrag passende Entscheidungen trifft.
Ein erfolgreicher Strukturtest ist dafür kein Ersatz.

Der Workflow `Process checks` läuft für PRs gegen `main` und Pushes nach `main`.
Er verwendet ausschließlich lesende Repositoryberechtigungen.
Ein erfolgreicher Check belegt die Prozessartefakte, nicht die Qualität einer
noch nicht implementierten Webanwendung.
Neue relevante Änderungen benötigen neue Nachweise.

## Pull Request und Review

Nach lokaler Prüfung nur auftragsbezogene Dateien stagen, auf Englisch committen
und den Feature-Branch pushen.
Die PR-Beschreibung enthält Problem, Änderung, Complexity, Verifikation,
wesentliche Einschränkungen und die passende Issue-Verknüpfung.
Bei vollständiger Umsetzung steht `Closes #<nummer>` in einer eigenen Zeile;
bei Teilumsetzung wird beispielsweise `Refs #<nummer>` verwendet.

```sh
gh pr create --repo lxndrp/eos-workbench --base main --head FEATURE_BRANCH --title 'PR_TITLE' --body-file PR_BODY_FILE
gh pr view PR --repo lxndrp/eos-workbench --json headRefOid,assignees,milestone,projectItems,closingIssuesReferences,statusCheckRollup
gh pr checks PR --repo lxndrp/eos-workbench
```

Beim Erstellen gesetzte Issue-Assignees, Milestone und Project-Zuordnung
über die jeweiligen `gh pr create`-Optionen ergänzen; leere Felder leer lassen.
Review-Threads, allgemeine Kommentare, Checks und zugehörige Sicherheitsbefunde
prüfen, bevor der PR als mergefähig gemeldet wird.
Akzeptanzkriterien werden am aktuellen Stand kontrolliert.
Bei C4 ist eine dokumentierte menschliche Bewertung erforderlich.
Ein automatisches Review ersetzt sie nicht.

## Merge und Closeout

Eine ausdrückliche Freigabe bezieht sich auf den konkreten PR-Stand.
Vor dem Merge prüfen, ob Commit, CI und Befunde noch dazu passen.
Nach Änderungen eine erneute Freigabe für den neuen Stand einholen.
Der Maintainer kann einen von ihm selbst erstellten PR nicht selbst über
GitHubs formale Approve-Funktion genehmigen; eine nachvollziehbare Entscheidung
im PR oder im ausdrücklich zugeordneten Auftrag dokumentiert die Freigabe.

Nach dem Merge den kanonischen Git-Stand, die CI auf `main`, Issue und Project
erneut prüfen.
Eine durch `Closes` automatisch geschlossene Aufgabe darf vorübergehend noch
`In Progress` bleiben, solange der technische Closeout nicht bestätigt ist.
`Done` bedeutet vollständig geliefert und geprüft.
Bei fehlgeschlagenen Folgeprüfungen den Befund dokumentieren und das Issue
gegebenenfalls wieder öffnen.

Saubere zugehörige Worktrees und lokale/Remote-Feature-Branches nach Prüfung
gezielt entfernen.
Reständerungen erhalten und mit konkreten Dateinamen zur Entscheidung vorlegen.
Codex-Aufgaben werden manuell archiviert.
Merge, Software-Release, Deployment und redaktionelle Veröffentlichung sind
unterschiedliche Vorgänge.

## Ruleset-Vorschlag

Die [Ruleset-Vorlage](../.github/rulesets/main.json) ist ein deaktivierter,
separat prüfbarer Vorschlag für `main`.
Sie verlangt PRs, den erfolgreichen Check `Process checks` von GitHub Actions
und aufgelöste Review-Threads; Force-Push und Branch-Löschung sind gesperrt.
Es gibt keine Bypass-Akteure und keine vorgeschriebene native Approve-Anzahl.
Die menschliche Freigabe nach AGENTS.md bleibt verbindlich.

Die GitHub-Actions-Integration und der Checkname wurden am ersten erfolgreichen
[PR-Lauf](https://github.com/lxndrp/eos-workbench/actions/runs/34477946173) verifiziert.
Der Commit dieser Vorlage aktiviert keinen Repositoryschutz.
Nach einer gesonderten Freigabe werden aktueller Repository-/CI-Stand und
vorhandene Rulesets erneut gelesen; ausschließlich dieser Vorschlag wird mit
`enforcement: active` angelegt oder ein eindeutig zugehöriges Ruleset aktualisiert.
Anschließend müssen aktive Regeln und Geltungsbereich erneut aus GitHub gelesen werden.
Die Parameter folgen dem
[GitHub-Ruleset-Vertrag](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset).

## Architekturentscheidungen und spätere Skillübernahme

ADRs dokumentieren Kontext, Alternativen, Entscheidung, Konsequenzen und Status.
Es gibt zunächst keinen Architekturentscheid und keine vorgeschriebene
Programmiersprache, kein Framework und keinen Deploymentanbieter.
Der Konzeptions-Pilot erhebt Anforderungen am aktuellen Content-Stand und
liefert technische Entscheidungsaufträge, ohne das Fachmodell zu duplizieren.

Gemeinsame Methoden sollen später als versionierte Skillquellen gepflegt werden.
Die vier lokalen EOS-Skills bleiben bis zum bestätigten Bereitstellungsnachweis aktiv.
Die Umstellung erfolgt in einem eigenen PR und wird in einem frischen
Codex-Kontext geprüft.
Installation, automatische Verteilung und chezmoi-Bootstrap sind kein Teil
dieser Prozessgrundlage.
