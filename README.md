# Repository: pngia-codex

Below are the initial files to copy into your GitHub repository. Each section starts with a file path, followed by its full contents.

---

## README.md

```markdown
# PNGIA Codex

Prototype public pour **PNGIA**, **Pixel 4D** et **ADN numérique** — concepts inventés par **Micaël Lanoix**.\
Objectif : fournir une base de code claire pour **créer**, **encapsuler** et **vérifier** l’authenticité d’une image.

> ⚠️ Statut : **prototype pédagogique**. Ce repo illustre le flux complet mais n’intègre pas encore :
> - Signature **Ed25519** réelle (les champs sont prêts)
> - **Merkle par tuiles** (hash global simplifié ici)
> - Chunks **PNG** conformes (on append des blobs balisés pour la démo)

---

## ⚙️ Fonctionnalités (MVP)
- **ADN numérique (agent)** : manifeste compressé (root SHA-256, iid, algos, policy)
- **Pixel 4D (canal IA)** : plan auxiliaire compact (fragments d’intégrité) pour un *quick-check* rapide
- **Encapsulation** : append binaire avec tags `\x00PNGIA\x00` (aiDN) et `\x00AIPL\x00` (aiPL)
- **Vérification** :
  - *quick-check* via Pixel 4D (score de correspondance)
  - vérification hors ligne de l’agent (recalcul du hash global)

---

## 📦 Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Démarrage rapide
```bash
# 1) Créer un fichier .pngia avec ADN + Pixel4D
python examples/create_agent.py input.png

# 2) Vérifier l'authenticité (quick + offline)
python examples/verify_agent.py output.pngia
```

Exemple de sortie :
```
QUICK-CHECK  score=0.97  status=ok
OFFLINE      status=authentique  iid=iid-demo-0001
```

---

## 🧱 Roadmap technique
- [ ] Remplacer le hash global par **Merkle par tuiles** (Annexe du livre)
- [ ] Ajouter **Ed25519** (RFC 8032) avec CBOR canonique (RFC 8949)
- [ ] Écrire/relire de vrais **chunks PNG** (ancillary, safe-to-copy) au lieu d’append naïf
- [ ] Intégrer un **registre** (log de transparence + ancrage) et reçu `aiAN`
- [ ] WASM/JS pour vérification web (quick + offline)

---

## 📚 Crédit & Licence
**Conception** : Micaël Lanoix — PNGIA / Pixel 4D / ADN numérique.\
**Code** : base de référence libre.

Ce repo est sous licence **MIT** (voir `LICENSE`).
```

---

## LICENSE

```text
MIT License

Copyright (c) 2025 Micaël Lanoix

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## requirements.txt

```text
Pillow>=10.0
numpy>=1.26
```

---

## src/__init__.py

```python
__all__ = ["agent", "pixel4d", "pngia"]
```

---

## src/pngia.py

```python
"""
Encapsulation prototype PNGIA.
On ajoute deux blocs à la fin du fichier image:
 - TAG aiDN: b"\x00PNGIA\x00" + uint32 size + payload (zlib)
 - TAG aiPL: b"\x00AIPL\x00"  + uint32 size + payload (zlib)

Dans une implémentation réelle, ces blobs seraient stockés en chunks PNG
(ancillary, private, safe-to-copy) avec CRC.
"""
import zlib

TAG_AIDN = b"\x00PNGIA\x00"
TAG_AIPL = b"\x00AIPL\x00"


def _append_blob(path_out: str, tag: bytes, payload: bytes) -> None:
    with open(path_out, "ab") as f:
        f.write(tag)
        f.write(len(payload).to_bytes(4, "big"))
        f.write(payload)


def extract_blob(data: bytes, tag: bytes) -> bytes | None:
    idx = data.rfind(tag)
    if idx < 0:
        return None
    size = int.from_bytes(data[idx + len(tag): idx + len(tag) + 4], "big")
    return data[idx + len(tag) + 4: idx + len(tag) + 4 + size]


def compress(obj_bytes: bytes) -> bytes:
    return zlib.compress(obj_bytes, 9)


def decompress(obj_bytes: bytes) -> bytes:
    return zlib.decompress(obj_bytes)
```

---

## src/agent.py

```python
import hashlib, json
from datetime import datetime, timezone
from PIL import Image
import io
from .pngia import TAG_AIDN, _append_blob, compress, extract_blob, decompress


def compute_root(img: Image.Image) -> str:
    """Hash global simplifié (remplacer par Merkle par tuiles)."""
    return hashlib.sha256(img.tobytes()).hexdigest()


