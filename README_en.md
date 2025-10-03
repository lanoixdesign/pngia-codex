# PNGIA Codex ![CI](https://github.com/lanoixdesign/pngia-codex/actions/workflows/tests.yml/badge.svg)

Public prototype for **PNGIA**, **Pixel 4D**, and **Digital DNA** — concepts invented by **Micaël Lanoix**.  
Goal: provide a clear codebase to **create**, **embed**, and **verify** the authenticity of an image.

> ⚠️ **Status: educational prototype**  
> This repo demonstrates the full workflow but does not yet include:  
> - Real **Ed25519 signatures**  
> - **Merkle tree per tiles**  
> - Proper **PNG chunks** (here we append tagged blobs for the demo)  

---

## ⚙️ Features (MVP)

- **Digital DNA (aiDN)**: compressed manifest (SHA-256 hash, unique ID, timestamp)  
- **Pixel 4D (aiPL)**: AI channel with integrity fragments for quick-check verification  
- **Encapsulation**: append tagged blocks at the end of `.pngia` files  
- **Verification**:  
  - *Quick-check* with Pixel 4D (matching score)  
  - Offline verification of the Digital DNA agent (global hash)  

---

## 📦 Installation

```bash
git clone https://github.com/lanoixdesign/pngia-codex.git
cd pngia-codex
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Quick Example

```python
from src.agent import create_agent, verify_agent
from src.pixel4d import quick_check

# Create a certified file
out = create_agent("image.png")

# Quick-check (Pixel4D)
print(quick_check(out))

# Full verification (Digital DNA)
print(verify_agent(out))
```

Example output:

```
QUICK-CHECK  score=0.97  status=ok
OFFLINE      status=authentic  iid=iid-demo-0001
```

---

## 📊 Samples

The [`samples/`](samples/) folder contains:
- `example.png` : original image  
- `example.pngia` : same image encapsulated with **Pixel4D (aiPL)** and **Digital DNA (aiDN)**

---

## 🧱 Roadmap

- [ ] Implement **Merkle tree per tiles**  
- [ ] Add **Ed25519 signature** (RFC 8032)  
- [ ] Store data in proper **PNG chunks** (ancillary, safe-to-copy)  
- [ ] Integrate an external registry (PKI / blockchain)  
- [ ] WebAssembly (WASM) verification for browsers  

---

## 📚 Credits & License

**Concept & Design**: Micaël Lanoix — PNGIA / Pixel 4D / Digital DNA  
**Code**: reference prototype, released under **MIT License**.
