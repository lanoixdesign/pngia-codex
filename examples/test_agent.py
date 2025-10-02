from PIL import Image
from src.agent import create_agent, verify_agent

def main():
    # 1) Génère une image grise 96x96 (fichier de travail)
    img = Image.new("RGB", (96, 96), "gray")
    img.save("demo_agent.png")

    # 2) Crée un .pngia avec l’ADN numérique (aiDN)
    out = create_agent("demo_agent.png")  # => demo_agent.pngia
    if not isinstance(out, str):
        out = "demo_agent.pngia"
    print("[create_agent] ->", out)

    # 3) Vérifie l’authenticité (offline)
    rep = verify_agent(out)
    print("[verify_agent] ->", rep)

    # 4) Assert simple (facultatif pour script)
    assert rep["status"] in ("authentique", "altere")
    assert "iid" in rep

if __name__ == "__main__":
    main()
