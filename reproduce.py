from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parent
for d in ('results','review'): (r/d).mkdir(exist_ok=True)
for n in range(1,5):
 subprocess.run(['node',str(r/'src/count_masks.cjs'),str(n),str(r/f'results/counts_n{n}.json')],check=True)
 subprocess.run(['node',str(r/'src/replay_dp.js'),str(n)],check=True)
for f in ('moves.py','independent_moves.py','certify.py'):
 subprocess.run([sys.executable,str(r/'src'/f)],check=True)
print('Complete exact verification for n=1..4 passed.')
