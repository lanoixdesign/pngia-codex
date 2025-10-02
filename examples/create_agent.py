# Exemple de création

from src.agent import create_agent, verify_agent

# Création d’un fichier PNGIA
out = create_agent("image.png")

# Vérification du fichier créé
print(verify_agent(out))
