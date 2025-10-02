from PIL import Image
from src.pixel4d import add_pixel4d, quick_check
from src.agent import create_agent, verify_agent

def test_full_pipeline(tmp_path):
    p = tmp_path / "demo.png"
    Image.new("RGB", (64, 64), "gray").save(p)
    out = add_pixel4d(str(p))
    qc = quick_check(out)
    assert qc["checked"] > 0

    out2_path = tmp_path / "agent.png"
    create_agent(out, out2_path)
    rep = verify_agent(str(out2_path))
    assert rep["status"] in ("authentique", "altere")
