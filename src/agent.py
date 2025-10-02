# Canal IA (fragments d’authenticité)

import hashlib, zlib, json
from PIL import Image

def compute_root(img):
    """Hash global simplifié (à remplacer par Merkle par tuiles)."""
    return hashlib.sha256(img.tobytes()).hexdigest()

def create_agent(img_path, key_id="demo-key"):
    img = Image.open(img_path).convert("RGBA")
    root = compute_root(img)

    manifest = {
        "ver": 1,
        "alg": {"hash": "SHA-256", "sig": "Ed25519", "comp": "zlib"},
        "iid": "iid-demo-0001",
        "ts0": "2025-01-01T00:00:00Z",
        "root": root,
        "kid": key_id,
        "policy": {"edits": ["crop", "color"], "allow": True},
        "journal": []
    }

    agent_bin = zlib.compress(json.dumps(manifest).encode("utf-8"))

    out_path = img_path.replace(".png", ".pngia")
    img.save(out_path)

    with open(out_path, "ab") as f:
        f.write(b"\x00PNGIA\x00")
        f.write(len(agent_bin).to_bytes(4, "big"))
        f.write(agent_bin)

    return out_path

def verify_agent(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    tag = b"\x00PNGIA\x00"
    idx = data.rfind(tag)
    if idx < 0:
        return {"status": "non_verifiable", "reason": "agent_absent"}

    size = int.from_bytes(data[idx+len(tag):idx+len(tag)+4], "big")
    agent_bin = data[idx+len(tag)+4:idx+len(tag)+4+size]
    manifest = json.loads(zlib.decompress(agent_bin).decode("utf-8"))

    import io
    img = Image.open(io.BytesIO(data[:idx]))
    root_now = hashlib.sha256(img.tobytes()).hexdigest()

    return {
        "status": "authentique" if root_now == manifest["root"] else "altere",
        "iid": manifest["iid"],
        "root_ref": manifest["root"],
        "root_now": root_now
    }
