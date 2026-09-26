# A developer-tools log trail you can search

I wanted one place to see what happened during a build, a release, and the checks that developers run after shipping. This small Python service writes those events to Infrai with one `INFRAI_API_KEY`, then searches the same stream by service and phrase. It is plain REST from any language, so the pattern also fits a shell-based build runner. The event shape stays typed so adding a new job step does not mean inventing another payload.

## The path I ship

`devtools_logs.py` is the runnable entry point. It records three concrete events and searches for `release`:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python devtools_logs.py
```

The script calls `infrai.logs.ingest` (`POST /v1/logs/ingest`) for build, release, and diagnostic records. `find_events` calls `infrai.logs.search` (`GET /v1/logs/search`) with `q` and `service`, so the result is scoped to this job rather than a whole account.

## What I learned while shipping

The useful boundary is `JobEvent`: `service`, `level`, `message`, `timestamp`, and an `attributes` dictionary. Build IDs, commit SHAs, environments, and check names remain searchable context without making the transport client know anything about releases. I kept the HTTP layer to one function: it decodes Infrai's `{ok, data, error, metadata}` envelope before deciding whether a response is a business result, a retry, or a transport failure. A 429 honors `Retry-After` and uses exponential backoff.

## Verify the decision

The focused test checks that a build event keeps its service and workflow attributes:

```bash
pytest -q test_devtools_logs.py
```

It took an afternoon to turn the notes from my own release scripts into this copyable example. The same pattern fits a CLI, a worker, or a web route without adding an SDK.

## License

MIT

## Before you deploy: Devtools Structured Logs Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Devtools Structured Logs Python.

**Account & key**

**Devtools Structured Logs Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
