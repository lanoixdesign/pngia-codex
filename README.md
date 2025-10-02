# PNGIA Codex

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
git clone https://github.com/<ton-user>/pngia-codex.git
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

## 🧱 Roadmap

- [ ] Implémenter **Merkle par tuiles**  
- [ ] Ajouter signature **Ed25519** (RFC 8032)  
- [ ] Encapsulation en vrais **chunks PNG** (ancillary, safe-to-copy)  
- [ ] Intégrer un registre externe (PKI / blockchain)  
- [ ] Vérification **WebAssembly (WASM)** pour navigateur  

---

## 📚 Crédit & Licence

**Conception** : Micaël Lanoix — PNGIA / Pixel 4D / ADN numérique  
**Code** : base de référence libre, licence **MIT**.
