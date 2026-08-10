## Learned User Preferences

- Prefer minimal, carefully scoped diffs; keep only the most important changes.
- Prefer minor/careful dependency and Docker base-image bumps over large upgrades.
- Prefer separate commits for distinct change sets when asked to commit.
- Prefer simplifying verbose Docker/build config rather than expanding it.
- Respond in Russian with concrete, project-applicable solutions; outline a short plan before edits.

## Learned Workspace Facts

- Aiogram Telegram bot for SPbU timetable; Poetry + Python 3.12; Docker Compose with Postgres and Redis (`network_mode: host`, `TZ: Europe/Moscow`).
- Schedule images are rendered via Playwright Chromium screenshots of compiled HTML under `data/compiled_html_pages`.
- Schedule fonts live in `data/styles/fonts` (Montserrat, SourceSansPro) and are copied into compiled styles during the Docker multi-stage build.
- Production deploy path is `/var/www/Timetable_SPBU_bot/Timetable_SPBU_bot_2`; Compose service is `timetable-tgbot`.
- Production host is memory-constrained (~3 GiB RAM, no swap); Chromium/Playwright needs adequate `/dev/shm` (`shm_size` in Compose).
- Inline keyboards for study-program navigation can hit Telegram’s `reply markup is too long` limit.
