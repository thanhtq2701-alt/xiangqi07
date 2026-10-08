# Local prototype privacy

The local server stores games, reflections, practice attempts, skill schedules and feedback in `var/chill.sqlite3`. An HttpOnly, SameSite=Strict random cookie links your browser to its records. No email, name, password, date of birth or contact information is requested. No analytics tracker, remote font, paid LLM or external API is called by the application.

Data is not automatically shared, transmitted for model training or sent to a coach. The project owner must obtain appropriate consent and define a reviewed privacy policy before any external pilot, particularly involving children. This file is a description of the prototype, not a legal compliance certification.

Use the Data and privacy screen to export your session records as JSON or delete them. Exported data retains the reflection gate for exercises whose answers are not yet revealed. Deletion removes active records for that guest; it does not erase separately downloaded exports or external backups. Losing the guest cookie loses the UI association to old records. Anyone with operating-system access to the database may read it; this is not encrypted multi-user production storage.

Only the web assets are served as files. Source documents and database files are not available through the HTTP server. Host and Origin checks prevent ordinary cross-origin writes; production security needs further work.
