# Android build notes

## What was corrected

- The Android build uses Python 3.11.9 for both target Python and hostpython.
- A project-local python-for-android bcrypt recipe keeps the existing bcrypt
  3.1.7 version and adds `pycparser` to hostpython build prerequisites.
- SQLAlchemy uses `postgresql+pg8000`, matching the Android dependency.
- The latest Actions log confirms that bcrypt, cffi, and pycparser build and
  install successfully. They are not the cause of the final failure.
- The actual failure occurs in python-for-android's temporary `build/venv`:
  it runs `pip install -U pip`, resolves pip 26.3, and then pip fails importing
  `open_rich_spinner` from its own internal modules.
- `.github/pip-constraints.txt` pins pip to 24.3.1. The Build APK workflow
  exports `PIP_CONSTRAINT` only for the build command, so p4a's internal pip
  upgrade is constrained to that compatible version. Other project package
  versions are not constrained by this file.
- The workflow also removes stale p4a `build/venv` directories before a build
  attempt, while preserving the rest of the Android build cache.

## Build

Push the complete project to the `main` branch or run **Actions -> Build APK ->
Run workflow**. On success, download the `warehouse-apk` artifact from that run.

The APK has not been built or run on a physical Android device in this editing
session. A successful GitHub Actions run and a device smoke test are still
required to confirm packaging and runtime behavior.

## Database connection

The app connects to PostgreSQL through SQLAlchemy and pg8000. On Android,
`DB_HOST=localhost` points to the phone itself, not the development PC. Set
`DB_HOST` to the reachable LAN address or DNS name of the PostgreSQL server,
and ensure PostgreSQL accepts connections from the phone/network. Do not expose
port 5432 to the public internet without appropriate network protections.
