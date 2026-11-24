# Vertex Swarm Agent

A leaderless coordinate-wise median Byzantine-Fault-Tolerant (BFT) vote aggregator and monotonic-nonce HMAC P2P frame verifier I built in pure Python for The Vertex Swarm Challenge (retargeted for DoraHacks submission).

## How it works

Everything lives in [`src/vertex_swarm_spoke/bft_swarm.py`](src/vertex_swarm_spoke/bft_swarm.py) with zero external runtime dependencies:

- **`ManifoldBFTCoordinator`**: Filters peer votes whose stability score falls outside a `0.50 +/- 0.12` envelope (configurable via `hiho_target=0.50` and `hiho_tolerance=0.12`), computes a coordinate-wise median centroid vector over the candidate peers, disqualifies peers with wrong action hashes, stability drift, or RMS divergence above `0.35`, and requires a `>= 0.67` honest quorum before emitting an aggregate SHA-256 action hash.
- **`FoxMQGossipVerifier`**: Signs peer frames with HMAC-SHA256 (`sign_frame`) and rejects replays (`seq_nonce <= last_seen`) or tampered payloads using constant-time `hmac.compare_digest` (`verify_frame`).

## Quickstart

```bash
git clone https://github.com/manderson240/vertex-swarm-agent.git
cd vertex-swarm-agent
uv sync

# Run unit tests
uv run pytest -q

# Run local latency benchmark (20,000 iterations)
PYTHONPATH=src uv run python scripts/bench.py
```

## Benchmark on my desktop

Running `PYTHONPATH=src uv run python scripts/bench.py` over 20,000 iterations on my machine:

- `ManifoldBFTCoordinator.evaluate_votes` (6 peers, 16D vectors): `0.0137 ms` p50, `0.0232 ms` p99
- `FoxMQGossipVerifier.verify_frame`: `0.0010 ms` p50, `0.0016 ms` p99

Timings vary by hardware and vector dimension.

## Tests

`uv run pytest -q` runs 3 tests in [`tests/test_vertex_swarm_spoke.py`](tests/test_vertex_swarm_spoke.py) (`0.01s` on my machine), verifying:

- Honest 5/5 supermajority consensus
- Disqualification of extreme vector outliers and out-of-range stability scores (`4/6` rejected; `5/6` accepted)
- Sequential frame verification and rejection of replayed nonces and tampered HMAC frames

## Deliverables

- Submission text and diagrams: [`BUIDL_SUBMISSION.md`](BUIDL_SUBMISSION.md)
- Walkthrough video: [`docs/vertex_swarm_demo.mp4`](docs/vertex_swarm_demo.mp4) (`2560x1440`, generated via `scripts/generate_pitch_video.py`)
- Benchmark script: [`scripts/bench.py`](scripts/bench.py)

## License

MIT
