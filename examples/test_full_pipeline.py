from PIL import Image
from src.pixel4d import add_pixel4d, quick_check
from src.agent import create_agent, verify_agent

def main():
    # 1) Image de base
    img_path = "demo_full.png"
    Image.new("RGB", (128, 128), "gray").save(img_path)

    # 2) Ajout du canal Pixel4D -> .pngia
    out = add_pixel4d(img_path)
    print("[add_pixel4d] ->", out)

    # 3) Quick-check Pixel4D
    qc = quick_check(out)
    print("[quick_check] ->", qc)
    assert qc["status"] in ("ok", "reserve", "suspect")

    # 4) Ajout de l’ADN numérique (sur le même fichier .pngia)
    out2 = create_agent(out, out)  # append aiDN dans le même fichier
    print("[create_agent in-place] ->", out2)

    # 5) Vérification offline de l’ADN
    rep = verify_agent(out2)
    print("[verify_agent] ->", rep)
    assert rep["status"] in ("authentique", "altere")

if __name__ == "__main__":
    main()
