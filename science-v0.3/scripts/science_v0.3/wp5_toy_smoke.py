from pyscf import gto, scf


mol = gto.M(atom="H 0 0 0; H 0 0 0.74", basis="sto-3g", verbose=0)
mf = scf.RHF(mol)
energy = float(mf.kernel())
print("WP5_TOY_SMOKE_OK", bool(mf.converged), f"{energy:.10f}")
raise SystemExit(0 if mf.converged else 2)
