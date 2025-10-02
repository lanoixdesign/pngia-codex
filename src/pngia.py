# Encapsulation PNGIA
"""
Encapsulation prototype PNGIA.
On ajoute deux blocs à la fin du fichier image:
- TAG aiDN: b"\x00PNGIA\x00" + uint32 size + payload (zlib)
- TAG aiPL: b"\x00AIPL\x00" + uint32 size + payload (zlib)


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