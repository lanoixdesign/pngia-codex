from PIL import Image
from src.agent import create_agent, verify_agent

def test_agent_roundtrip(tmp_path):
    p = tmp_path / "demo.png"
    Image.new("RGB", (64, 64), "gray").save(p)
    out = create_agent(str(p))
    rep = verify_agent(out)
    assert rep["status"] in ("authentique", "altere")