def create_agent(img_path: str, out_path: str | None = None, key_id: str = "kid:demo", iid: str = "iid-demo-0001") -> str:
    img = Image.open(img_path).convert("RGBA")
    root = compute_root(img)

    manifest = {
        "ver": 1,
        "alg": {"hash": "SHA-256", "sig": "Ed25519", "comp": "zlib"},
        "iid": iid,
        "ts0": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tiles": {"mode": "full"},
        "root": root,
        "salt": "",  # TODO: utiliser un sel aléatoire pour Merkle
        "kid": key_id,
        "policy": {"edits": ["crop", "color"], "allow": True},
        "journal": []
        # "sig": ...  # TODO: Ed25519 sur bytes canoniques
    }

    import json as _json
    payload = compress(_json.dumps(manifest, separators=(",", ":")).encode("utf-8"))

    if out_path is None:
        if img_path.lower().endswith(".png"):
            out_path = img_path[:-4] + ".pngia"
        else:
            out_path = img_path + ".pngia"

    img.save(out_path)
    _append_blob(out_path, TAG_AIDN, payload)
    return out_path


def verify_agent(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        data = f.read()

    agent_blob = extract_blob(data, TAG_AIDN)
    if agent_blob is None:
        return {"status": "non_verifiable", "reason": "agent_absent"}

    manifest = json.loads(decompress(agent_blob).decode("utf-8"))

    # Recompute hash on the displayed image bytes (before the agent blob)
    # We use a conservative approach: read the image portion by re-opening from bytes
    idx = data.rfind(TAG_AIDN)
    img = Image.open(io.BytesIO(data[:idx]))
    img = img.convert("RGBA")
    root_now = hashlib.sha256(img.tobytes()).hexdigest()

    status = "authentique" if root_now == manifest["root"] else "altere"
    return {
        "status": status,
        "iid": manifest.get("iid"),
        "root_ref": manifest.get("root"),
        "root_now": root_now,
        "alg": manifest.get("alg"),
    }
```

---

## src/pixel4d.py

```python
"""
Pixel 4D (canal IA) — Prototype minimal "robuste" pour quick-check.

Principe :
- Génère N positions pseudo-aléatoires dépendantes d'un seed (dérivé du fichier)
- Pour chaque position, calcule un fragment (8–12 bits) basé sur un descripteur local simple
- Stocke les fragments dans un blob compressé (tag AIPL) et permet un contrôle rapide

Ce prototype vise la pédagogie, pas la sécurité finale.
"""
from __future__ import annotations
import io, json, hashlib, zlib, random
from dataclasses import dataclass
from typing import Tuple
import numpy as np
from PIL import Image
from .pngia import TAG_AIPL, _append_blob, extract_blob, decompress, compress


@dataclass
class AiPlHeader:
    ver: int = 1
    mode: int = 1    # 0=strict, 1=robuste
    w: int = 0
    h: int = 0
    block: int = 8
    frag_bits: int = 12
    density: int = 250  # échantillons par mégapixel
    seed: int = 0
    salt: int = 1337

    def to_json(self) -> bytes:
        return json.dumps(self.__dict__, separators=(",", ":")).encode()

    @staticmethod
    def from_json(b: bytes) -> "AiPlHeader":
        d = json.loads(b.decode())
        return AiPlHeader(**d)


def _to_luma(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGBA")).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _prng_positions(seed_int: int, w: int, h: int, n: int):
    rnd = random.Random(seed_int)
    for _ in range(n):
        yield rnd.randrange(0, w), rnd.randrange(0, h)


def _descriptor_fragment(y: np.ndarray, x: int, y0: int, block: int, salt: int, frag_bits: int) -> int:
    H, W = y.shape
    bx = block // 2
    x0, x1 = max(0, x - bx), min(W, x + bx)
    y0_, y1 = max(0, y0 - bx), min(H, y0 + bx)
    patch = y[y0_:y1, x0:x1]
    mu = float(patch.mean()) if patch.size else 0.0
    gx = float(np.mean(np.diff(patch, axis=1))) if patch.shape[1] > 1 else 0.0
    gy = float(np.mean(np.diff(patch, axis=0))) if patch.shape[0] > 1 else 0.0
    v = f"{int(mu):03d}|{int(gx):+03d}|{int(gy):+03d}|{salt}"
    hsh = hashlib.sha256(v.encode()).digest()
    needed = (frag_bits + 7) // 8
    frag_bytes = hsh[:needed]
    val = int.from_bytes(frag_bytes, "big")
    mask = (1 << frag_bits) - 1
    return (val >> (needed * 8 - frag_bits)) & mask


def _pack_bits(values, frag_bits) -> bytes:
    acc = 0
    acc_bits = 0
    out = bytearray()
    for v in values:
        acc = (acc << frag_bits) | (v & ((1 << frag_bits) - 1))
        acc_bits += frag_bits
        while acc_bits >= 8:
            acc_bits -= 8
            out.append((acc >> acc_bits) & 0xFF)
            acc &= (1 << acc_bits) - 1
    if acc_bits:
        out.append((acc << (8 - acc_bits)) & 0xFF)
    return bytes(out)


def _unpack_bits(buf: bytes, frag_bits: int, n: int):
    vals = []
    bitlen = len(buf) * 8
    bitpos = 0
    while len(vals) < n and bitpos + frag_bits <= bitlen:
        bytepos = bitpos // 8
        offset = bitpos % 8
        window = int.from_bytes(buf[bytepos:bytepos + 8], "big")
        shift = (8 * 8 - offset - frag_bits)
        vals.append((window >> shift) & ((1 << frag_bits) - 1))
        bitpos += frag_bits
    return vals


def seed_from_bytes(b: bytes) -> int:
    return int.from_bytes(hashlib.sha256(b).digest()[:16], "big")


def add_pixel4d(img_path: str, out_path: str | None = None, frag_bits: int = 12, density: int = 250, block: int = 8) -> str:
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    y = _to_luma(img)

    # Seed déterministe basé sur l'image source (bytes du PNG minimal)
    with open(img_path, "rb") as f:
        seed = seed_from_bytes(f.read())

    n = max(1, int(density * (w * h) / 1_000_000))
    frags = []
    for (xi, yi) in _prng_positions(seed, w, h, n):
        frags.append(_descriptor_fragment(y, xi, yi, block, 1337, frag_bits))

    header = AiPlHeader(w=w, h=h, block=block, frag_bits=frag_bits, density=density, seed=seed)
    blob = header.to_json() + b"\n" + _pack_bits(frags, frag_bits)
    comp = compress(blob)

    if out_path is None:
        if img_path.lower().endswith(".png"):
            out_path = img_path[:-4] + ".pngia"
        else:
            out_path = img_path + ".pngia"

    img.save(out_path)
    _append_blob(out_path, TAG_AIPL, comp)
    return out_path


def quick_check(file_path: str, min_ok: float = 0.95, min_warn: float = 0.80) -> dict:
    with open(file_path, "rb") as f:
        data = f.read()

    comp = extract_blob(data, TAG_AIPL)
    if comp is None:
        return {"status": "non_verifiable", "reason": "aipl_absent"}

    blob = decompress(comp)
    header_json, payload = blob.split(b"\n", 1)
    hdr = AiPlHeader.from_json(header_json)

    # Re-ouvrir l'image visible
    idx = data.rfind(TAG_AIPL)
    img = Image.open(io.BytesIO(data[:idx])).convert("RGBA")
    # Ajuster taille si nécessaire
    if img.size != (hdr.w, hdr.h):
        img = img.resize((hdr.w, hdr.h), Image.BILINEAR)
    y = _to_luma(img)

    n = max(1, int(hdr.density * (hdr.w * hdr.h) / 1_000_000))
    stored = _unpack_bits(payload, hdr.frag_bits, n)

    matches = 0
    total = 0
    for k, (xi, yi) in enumerate(_prng_positions(hdr.seed, hdr.w, hdr.h, n)):
        if k >= len(stored):
            break
        calc = _descriptor_fragment(y, xi, yi, hdr.block, hdr.salt, hdr.frag_bits)
        total += 1
        if calc == stored[k]:
            matches += 1

    score = matches / total if total else 0.0
    if score >= min_ok:
        status = "ok"
    elif score >= min_warn:
        status = "reserve"
    else:
        status = "suspect"

    return {"status": status, "score": round(score, 4), "checked": total}
```

---

## examples/create_agent.py

```python
import sys
from src.agent import create_agent
from src.pixel4d import add_pixel4d

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python examples/create_agent.py <input.png>")
        sys.exit(1)

    input_path = sys.argv[1]
    # 1) Ajouter Pixel4D (aiPL) et obtenir un .pngia
    out = add_pixel4d(input_path)
    # 2) Ajouter l'ADN (aiDN) sur ce même fichier
    out2 = create_agent(out, out)  # out_path = out (in-place append)
    print("Created:", out2)
```

---

## examples/verify_agent.py

```python
import sys
from src.pixel4d import quick_check
from src.agent import verify_agent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python examples/verify_agent.py <file.pngia>")
        sys.exit(1)

    file_path = sys.argv[1]
    qc = quick_check(file_path)
    print("QUICK-CHECK", "status=", qc.get("status"), "score=", qc.get("score"))

    rep = verify_agent(file_path)
    print("OFFLINE", "status=", rep.get("status"), "iid=", rep.get("iid"))
```

---

## tests/test_smoke.py

```python
# Placeholders pour futur PyTest

def test_placeholder():
    assert True
