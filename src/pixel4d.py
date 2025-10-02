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
    mode: int = 1 # 0=strict, 1=robuste
    w: int = 0
    h: int = 0
    block: int = 8
    frag_bits: int = 12
    density: int = 250 # échantillons par mégapixel
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


    return {"status": status, "score": round(score, 4), "checked": total}