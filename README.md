# 🕵️ Autonomous Fraud Investigation System

**Agentic RAG + Graph Intelligence + Event-Driven Automation**

An AI system that autonomously investigates financial transactions in real time. A
multi-step LangGraph agent plans its own investigation, calls tools (behavioural
baselines, anomaly checks, Neo4j graph queries, FAISS vector search over known
fraud cases), and produces an explainable decision — fraud score, evidence-based
reasons, confidence, and an action (allow / review / block). n8n drives the
event pipeline, a Next.js console shows the live feed, alerts, and the agent's
full reasoning trace.

This is not a chatbot — it is a decision-making system.

```bash
 simulator ──▶ n8n webhook ──▶ pre-filter rules ──┬─▶ low risk ──▶ POST /transactions
                                                  │
                                                  └─▶ suspicious ─▶ POST /investigate
                                                                        │
                                              ┌─────────────────────────┘
                                              ▼
                                   LangGraph agent (FastAPI)
                                   planner ⇄ tools loop:
                                     • get_user_history        (Postgres/CSV baseline)
                                     • check_transaction_pattern (anomaly detection)
                                     • get_linked_accounts     (Neo4j graph)
                                     • search_similar_cases    (FAISS RAG)
                                              │
                                              ▼
                            decision: fraud_score · reasons · confidence · action
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
               n8n Slack alert        stored in DB            Next.js dashboard
               (score ≥ 0.8)      (full reasoning log)     (feed · alerts · graph · logs)
```

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph (planner → tools → decide loop) |
| LLM | Anthropic Claude (`claude-opus-4-8`), with a deterministic rule-based fallback engine — the system runs fully without an API key |
| Retrieval (RAG) | FAISS vector index over a fraud-case knowledge base |
| Graph intelligence | Neo4j (`User`/`Device` nodes, `USED_DEVICE`/`TRANSFERRED_TO` edges), with an in-memory fallback |
| Backend | FastAPI + SQLAlchemy (SQLite by default, Postgres via Docker) |
| Automation | n8n (webhook → pre-filter → investigate → alert) |
| Frontend | Next.js 15 + Tailwind CSS 4 |

## Quick start (no Docker, no API key)

Everything degrades gracefully: SQLite instead of Postgres, in-memory graph
instead of Neo4j, rule-based agent instead of Claude.

```powershell
# 1. Data
python data\generate_data.py

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --port 8000

# 3. Dashboard (new terminal)
cd frontend
npm install
npm run dev            # http://localhost:3000

# 4. Simulate traffic (new terminal)
python simulation\simulator.py --target backend --interval 3
```

Watch the dashboard: transactions stream in, suspicious ones get investigated,
and clicking an alert shows the agent's step-by-step reasoning plus the identity
graph around the account.

## Full stack, one command (Docker: backend + frontend + Postgres + Neo4j + n8n)

```bash
cp .env.example .env       # optionally set ANTHROPIC_API_KEY / API_KEY / WEBHOOK_SECRET
docker compose up -d --build
```

This brings up everything: Postgres (with Alembic migrations run automatically
on backend startup), Neo4j, the FastAPI backend, the Next.js dashboard, and
n8n — dashboard at http://localhost:3000, API at http://localhost:8000/docs.

```bash
# seed the graph database once Neo4j is up
docker compose exec backend python -m app.graph.seed
```

### Database migrations (Postgres)

The backend uses SQLAlchemy models as the source of truth, versioned with
Alembic. SQLite (local dev) still auto-creates tables for zero-friction
startup; Postgres is managed exclusively through migrations, which the
backend container runs automatically on boot (`alembic upgrade head`).

```bash
cd backend
alembic upgrade head                       # apply migrations
alembic revision --autogenerate -m "..."   # after changing db/models.py
```

## Security

Auth is **opt-in** so local dev stays frictionless, but is a single env var
away from being locked down:

| Env var | Effect |
|---|---|
| `API_KEY` | When set, every route except `/health` requires header `X-API-Key: <value>`. Unset = auth disabled (dev mode). |
| `WEBHOOK_SECRET` | When set, `POST /transactions` and `POST /investigate` additionally require `X-Webhook-Signature`, an HMAC-SHA256 of the raw request body. n8n's workflow computes this automatically; it scopes those two ingestion routes to the automation pipeline even if `API_KEY` leaks. |

