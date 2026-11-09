# Android build notes

## What was corrected

- The Android build uses Python 3.11.9 for both target Python and hostpython.
  The previous run selected Python 3.14.2 automatically while compiling the
  legacy bcrypt 3.1.7 recipe.
- A project-local python-for-android bcrypt recipe keeps bcrypt 3.1.7 and adds
  `pycparser` to hostpython build prerequisites. The failed run showed CFFI
  trying to import `pycparser` during bcrypt's host-side CFFI build.
- SQLAlchemy's PostgreSQL URL now uses `postgresql+pg8000`, matching the
  Android dependency. This avoids requesting psycopg/psycopg2 while packaging
  pg8000.
- The python-for-android release and Buildozer version are pinned. The workflow
  caches Buildozer downloads and retries the build once to tolerate transient
  HTTP 504 download failures.

## Build

Push the project to the `main` branch or run **Actions -> Build APK -> Run
workflow**. On success, download the `warehouse-apk` artifact from that run.

The APK has not been built or run on a physical Android device in this editing
session. A successful GitHub Actions run and a device smoke test are still
required to confirm packaging and runtime behavior.

## Database connection

The app connects to PostgreSQL through SQLAlchemy and pg8000. On Android,
`DB_HOST=localhost` points to the phone itself, not the development PC. Set
`DB_HOST` to the reachable LAN address or DNS name of the PostgreSQL server,
and ensure PostgreSQL accepts connections from the phone/network. Do not expose
port 5432 to the public internet without appropriate network protections.
