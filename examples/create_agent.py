# Exemple de création

import sys
from src.agent import create_agent
from src.pixel4d import add_pixel4d


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python examples/create_agent.py <input.png>")
		sys.exit(1)

	input_path = sys.argv[1]
	# 1) Ajouter Pixel4D (aiPL) et obtenir un .pngia
	out = add_pixel4d(input_path)
	# 2) Ajouter l'ADN (aiDN) sur ce même fichier
	out2 = create_agent(out, out) # out_path = out (in-place append)
	print("Created:", out2)
