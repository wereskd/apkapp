# Android build notes

## What was corrected

- The Android build uses Python 3.11.9 for both target Python and hostpython.
- A project-local python-for-android bcrypt recipe keeps the existing bcrypt
  3.1.7 version and adds `pycparser` to hostpython build prerequisites.
- SQLAlchemy's PostgreSQL URL uses `postgresql+pg8000`, matching the Android
  dependency. This avoids requesting psycopg/psycopg2 while packaging pg8000.
- The latest build log confirms that bcrypt, cffi, and pycparser build
  successfully. The actual failure occurs later: python-for-android creates a
  temporary `build/venv`, upgrades pip, and then encounters inconsistent pip
  internals (`open_rich_spinner` import error).
- The workflow now removes only python-for-android's temporary `build/venv`
  directories after restoring the cache and before each build attempt. This
  prevents a partially upgraded pip environment from being reused, while
  preserving the rest of the Android build cache and compiled project files.
- The workflow still pins Buildozer and Cython, caches Android build downloads,
  and retries once for transient download failures.


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
