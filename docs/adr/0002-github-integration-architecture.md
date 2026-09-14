# ADR 0002: Servergestützte GitHub-Integration für die EOS Workbench

- Status: Vorgeschlagen – menschliches C4-Review erforderlich
- Datum: 2026-09-14
- Entscheidet: Anwendungsarchitektur, GitHub-Authentifizierung und
  Sicherheitsgrenzen der ersten EOS-Workbench
- Geltungsbereich: Eine kleine Webanwendung für ein ausdrücklich konfiguriertes
  privates `eos-content`-Repository desselben GitHub-Accounts

## Kontext

Die Workbench muss private Inhalte lesen und später kontrolliert bearbeiten
können, ohne eine fachliche Nebenhaltung aufzubauen.
[ADR 0001](0001-content-source-contract.md) verlangt dafür eine verlustfreie
Adaptergrenze, explizite Konflikte und gesperrte Schreibvorgänge bei
Mehrdeutigkeit.
Der Konzeptions-Pilot verlangt außerdem, dass Tokens und private Inhalte weder
in Builds, Logs oder Telemetrie geraten noch über die Vorschau externe Abrufe
auslösen.

GitHub Apps bieten im Gegensatz zu OAuth Apps repositorygenaue Berechtigungen
und kurzlebigere Zugangstoken.
Bei Aktionen im Namen eines Nutzers empfiehlt GitHub ein User Access Token,
weil es zusätzlich durch dessen eigene Rechte begrenzt ist.
Die aktuelle Machbarkeit wurde anhand der folgenden offiziellen Quellen geprüft:

