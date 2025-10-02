from datetime import datetime, timezone
from PIL import Image
import io
import hashlib
import json as _json
from .pngia import TAG_AIDN, _append_blob, compress, extract_blob, decompress


def compute_root(img: Image.Image) -> str:
    """
    Hash global simplifié (remplacer par Merkle par tuiles).
    """
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
        "salt": "", # TODO: utiliser un sel aléatoire pour Merkle
        "kid": key_id,
        "policy": {"edits": ["crop", "color"], "allow": True},
        "journal": []
        # "sig": ... # TODO: Ed25519 sur bytes canoniques
    }

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

    manifest = _json.loads(decompress(agent_blob).decode("utf-8"))

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
    }