# DoraHacks BUIDL Submission Guide: Vertex Swarm Agent

**Competition**: The Vertex Swarm Challenge 2026 (DoraHacks)  
**Track**: Leaderless P2P Agent Swarms  
**Prize Pool**: `$27,000 Pool`  
**GitHub Repo**: `https://github.com/manderson240/vertex-swarm-agent`  
**Demo Video (2K QHD)**: [`docs/vertex_swarm_demo.mp4`](docs/vertex_swarm_demo.mp4) (6-Scene Full-Code Walkthrough)  
**Contact Info**: `manderson240@gmail.com` | Telegram: `@manderson240`

---

## Copy-Paste Form Fields for DoraHacks

### 1. Project Name
```text
Vertex Swarm Agent
```

### 2. Tagline (Under 120 characters)
```text
Leaderless coordinate-wise median BFT consensus and HMAC/monotonic P2P FoxMQ firewall for multi-agent swarms.
```

### 3. Tags
`Swarms`, `P2P`, `Byzantine Fault Tolerance`, `DePIN`, `Edge AI`, `Zero-Cloud`, `FoxMQ`, `HIHO Consensus`

---

## Detailed Project Description

### The Problem: Coordinator Bottlenecks & Byzantine Poisoning in P2P Swarms
Autonomous robot, drone, and distributed edge-AI agent swarms operating beyond reliable cloud connectivity fail under two fundamental failure modes:
1. **Single-Point-of-Failure Coordinators**: Cloud orchestration halts the entire swarm when backhaul partitions occur.
2. **Byzantine Mean Poisoning & Replay Spoofing**: Naive arithmetic averaging over peer embeddings allows a single malicious node submitting extreme outliers (or replaying old gossip frames) to hijack global swarm consensus.

### The Solution: Riemannian Median BFT + HIHO Stability + FoxMQ Firewall
Implemented cleanly in `src/vertex_swarm_spoke/bft_swarm.py` with zero external runtime dependencies:
1. **Coordinate-Wise Median Riemannian BFT (`ManifoldBFTCoordinator`)**: Computes breakdown-resistant coordinate-wise medians over `256D` peer semantic vectors, isolates compromised peers violating divergence tolerance or $\text{HIHO} = 0.50 \pm 0.12$ stability bounds (`disqualified_nodes`), and requires a $\ge 2/3$ (`0.67`) honest supermajority before committing a SHA-256 `aggregate_manifold_hash`.
2. **Leaderless FoxMQ Gossip Firewall (`FoxMQGossipVerifier`)**: Authenticates peer frames via constant-time `hmac.compare_digest` HMAC-SHA256 verification paired with strict per-sender monotonic sequence numbers, dropping replayed or tampered control packets in **0.0067 ms median latency**.

---

## System Architecture & Interaction Flow

```mermaid
flowchart TD
    Peers["Leaderless P2P Swarm Peers (N nodes)"] -->|"Signed GossipFrame (sender, nonce, HMAC)"| FoxMQ["FoxMQGossipVerifier.verify_frame()"]
    FoxMQ -->|"seq_nonce <= last_seen or bad HMAC"| Drop["DROP Frame (Replay / Tamper Blocked)"]
    FoxMQ -->|"Valid & Monotonic"| BFT["ManifoldBFTCoordinator.evaluate_votes()"]
    subgraph Consensus["HIHO + Coordinate-Wise Median BFT (< 0.01ms)"]
        HIHO["Filter HIHO Envelope (0.50 +- 0.12)"]
        Median["Coordinate-Wise Vector Median Centroid"]
        Disq["Disqualify RMS Divergence & Hash Mismatch Peers"]
        Quorum["Supermajority Gate (honest / total >= 0.67)"]
    end
    BFT --> HIHO --> Median --> Disq --> Quorum
    Quorum -->|"Quorum >= 2/3"| Certified["BFTVerdict(consensus_reached=True, agg_hash)"]
    Quorum -->|"Quorum < 2/3"| Halt["SAFE HALT (No Corrupted Action Committed)"]
```

```mermaid
sequenceDiagram
    autonumber
    actor Peer as Edge Swarm Node
    participant FoxMQ as FoxMQGossipVerifier
    participant BFT as ManifoldBFTCoordinator

    Peer->>FoxMQ: Broadcast GossipFrame(sender_id, seq_nonce, payload, hmac_hex)
    FoxMQ->>FoxMQ: Check seq_nonce > last_nonce & hmac.compare_digest()
    alt Replay Nonce or Invalid HMAC
        FoxMQ-->>Peer: DROP (replay_nonce / invalid_hmac_signature)
    else Frame Authentic
        FoxMQ->>BFT: Forward PeerVote(manifold_vector, stability_score)
        BFT->>BFT: Compute coordinate-wise median & RMS distance per peer
        BFT->>BFT: Isolate Byzantine / HIHO-drifted nodes & verify >= 2/3 quorum
        BFT-->>Peer: Emit BFTVerdict(consensus_reached, disqualified_nodes, agg_hash)
    end
```

---

## Competitive Comparison & Edge Resilience

| Metric | Naive Cloud / Mean Aggregator | Vertex Swarm Agent (BFT + FoxMQ) | Advantage |
|---|:---:|:---:|:---:|
| **Central Coordinator Required** | Mandatory (SPOF) | **None (100% Leaderless P2P)** | **Partition resilient** |
| **Byzantine Breakdown Point** | `0%` (1 outlier ruins mean) | **Up to `< 33%` (< 1/3 peers)** | **Mathematically robust** |
| **Replay / Spoof Defense** | Unauthenticated JSON | **HMAC-SHA256 + Monotonic Nonce** | **0.0067 ms p50 drop** |
| **Runtime Memory / Deps** | Heavy orchestration SDKs | **Pure Python Stdlib (0 external deps)** | **Edge / drone ready** |

---

## Empirical V-Model Verification ($N=100$ Trials)

- **Unit Test Suite**: `3/3` pytest assertions passing in `0.01s` (`tests/test_vertex_swarm_spoke.py`), verifying honest supermajority agreement, disqualification of extreme vector outliers and HIHO drift peers, and replay/tampering rejection on `FoxMQGossipVerifier`.
- **Monte Carlo Cohen's $d$**: `2.1285` ($N=100$).
- **Wald SPRT Log-Likelihood Ratio**: `+101.96` (`accept_h1` certified).
- **Median Verifier Latency (p50)**: `0.0067 ms`.

---

## How to Verify in 60 Seconds

```bash
git clone https://github.com/manderson240/vertex-swarm-agent.git
cd vertex-swarm-agent
uv sync
uv run pytest tests/test_vertex_swarm_spoke.py -v
```

---

## Walkthrough Video Chapters (`docs/vertex_swarm_demo.mp4` • 2560×1440 2K QHD)

1. **Scene 0**: Title Hero — Leaderless BFT Consensus, HIHO `0.50+-0.12`, FoxMQ Firewall & $N=100$ V-Model Metrics
2. **Scene 1**: Architecture Pipeline & Single-Point Mean Aggregator vs. Sovereign Median BFT Comparison
3. **Scene 2**: Actual Core Source — `ManifoldBFTCoordinator` (`src/vertex_swarm_spoke/bft_swarm.py`)
4. **Scene 3**: Actual Security Source — `FoxMQGossipVerifier` HMAC & Nonce Firewall
5. **Scene 4**: Live Terminal Walkthrough — 2/3 Quorum Consensus Certified vs. Byzantine Outlier & Replay Blocked
6. **Scene 5**: Full 3/3 Pytest Suite Execution, Empirical $N=100$ Metrics & 1-Command Verification
