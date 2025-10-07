# PNGIA Codex ![CI](https://github.com/lanoixdesign/pngia-codex/actions/workflows/tests.yml/badge.svg)

Prototype public pour **PNGIA**, **Pixel 4D** et **ADN numérique** — concepts inventés par **Micaël Lanoix**.  
Objectif : fournir une base de code claire pour **créer**, **encapsuler** et **vérifier** l’authenticité d’une image.

> ⚠️ **Statut : prototype pédagogique**  
> Ce repo illustre le flux complet mais n’intègre pas encore :  
> - Signature **Ed25519** réelle  
> - **Merkle par tuiles**  
> - Chunks **PNG** conformes (ici on append des blobs balisés pour la démo)  

---

## ⚙️ Fonctionnalités (MVP)

- **ADN numérique (aiDN)** : manifeste compressé (hash SHA-256, identifiant unique, horodatage)  
- **Pixel 4D (aiPL)** : canal IA avec fragments d’intégrité pour un *quick-check* rapide  
- **Encapsulation** : ajout de blocs balisés en fin de fichier `.pngia`  
- **Vérification** :  
  - *quick-check* via Pixel 4D (score de correspondance)  
  - vérification hors ligne de l’agent ADN (hash global)  

---

## 📦 Installation

```bash
git clone https://github.com/lanoixdesign/pngia-codex.git
cd pngia-codex
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Exemple rapide

```python
from src.agent import create_agent, verify_agent
from src.pixel4d import quick_check

# Créer un fichier certifié
out = create_agent("image.png")

# Vérification rapide (Pixel4D)
print(quick_check(out))

# Vérification complète (ADN numérique)
print(verify_agent(out))
```

Exemple de sortie :

```
QUICK-CHECK  score=0.97  status=ok
OFFLINE      status=authentique  iid=iid-demo-0001
```

---

## 📊 Samples

Le dossier [`samples/`](samples/) contient :
- `example.png` : image originale
- `example.pngia` : même image encapsulée avec **Pixel4D (aiPL)** et **ADN numérique (aiDN)**

---

## 🧱 Roadmap

- [ ] Implémenter **Merkle par tuiles**  
- [ ] Ajouter signature **Ed25519** (RFC 8032)  
- [ ] Encapsulation en vrais **chunks PNG** (ancillary, safe-to-copy)  
- [ ] Intégrer un registre externe (PKI / blockchain)  
- [ ] Vérification **WebAssembly (WASM)** pour navigateur  

---

## 📖 À propos du livre

Ce projet est directement issu du livre PNGIA — L’ADN numérique des images, écrit par Micaël Lanoix.
L’ouvrage explore la genèse du concept de Pixel 4D, la structure d’un ADN numérique pour les médias visuels,
et les implications éthiques, juridiques et spirituelles de la traçabilité numérique.

“Ce n’est pas seulement une technologie, c’est une vision : celle d’un futur où chaque image porte la mémoire de sa vérité.”
— Micaël Lanoix

📘 Disponible sur Amazon :
👉 https://www.amazon.fr/dp/B0FTVMM8QW

🔗 DOI of the technical report: [https://doi.org/10.5281/zenodo.17285510](https://doi.org/10.5281/zenodo.17285510)

---

## 📚 Crédit & Licence

**Conception** : Micaël Lanoix — PNGIA / Pixel 4D / ADN numérique  
**Code** : base de référence libre, licence **MIT**.
