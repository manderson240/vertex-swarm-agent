# DoraHacks BUIDL Submission: Vertex Swarm Agent

- **Competition**: The Vertex Swarm Challenge 2026 (DoraHacks)
- **Prize Pool**: $27,000
- **Name of your Build**: `Vertex Swarm Agent`
- **Brief description of this Build**: `Leaderless coordinate-wise median BFT consensus and HMAC/monotonic P2P gossip firewall for resilient multi-agent swarms.`
- **Tags**: `Swarms`, `P2P`, `BFT`, `DePIN`, `Edge AI`, `Zero-Cloud`, `FoxMQ`, `Consensus`
- **GitHub Repo**: `https://github.com/manderson240/vertex-swarm-agent`
- **Contact Info**: `manderson240@gmail.com | Telegram: @manderson240`

## Describe your Build
### The problem: What are you solving?
Distributed drone, robot, and edge-AI agent fleets operating beyond reliable cloud connectivity fail under two classical threats: single-point-of-failure cloud coordinators and Byzantine sensor/vector poisoning attacks where compromised peers pull naive mean-averaged swarm decisions off-course.

### How it works
1. **Coordinate-Wise Median Riemannian BFT (`ManifoldBFTCoordinator`)**: Replaces vulnerable arithmetic means with breakdown-resistant coordinate-wise medians and enforces a symmetric $\text{HIHO} = 0.50 \pm 0.12$ stability envelope, isolating compromised peers (`disqualified_nodes`) and requiring a $\ge 2/3$ honest supermajority before emitting an aggregate consensus hash.
2. **Leaderless FoxMQ Gossip Integrity (`FoxMQGossipVerifier`)**: Signs peer frames with HMAC-SHA256 and enforces strict per-sender monotonic nonces so replayed or spoofed control frames are dropped in microseconds without centralized servers.

### Tech stack
Python 3.11+, pure stdlib cryptographic & geometric primitives (`hmac`, `hashlib`, `statistics`), `pytest`, and Cohezion V-Model Empirical Statistical Verification ($N=100$ trials).
