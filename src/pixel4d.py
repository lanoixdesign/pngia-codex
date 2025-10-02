"""
Pixel 4D (canal IA) — Prototype minimal "robuste" pour quick-check.

Principe :
- Génère N positions pseudo-aléatoires dépendantes d'un seed (dérivé du fichier)
- Pour chaque position, calcule un fragment (8–12 bits) basé sur un descripteur local simple
- Stocke les fragments dans un blob compressé (tag AIPL) et permet un contrôle rapide

Ce prototype vise la pédagogie, pas la sécurité finale.
"""

from __future__ import annotations
import io, json, hashlib, random
from dataclasses import dataclass
from typing import Tuple, Iterable, List
import numpy as np
from PIL import Image

# Import utilitaires depuis pngia.py
from .pngia import TAG_AIPL, _append_blob, extract_blob, decompress, compress


# ---------- Header struct ----------

@dataclass
class AiPlHeader:
    ver: int = 1
    mode: int = 1      # 0=strict, 1=robuste
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


# ---------- Helpers ----------

def _to_luma(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGBA")).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _prng_positions(seed_int: int, w: int, h: int, n: int) -> Iterable[Tuple[int, int]]:
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


def _pack_bits(values: Iterable[int], frag_bits: int) -> bytes:
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


def _unpack_bits(buf: bytes, frag_bits: int, n: int) -> List[int]:
    vals: List[int] = []
    bitlen = len(buf) * 8
    bitpos = 0
    while len(vals) < n and bitpos + frag_bits <= bitlen:
        bytepos = bitpos // 8
        offset = bitpos % 8
        window = int.from_bytes(buf[bytepos:bytepos + 8], "big")  # fenêtre 64 bits
        shift = (8 * 8 - offset - frag_bits)
        vals.append((window >> shift) & ((1 << frag_bits) - 1))
        bitpos += frag_bits
    return vals


def _seed_from_file(img_path: str) -> int:
    with open(img_path, "rb") as f:
        return int.from_bytes(hashlib.sha256(f.read()).digest()[:16], "big")


# ---------- Public API ----------

def add_pixel4d(img_path: str,
                out_path: str | None = None,
                frag_bits: int = 12,
                density: int = 250,
                block: int = 8) -> str:
    """Crée (ou met à jour) un fichier .pngia en ajoutant le canal aiPL."""
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    y = _to_luma(img)

    seed = _seed_from_file(img_path)
    salt = 1337

    n = max(1, int(density * (w * h) / 1_000_000))
    frags = []
    for (xi, yi) in _prng_positions(seed, w, h, n):
        frags.append(_descriptor_fragment(y, xi, yi, block, salt, frag_bits))

    header = AiPlHeader(w=w, h=h, block=block, frag_bits=frag_bits,
                        density=density, seed=seed, salt=salt)

    blob = header.to_json() + b"\n" + _pack_bits(frags, frag_bits)
    comp = compress(blob)

    # Détermination du chemin de sortie
    if out_path is None:
        lower = img_path.lower()
        if lower.endswith(".png"):
            out_path = img_path[:-4] + ".pngia"
        elif lower.endswith(".jpg"):
            out_path = img_path[:-4] + ".jpegia"
        elif lower.endswith(".jpeg"):
            out_path = img_path[:-5] + ".jpegia"
        else:
            out_path = img_path + ".pngia"

    # Sauvegarde de l'image visible puis append du blob tagué
    img.save(out_path, format="PNG")
    _append_blob(out_path, TAG_AIPL, comp)
    return out_path


def quick_check(file_path: str, min_ok: float = 0.95, min_warn: float = 0.80) -> dict:
    """Vérification rapide (Pixel4D) sur un .pngia."""
    with open(file_path, "rb") as f:
        data = f.read()

    comp = extract_blob(data, TAG_AIPL)
    if comp is None:
        return {"status": "non_verifiable", "reason": "aipl_absent"}

    blob = decompress(comp)
    header_json, payload = blob.split(b"\n", 1)
    hdr = AiPlHeader.from_json(header_json)

    # Re-ouvrir l'image visible (portion avant le blob AIPL)
    idx = data.rfind(TAG_AIPL)
    img = Image.open(io.BytesIO(data[:idx])).convert("RGBA")
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