Also included:
- **Rate limiting** — 60 req/min per (IP, API key) via `RateLimitMiddleware` (in-process; swap for Redis-backed `slowapi` before scaling to multiple backend replicas).
- **CORS** locked to the dashboard origin.
- **Graceful tool failures** — every agent tool call and external dependency (Claude API, Neo4j, FAISS) is wrapped so a single failure degrades the system rather than crashing it (see "How the agent works").
- `.env` is git-ignored; `.env.example` documents every variable with a safe default.

## RAG ingestion pipeline

```bash
# Add new fraud cases (CSV or JSON) and rebuild the FAISS index in one step
python scripts/ingest_cases.py --file new_cases.csv

# Or just rebuild the index after manually editing data/fraud_cases.csv
python scripts/update_index.py
```

`ingest_cases.py` validates required fields (`case_id`, `fraud_type`,
`pattern`, `description`), de-duplicates by `case_id`, appends to
`data/fraud_cases.csv`, and rebuilds the index in-process. The running API
picks up a rebuilt index on next restart.

**n8n setup** (http://localhost:5678):
1. Create the local account, then *Workflows → Import from file* → `n8n/workflow.json`
2. Activate the workflow (toggle top-right)
3. Optional alerts: set `SLACK_WEBHOOK_URL` env var on the n8n container
4. Stream traffic through the full pipeline:
   `python simulation\simulator.py --target n8n --interval 3`

## Enable the Claude-powered agent

```powershell
copy .env.example .env
# set ANTHROPIC_API_KEY=sk-ant-...
```

With a key, Claude plans the investigation itself: it decides which tools to
call, follows up on findings (e.g. runs graph queries on a suspicious receiver),
and finalizes a structured decision. Without a key, a deterministic engine runs
the same tools with a weighted scoring model — same API, same explainability.
If a Claude call fails mid-investigation, the agent degrades to the rule engine
automatically.

## API

| Endpoint | Purpose |
|---|---|
| `POST /investigate` | Run the agent on a suspicious transaction |
| `POST /transactions` | Record a low-risk transaction (n8n clean branch) |
| `GET /transactions/feed` | Live feed for the dashboard |
| `GET /investigations` · `GET /investigations/{id}` | Results + full reasoning logs |
| `GET /graph/{user_id}` | Identity subgraph (users, devices, transfers) |
| `GET /stats` | Aggregate metrics |
| `GET /health` | Health + active graph backend |

Interactive docs: http://localhost:8000/docs

### Example decision output

```
Fraud Score: 0.99

Reasons:
1. Transaction is 8.54x the sender's average of $304.42
2. Transaction from AE — outside the sender's usual countries
3. Initiated at an unusual hour (2:00)
4. High-risk merchant category: crypto_exchange
5. Graph link to 5 flagged account(s): U020, U033, U051, U052
6. Matches known fraud pattern 'crypto_offramp' (case C014, similarity 0.41)

Confidence: High
Action: Block + Manual Review
```

## Project structure

```
backend/app/
  agents/        LangGraph investigator, Claude wrapper, rule-based scoring, explainer
  tools/         the 4 investigation tools + Anthropic tool specs
  rag/           embeddings + FAISS case store
  graph/         Neo4j client (with in-memory fallback) + seed script
  api/           REST routes (public health check + authenticated router)
  core/          API-key auth, webhook HMAC verification, rate limiting
  db/            SQLAlchemy models/session
backend/alembic/     Postgres schema migrations (SQLite skips these — auto-created)
scripts/         RAG ingestion (ingest_cases.py, update_index.py)
data/            dataset generator + generated CSVs (users, devices, transactions, fraud cases)
n8n/             importable workflow (webhook → HMAC sign → pre-filter → investigate → alert, with retries)
simulation/      real-time transaction simulator
frontend/        Next.js dashboard (feed, alerts, score chart, graph viz, reasoning logs)
docker-compose.yml   one-command stack: backend + frontend + Postgres + Neo4j + n8n
```

## How the agent works

The investigation is a LangGraph state machine:

1. **Planner** — Claude receives the transaction and the tool catalog, thinks,
   and picks the next tool call(s). (Rule engine: fixed 4-step plan.)
2. **Tools** — calls execute against real data sources; results are appended to
   the agent's context and to the reasoning log.
3. **Loop** — think → act → observe repeats until the agent is confident
   (or a step cap forces a decision).
4. **Decide** — the agent calls `finalize_decision` with a fraud score,
   confidence, evidence-based reasons, and an action mapped to thresholds
   (≥ 0.5 review, ≥ 0.8 block).

Every step is persisted, so any decision can be audited after the fact — the
dashboard renders the full trace: thoughts, tool inputs/outputs, and the final
structured decision.
