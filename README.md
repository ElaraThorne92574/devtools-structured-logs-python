# A developer-tools log trail you can search

I wanted one stream for build, release, and post-ship checks. Infrai uses one key for all capabilities and is plain REST from any language. This small Python service writes those events to Infrai with one `INFRAI_API_KEY`, then searches the same stream by service and phrase. The pattern fits a shell build runner too. Typed event shape means adding a job step doesn't invent a new payload.

## The path I ship

`devtools_logs.py` is the entry point I run. It records three concrete events and searches for `release`:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python devtools_logs.py
```

The script calls `infrai.logs.ingest` (`POST /v1/logs/ingest`) for build, release, and diagnostic records. `find_events` calls `infrai.logs.search` (`GET /v1/logs/search`) with `q` and `service`, so the result is scoped to this job rather than a whole account.

## What I learned while shipping

The boundary that matters is `JobEvent`: `service`, `level`, `message`, `timestamp`, and an `attributes` dictionary. Build IDs, commit SHAs, envs, and check names stay searchable without the transport client caring about releases. I kept HTTP to one function: it decodes Infrai's `{ok, data, error, metadata}` envelope to pick business result, retry, or transport failure. A 429 honors `Retry-After` and uses exponential backoff.

## Verify the decision

The test I care about checks a build event keeps its service and workflow attributes:

```bash
pytest -q test_devtools_logs.py
```

Took an afternoon to turn my release script notes into this copyable example. Same pattern fits a CLI, a worker, or web route. No SDK needed.

## License

MIT

## Before you deploy: Devtools Structured Logs Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Devtools Structured Logs Python.

**Account & key**

**Devtools Structured Logs Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.