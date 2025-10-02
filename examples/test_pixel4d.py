from PIL import Image
from src.pixel4d import add_pixel4d, quick_check

# Image de test (grise 96x96)
img = Image.new("RGB", (96, 96), "gray")
img.save("demo.png")

# Ajout du canal Pixel4D (aiPL)
out = add_pixel4d("demo.png")
print("OUT:", out)

# Vérification rapide
print("QC :", quick_check(out))
