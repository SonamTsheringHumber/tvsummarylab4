# tvsummary

Downloads TV show records from the TVmaze API (https://api.tvmaze.com/shows?page=0,
about 240 shows) and writes a JSON summary: shows per genre, ratings per language,
shows per decade, top-rated shows, data-quality counts, and a short list of
featured shows chosen at random from a seed.

## Setup

```
conda env create -f environment.yml
conda activate tvsummary
pip install -r requirements.txt
pip install -e .
```

## Run

```
python -m tvsummary.main
python -m tvsummary.main --config config/tvsummary.toml
```

Results go to `data/processed/summary.json` and `data/processed/run_info.json`.

## Check it

```
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest
```

## Settings

All settings live in `config/tvsummary.toml` and are read into a frozen `Settings` object.

- `source_url`: the TVmaze page that is downloaded.
- `timeout`: seconds to wait for the download before giving up.
- `output_dir`: folder that receives `summary.json` and `run_info.json`.
- `seed`: seed for `random.Random`, which picks `featured_shows`.
- `sample_size`: how many show names go into `featured_shows`.
- `log_level`: DEBUG, INFO, WARNING, ERROR or CRITICAL.
- `min_records`: fewer usable shows than this counts as a failed run.
- `top_n`: how many shows appear in `top_rated_shows`.

## Errors and exit codes

All errors inherit from `TVSummaryError`. Only `main()` catches them. In every
case the user sees one line starting `Error:` on standard error, and no traceback.
`<url>`, `<path>` and similar placeholders are filled in at run time.

| Error class | When it is raised | What the user sees |
|---|---|---|
| `DownloadError` | The request times out | `Error: The request to <url> timed out after <timeout> seconds.` |
| `DownloadError` | The server cannot be reached | `Error: Could not connect to <url>. Check your internet connection.` |
| `DownloadError` | The server answers with an HTTP error status | `Error: The server returned an error: <details>` |
| `DownloadError` | Any other request failure | `Error: The request to <url> failed: <details>` |
| `DownloadError` | Fewer than `min_records` usable shows arrive | `Error: Only <n> usable records downloaded; at least <min_records> are required.` |
| `DataShapeError` | The response is not valid JSON | `Error: The response from <url> was not valid JSON.` |
| `DataShapeError` | The response is JSON but not a list | `Error: Unexpected response format: expected a list of shows.` |
| `SettingsError` | The settings file does not exist | `Error: Settings file not found: <path>` |
| `SettingsError` | The file is not valid TOML | `Error: Settings file is not valid TOML: <path>: <details>` |
| `SettingsError` | The file exists but cannot be read | `Error: Settings file could not be read: <path>: <details>` |
| `SettingsError` | A setting is missing | `Error: Settings file <path> is missing the setting '<name>'.` |
| `SettingsError` | A setting has a value that cannot be converted | `Error: Settings file <path> has a bad value: <details>` |
| `SettingsError` | A value is out of range (for example an unknown `log_level`) | `Error: Settings file <path> is invalid: <reasons>.` |
| `OutputError` | `summary.json` or `run_info.json` cannot be written | `Error: Could not write <path>: <reason>` |

Exit code `0` means the run succeeded and both files were written. Exit code `1`
means an expected failure: the error is logged at ERROR level (a `Run failed: ...`
log line), one line starting `Error:` is printed to standard error, and no
traceback is shown.

## Reproducing a run

The seed is in `config/tvsummary.toml`. `run_info.json` records every setting used,
the Python version, and the versions of tvsummary, pytest, mypy and ruff. To get
exactly the same `featured_shows` list, a classmate needs the same seed, the same
`sample_size`, and the same downloaded data, because names are sorted and then
sampled with `random.Random(seed)`. Install the pinned `requirements.txt` and use
Python 3.11. TVmaze can change its data, so a later run may differ even with the
same seed. `generated_at_utc` changes on every run by design.

## What the tests cover

- `Show` cleaning: a missing genre list, a missing or invalid rating, bad years and blank languages.
- Each of the five aggregations, using hand-made records.
- The download failure paths (no connection, timeout, HTTP error, bad JSON, wrong shape), with `requests.get` replaced so no network is used.
- Settings loading: a valid file, a missing file, invalid TOML, each missing setting, and an unknown `log_level`.
- The summary keys, the same-seed-same-list guarantee, writing files, and `run_info.json`.
- `main()`: exit codes 0 and 1, the printed `Error:` line, and the logged messages.

Not tested: a real download from TVmaze. A test that needs the internet fails when
the wifi does, so the live call is checked by running the program by hand.

## Known limitations

- Only the first page (page 0) of the TVmaze shows list is downloaded.
- The whole page is held in memory, which would not scale to very large datasets.
- `generated_at_utc` makes two summary files differ even when everything else matches.
- Logging goes to standard error only; there is no log file.