# Exemple de vérification

import sys
from src.pixel4d import quick_check
from src.agent import verify_agent


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python examples/verify_agent.py <file.pngia>")
		sys.exit(1)

	file_path = sys.argv[1]
	qc = quick_check(file_path)
	print("QUICK-CHECK", "status=", qc.get("status"), "score=", qc.get("score"))

	rep = verify_agent(file_path)
	print("OFFLINE", "status=", rep.get("status"), "iid=", rep.get("iid"))