- [GitHub Apps und OAuth Apps vergleichen](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps)
- [Best Practices für GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app)
- [User Access Tokens für GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app)
- [Repository-Inhalte über die REST-API](https://docs.github.com/en/rest/repos/contents)
- [Projects über die API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
- [GraphQL-Authentifizierung](https://docs.github.com/en/graphql/guides/forming-calls-with-graphql)
- [OWASP: XSS-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
  und [Content Security Policy](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

GitHubs REST-API erlaubt GitHub-App-User-Tokens für das Schreiben von
Repository-Inhalten, verlangt dafür aber mindestens `Contents: write`.
Project-V2-Zugriffe sind grundsätzlich über GraphQL möglich; die für die
konkreten Abfragen notwendige GitHub-App-Berechtigung muss laut GitHub gegen
den tatsächlichen Zugriff geprüft werden.
Diese Entscheidung verspricht daher keine ungeprüfte Project-Automation.

## Entscheidungsvorschlag

Die erste Workbench wird als same-origin Webanwendung mit einem
serverseitigen Backend-for-Frontend (BFF) umgesetzt.

Der vorgeschlagene Stack ist TypeScript in beiden Teilen, ein React-Frontend
und ein schlankes Node.js-BFF mit Fastify.
Das BFF und die statischen Frontend-Artefakte werden später gemeinsam hinter
einem TLS-Terminierungspunkt betrieben.
Eine Datenbank, ein Suchindex mit eigener Wahrheit, Hintergrundsynchronisation
und Telemetrie mit Inhaltsdaten gehören nicht zum Ansatz.

```text
Browser
  |  HTTPS, gleiche Origin, HttpOnly-Sitzung
  v
EOS-BFF
  |  GitHub-App-User-Token nur serverseitig
  v
GitHub REST und GraphQL
  |  private Dateien, Issues, Pull Requests und Project-Kontext
  v
eos-content und Editorial System
```

Das BFF ist ein technischer Vermittler.
Es hält keine redaktionellen Objekte, Beziehungen, Status oder Inhalte als
dauerhafte Quelle vor.
Es gibt ausschließlich eine quellmarkierte Adapteransicht für die konkrete
Git-Revision zurück.
Flüchtige Sitzungs- und Token-Caches sind nach Ablauf, Logout oder Neustart
löschbar und enthalten keine ausschließlich dort bearbeiteten Fachänderungen.

## Authentifizierung, Repository-Auswahl und Rechte

Die Workbench verwendet eine GitHub App mit Web-Flow für User Access Tokens.
Der Nutzer installiert die App für sein GitHub-Konto und wählt dort die
erlaubten Repositories.
Nach dem Login wählt die Workbench nur aus den für diese App-Installation und
diesen Nutzer erreichbaren Repositories ein `eos-content`-Repository aus.
Die Auswahl ist eine technische Konfiguration, keine fachliche Kopie.

Für den ersten vertikalen Schnitt gelten diese Grenzen:

| Fähigkeit | Vorgeschlagene minimale Berechtigung | Verhalten |
| --- | --- | --- |
| Repository und Dateien lesen | Metadata implicit; Contents read | Quelldateien und Git-Revision lesen |
| Zugeordnete Issues und Pull Requests lesen | Issues read; Pull requests read | Redaktionellen Kontext als getrennten Beleg anzeigen |
| Project-Kontext lesen | Im Spike konkret ermittelte, kleinste Project-Berechtigung | Fehlende oder nicht lesbare Daten als Fehlerzustand zeigen |
| Dateien, Issues, Projects oder PRs schreiben | Keine | Nicht Teil des ersten vertikalen Schnitts |

Das BFF hält den User Access Token ausschließlich in einer flüchtigen,
serverseitigen Sitzung.
Der Browser erhält nur ein sicheres, HttpOnly-, Secure- und SameSite-Cookie
mit einer opaken Sitzungskennung.
Bei Serverneustart oder Tokenablauf meldet sich der Nutzer erneut an.
Refresh-Tokens, Personal Access Tokens und GitHub-App-Installationstokens
werden im ersten Schnitt nicht dauerhaft gespeichert.

Die GitHub-App-Private-Key-Datei, das Client Secret und spätere
Deployment-Secrets liegen ausschließlich in einem geeigneten Secret Store.
Sie werden weder ausgeliefert noch in Repository, Browser-Bundle, Logs,
Fehlermeldungen oder lokale Beispielkonfiguration geschrieben.
GitHub rät ausdrücklich davon ab, private Schlüssel in Client-Anwendungen
auszuliefern oder Zugangsdaten fest im Code abzulegen.

Ein späterer Schreibbetrieb ist eine neue Berechtigungs- und Reviewentscheidung:
Er erfordert mindestens `Contents: write`, eine erneute Prüfung des
Autorisierungsflusses und den konfliktsicheren Schreibvertrag aus Issue #9.
Der erste read-only Schnitt beantragt diese Schreibberechtigung nicht.

## Datenfluss und Sicherheitsgrenzen

| Schutzgut oder Grenze | Risiko | Verbindliche Maßnahme |
| --- | --- | --- |
| GitHub-Token | XSS, Browser-Speicher, Log-Leak oder Weitergabe an fremde Skripte | Tokens nie an den Browser; serverseitige flüchtige Sitzung, Secret Store, Redaction und keine Drittanbieter-Skripte |
| Private Inhalte | Browser-Cache, Telemetrie, Diagnoseprotokolle oder unberechtigte Antwort | `Cache-Control: no-store` für Inhaltsantworten; keine Inhalts-Logs; Zugriff pro Sitzung und GitHub-Antwort erneut prüfen |
| Markdown-Vorschau | Aktives HTML, Skripte, URL-basierte Datenabflüsse oder irreführende Darstellung | Markdown als untrusted input behandeln; Roh-HTML standardmäßig deaktivieren, HTML sanitizen, strikte CSP einsetzen und externe Medien/Einbettungen standardmäßig blockieren |
| Callback und Sitzung | Login-CSRF, Session-Fixation oder fremde Rücksprungziele | State-Prüfung, feste Callback-URL, Sitzungsrotation nach Login und Origin-/CSRF-Prüfung für zustandsändernde BFF-Endpunkte |
| GitHub-Fehler und Konflikte | Fehler wird als leerer Bestand missverstanden oder Schreibversuch wiederholt | Fehlerklasse, Git-Revision und fehlende Berechtigung sichtbar ausweisen; keine automatische Wiederholung zustandsändernder Aufrufe |
| Externe Ressourcen | Private Vorschau löst Abrufe zu Dritten aus | Keine externen Fonts, Analytik oder Preview-Proxy; Links nur als Interaktion des Nutzers öffnen |

Die Vorschau bekommt nur die aktuelle, ungespeicherte Adapteransicht.
Sie führt keine Markdown-Skripte aus und übernimmt keine
Veröffentlichungs- oder Freigabebehauptung.
Die serverseitige Antwort enthält eine Basisrevision, damit spätere
Änderungs- und Konfliktprüfungen darauf aufbauen können.

## Vergleich der Alternativen

| Ansatz | Vorteile | Risiken und Aufwand | Entscheidung |
| --- | --- | --- | --- |
| Lokale Verarbeitung mit lokalem Checkout oder nativer Begleitkomponente | Private Inhalte und Tokens verlassen das Nutzergerät nicht; Git-Operationen können lokal erfolgen | Installation, OS-Credential-Integration und plattformabhängige Brücke; keine einfache browserbasierte Nutzung oder zentrale Sicherheitsgrenze | Als späterer Offline-/Power-User-Modus offen, nicht erster Webansatz |
| Browser-direkte GitHub-Integration | Kein eigener Server und schneller Prototyp | User-Tokens und private Inhalte liegen im Browser-Kontext; XSS, Browser-Erweiterungen und CORS-/API-Beschränkungen werden Teil der Sicherheitsgrenze; GitHub-App-Private-Key darf nicht an Clients | Für schreibende Workbench verworfen; höchstens isolierter read-only Prototyp |
| Servergestütztes BFF mit GitHub-App-User-Token | Token bleibt serverseitig, Rechte sind durch App und Nutzer begrenzt, same-origin Grenze für Vorschau und Logging | Betrieb eines kleinen Servers, Secret Store, Login-Callback und Sicherheitsupdates nötig | Empfohlen |

Ein reiner OAuth-App-Ansatz wird nicht empfohlen.
Er benötigt für private Repositories breite `repo`-Scopes, während die
GitHub App gezieltere Repository-Berechtigungen und eine begrenzte
Repository-Auswahl erlaubt.

## Erster vertikaler Schnitt

Der erste Schnitt ist bewusst read-only und beweist die Architektur, nicht den
gesamten Redaktionsprozess:

1. GitHub-App-Login starten und die serverseitige, flüchtige Sitzung anlegen.
2. Ein berechtigtes privates `eos-content`-Repository sowie dessen
   Default-Branch auswählen und die Auswahl sichtbar bestätigen.
3. Einen Verzeichnis- und Dokumentabruf mit Git-Revision ausführen.
4. Eine synthetisch getestete, quellmarkierte Roh- und Adapteransicht eines
   Dokuments zeigen, ohne unbekannte Daten zu normalisieren oder zu speichern.
5. Die Markdown-Vorschau ohne Roh-HTML und ohne externe Inhaltsabrufe zeigen.
6. Project- und Issue-Kontext nur lesen; ein fehlender Zugriff erscheint als
   nachvollziehbarer Berechtigungs- oder Integrationsbefund.

Alle Tests, Demos und Logs verwenden synthetische Inhalte.
Der Schnitt erzeugt keine Commits, Pull Requests, Project-Änderungen oder
Veröffentlichungen.

## Nachgewiesene Annahmen und notwendige Spikes

Folgende Annahmen sind durch die verlinkte GitHub-Dokumentation belegt:

- GitHub-App-User-Tokens können die REST- und GraphQL-APIs verwenden.
- Eine GitHub-App-Installation begrenzt die auswählbaren Repositories.
- Repository-Schreiben ist mit `Contents: write` möglich, aber für den
  ersten Schnitt nicht erforderlich.
- Project-V2-Abfragen sind über die GitHub-API möglich.

Vor einer Implementierung sind diese kleinen, nicht produktiven Spikes
erforderlich:

1. Mit einer Test-GitHub-App die kleinste Berechtigung für die konkreten
   lesenden Project-V2-GraphQL-Abfragen des privaten User-Projects ermitteln.
2. Den Login- und Repository-Auswahlfluss gegen ein synthetisches privates
   Test-Repository prüfen; dabei Account- und Repositorygrenzen nachweisen.
3. Einen End-to-End-Test gegen eine synthetische Markdown-Datei durchführen:
   Token bleibt serverseitig, CSP ist aktiv, Roh-HTML und externe Abrufe sind
   in der Vorschau blockiert.
4. Den vollständigen Berechtigungs- und Secret-Lebenszyklus vor der ersten
   produktiven App-Registrierung als Betriebsanleitung reviewen.

Ein fehlgeschlagener Spike ist ein Architektur- oder Berechtigungsbefund.
Er darf nicht durch eine breitere Token-Berechtigung oder Browser-Speicherung
umgangen werden.

## Konsequenzen und Folgearbeit

Die Entscheidung erlaubt die Vorbereitung eines kleinen TypeScript-Webprojekts
mit React-Frontend und Fastify-BFF, aber noch keine App-Registrierung,
Secret-Anlage, Cloud-Aktivierung oder produktive Bereitstellung.

- Issue #8 konkretisiert den verlustfreien Adapter, Bearbeiten und Vorschau
  innerhalb der hier beschlossenen read-only Sicherheitsgrenze.
- Issue #9 entwirft erst danach einen expliziten, konfliktsicheren
  Schreibvorgang und bewertet die notwendige Berechtigungserweiterung.
- Die im ersten vertikalen Schnitt genannten Spikes sind Eintrittskriterien
  für die Implementierung, keine stillschweigende Abkürzung dieser ADR.

Menschliches C4-Review entscheidet insbesondere über den Betrieb eines BFF,
die GitHub-App-Registrierung, die gewählte Secret-Verwaltung und eine spätere
Erhöhung von `Contents: read` auf `Contents: write`.
Bis dahin bleibt diese ADR vorgeschlagen.
