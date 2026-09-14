# ADR 0002: Architekturvorschlag für die GitHub-Integration der EOS Workbench

- Status: Diskussionsvorlage – noch kein Architekturentscheid
- Datum: 2026-09-14
- Bewertet: Anwendungsarchitektur, GitHub-Authentifizierung, UI-Optionen und
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
- [Flutter für mehrere Plattformen](https://docs.flutter.dev/platform-integration),
  [Flutter Web](https://docs.flutter.dev/deployment/web) und
  [Flutter Web Accessibility](https://docs.flutter.dev/ui/accessibility/web-accessibility)

GitHubs REST-API erlaubt GitHub-App-User-Tokens für das Schreiben von
Repository-Inhalten, verlangt dafür aber mindestens `Contents: write`.
Project-V2-Zugriffe sind grundsätzlich über GraphQL möglich; die für die
konkreten Abfragen notwendige GitHub-App-Berechtigung muss laut GitHub gegen
den tatsächlichen Zugriff geprüft werden.
Diese Diskussionsvorlage verspricht daher keine ungeprüfte Project-Automation.

## Architekturvorschlag

Als zentrale Architekturgrenze wird eine same-origin Webanwendung mit einem
serverseitigen Backend-for-Frontend (BFF) vorgeschlagen.

Für das BFF steht ein schlanker Node.js-Dienst mit TypeScript und Fastify als
Ausgangskandidat zur Auswahl.
Für das Frontend wird **noch kein Framework entschieden**:
React mit TypeScript und Flutter Web mit Dart bilden die enge Auswahl.
Beide Varianten verwenden dieselbe BFF-Grenze und dieselben GitHub-Rechte.
Das BFF und die jeweiligen Frontend-Artefakte werden später gemeinsam hinter
einem TLS-Terminierungspunkt betrieben.
Eine Datenbank, ein Suchindex mit eigener Wahrheit, Hintergrundsynchronisation
und Telemetrie mit Inhaltsdaten gehören nicht zum Ansatz.

```text
Browser: React oder Flutter Web
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

Flutter bleibt zusätzlich als mögliche spätere lokale macOS-Anwendung in der
Betrachtung.
Das ist kein Auftrag für eine Desktop-Anwendung, erweitert aber die spätere
Option, private Inhalte und Credentials auf dem Nutzergerät zu halten.
Flutter unterstützt Web und macOS aus einer Codebasis; dieser Vorteil muss
gegen Web-Barrierefreiheit, Markdown-Integration und Bundle-Verhalten geprüft
werden.

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

## Enge Auswahl für das Frontend

Die BFF-Grenze löst die Token- und Repository-Frage unabhängig vom
UI-Framework.
Für den ersten vertikalen Schnitt bleiben daher zwei gleichberechtigte
Frontend-Kandidaten offen:

| Kandidat | Stärken für die Workbench | Zu prüfende Risiken |
| --- | --- | --- |
| React mit TypeScript | Browsernahe HTML-, Formular- und Markdown-Integration; gemeinsamer Typraum mit einem TypeScript-BFF | Kein direkter Weg zu einer lokalen Desktop-Anwendung; Abhängigkeiten und clientseitige Renderinggrenzen gezielt klein halten |
| Flutter Web mit Dart | Einheitliche UI-Basis für Web und eine spätere macOS-Anwendung; Flutter unterstützt beide Zielplattformen | Flutter Web benötigt bewusste Semantik-Aktivierung und -Tests für Screenreader; Markdown-/HTML-Einbettungen, Startgröße und Web-Interoperabilität müssen am echten vertikalen Schnitt geprüft werden |

### Gegenüberstellung

Die folgende Bewertung trennt belastbare Eigenschaften von noch zu messenden
Punkten.
Sie ist kein gewichteter Endentscheid: Der relative Wert einer späteren
lokalen macOS-Anwendung gegenüber einer möglichst browsernahen ersten
Workbench muss vor der Frameworkwahl bewusst gewichtet werden.

| Kriterium | React mit TypeScript | Flutter Web mit Dart | Bedeutung für EOS |
| --- | --- | --- | --- |
| GitHub-Token und private Repository-Inhalte | Gleich: Bei ausschließlichem BFF-Zugriff erreichen weder Token noch GitHub-Client den Browser. | Gleich: Flutter Web benötigt dieselbe BFF-Grenze. | Kein Auswahlkriterium; browserdirekte Varianten bleiben für beide ausgeschlossen. |
| GitHub-API, Project- und Konfliktvertrag | Direkte TypeScript-Modelle können mit dem TypeScript-BFF geteilt werden. | Der Vertrag wird über JSON-Schema oder generierten Dart-Code separat abgebildet. | React reduziert im BFF-Vorschlag die Gefahr auseinanderlaufender technischer Typen; die fachliche Quelle bleibt in beiden Fällen `eos-content`. |
| Verlustfreie Datei- und Diff-Ansicht | Browser- und DOM-nahe Komponenten eignen sich für Textdiff, Rohansicht und große Markdown-Dokumente. | Möglich, aber für Texteditor-, Diff- und Web-Interoperabilität sind gezielte Komponenten- und Performanceprüfungen nötig. | Der Adapter bleibt server- und frameworkunabhängig; die UI darf keine ganze Datei neu generieren. |
| Sichere Markdown-Vorschau | React kann browsernative HTML-Elemente direkt verwenden; eine Sanitizer-/AST-Pipeline bleibt zwingend, insbesondere ohne unsicheres Roh-HTML-Rendering. | Flutter kann Markdown als Widgetbaum darstellen; HTML- oder Webview-Einbettungen erhöhen den Prüfbedarf und dürfen die Sperren für aktive Inhalte nicht umgehen. | React hat hier weniger Integrationsrisiko, nicht weniger Sicherheitsverantwortung. |
| Barrierefreiheit im Web | Browsernative Elemente bieten unmittelbar die übliche DOM- und ARIA-Grundlage; Komponenten und Fokusführung müssen dennoch getestet werden. | Flutter bildet Semantik in ein zugängliches DOM ab, muss sie für Web aber bewusst aktivieren und mit Screenreadern prüfen. | React hat einen pragmatischen Vorteil für den webbasierten Erstbetrieb; Flutter ist bei nachgewiesener Semantik nicht ausgeschlossen. |
| Bedienung als anspruchsvolle Arbeitsoberfläche | Starke Browser- und Formularintegration; Komponentenauswahl und State-Management müssen schlank bleiben. | Einheitliches Widget- und Zustandsmodell für komplexe, interaktive Oberflächen. | Beide sind geeignet; der synthetische Schnitt muss Tastatur, Fokus, Fehlermeldungen und Mehrspaltenansichten zeigen. |
| Spätere lokale macOS-Anwendung | Erfordert eine zusätzliche Plattformstrategie und wahrscheinlich einen getrennten Client. | Kann UI und Teile der Anwendungslogik für macOS wiederverwenden. | Flutter hat einen klaren strategischen Vorteil, falls lokales Arbeiten mit Content-Checkout und OS-Credential-Speicher ein bestätigtes Ziel wird. |
| Web-Build und Betrieb | Klassische statische Webartefakte neben dem BFF; konkrete Bundlegröße und Abhängigkeiten messen. | `flutter build web` erzeugt Webartefakte; Quellkarten dürfen nicht öffentlich ausgeliefert werden und Startverhalten muss gemessen werden. | Kein pauschaler Performance-Sieger; reale Release-Builds mit derselben Aufgabe vergleichen. |
| Teamwissen und Wartung | Abhängig von vorhandenem TypeScript-/React-Wissen. | Abhängig von vorhandenem Dart-/Flutter-Wissen und der Bereitschaft, Web-Spezifika bewusst zu testen. | Noch unbekannt; vor der Auswahl ausdrücklich erheben, nicht vermuten. |

**Zwischenfazit:** Für eine rein webbasierte erste Workbench bietet React
geringere Risiken bei browsernativer Semantik, Markdown- und Diff-Integration
sowie einem TypeScript-BFF-Vertrag.
Flutter ist die gleichwertige strategische Alternative, wenn eine spätere
lokale macOS-Anwendung einen hohen Stellenwert besitzt und der zusätzliche
Nachweis für Web-Semantik, Vorschau und Release-Verhalten erbracht wird.
Keine dieser Aussagen ersetzt den synthetischen Vergleichsspike.

Flutter Web ersetzt das BFF nicht: Eine browserdirekt laufende Flutter-App
hätte dieselben Token-, Vorschau- und externen Ressourcenrisiken wie jede
andere browserdirekte Lösung.
Für beide Kandidaten sind deshalb dieselben Akzeptanztests verbindlich:

1. Tastaturbedienung, sichtbarer Fokus, Screenreader-Semantik und Zoom auf
   der Repositoryübersicht, einer Metadatenansicht und der Vorschau.
2. Keine Token oder privaten Inhalte im Browser-Speicher, Bundle, Netzwerklog
   oder Fehlerbericht.
3. Roh-HTML, aktive Inhalte und externe Medien bleiben in der Vorschau
   blockiert; nicht unterstützte Elemente sind erkennbar.
4. Ein Release-Build und dessen Quellkarten werden nicht öffentlich mit
   privaten Pfaden oder Diagnoseinformationen ausgeliefert.

Flutter dokumentiert für Web eine in das DOM übersetzte Semantikschicht, die
aus Performancegründen explizit aktiviert werden muss.
Das ist kein Ausschlusskriterium, sondern ein verpflichtender Nachweis im
Flutter-Spike.

## Vergleich der Alternativen

| Ansatz | Vorteile | Risiken und Aufwand | Bewertung |
| --- | --- | --- | --- |
| Lokale Verarbeitung mit lokalem Checkout oder nativer Begleitkomponente, etwa Flutter für macOS | Private Inhalte und Tokens verlassen das Nutzergerät nicht; Git-Operationen können lokal erfolgen | Installation, OS-Credential-Integration und plattformabhängige Brücke; keine einfache browserbasierte Nutzung oder zentrale Sicherheitsgrenze | Als späterer Offline-/Power-User-Modus offen, nicht erster Webansatz |
| Browser-direkte GitHub-Integration, unabhängig von React oder Flutter Web | Kein eigener Server und schneller Prototyp | User-Tokens und private Inhalte liegen im Browser-Kontext; XSS, Browser-Erweiterungen und CORS-/API-Beschränkungen werden Teil der Sicherheitsgrenze; GitHub-App-Private-Key darf nicht an Clients | Für schreibende Workbench verworfen; höchstens isolierter read-only Prototyp |
| Servergestütztes BFF mit GitHub-App-User-Token | Token bleibt serverseitig, Rechte sind durch App und Nutzer begrenzt, same-origin Grenze für Vorschau und Logging | Betrieb eines kleinen Servers, Secret Store, Login-Callback und Sicherheitsupdates nötig | Architekturvorschlag; Frontend bleibt zwischen React und Flutter Web offen |

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
7. React und Flutter Web mit derselben synthetischen Aufgabe anhand der
   Kriterien aus „Enge Auswahl für das Frontend“ bewerten; erst dann das
   Frontend auswählen.

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
5. Für Flutter Web die aktivierte Semantik, Tastaturbedienung, Screenreader-
   Verhalten und den Verzicht auf unsichere HTML-/Webview-Einbettungen gegen
   die synthetische Vorschau prüfen.

Ein fehlgeschlagener Spike ist ein Architektur- oder Berechtigungsbefund.
Er darf nicht durch eine breitere Token-Berechtigung oder Browser-Speicherung
umgangen werden.

## Konsequenzen und Folgearbeit

Diese Diskussionsvorlage erlaubt die Vorbereitung eines kleinen Webprojekts
mit einem BFF-Kandidaten und der engen Frontend-Auswahl React oder Flutter
Web, aber noch keine App-Registrierung, Secret-Anlage, Cloud-Aktivierung oder
produktive Bereitstellung.

- Issue #8 konkretisiert den verlustfreien Adapter, Bearbeiten und Vorschau
  innerhalb der hier beschlossenen read-only Sicherheitsgrenze.
- Issue #9 entwirft erst danach einen expliziten, konfliktsicheren
  Schreibvorgang und bewertet die notwendige Berechtigungserweiterung.
- Die im ersten vertikalen Schnitt genannten Spikes sind Eintrittskriterien
  für die Implementierung, keine stillschweigende Abkürzung dieser ADR.

Menschliches C4-Review entscheidet, ob die BFF-Grenze, die GitHub-App-
Registrierung, die gewählte Secret-Verwaltung und die spätere Erhöhung von
`Contents: read` auf `Contents: write` verfolgt werden.
Die Auswahl zwischen React und Flutter Web erfolgt erst nach den beschriebenen
Spikes und einem nachvollziehbaren Vergleich.
Bis dahin bleibt dieses Dokument eine Diskussionsvorlage.
