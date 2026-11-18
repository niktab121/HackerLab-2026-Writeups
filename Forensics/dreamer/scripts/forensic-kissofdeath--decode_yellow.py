from PIL import Image
import numpy as np
import subprocess
import sys

def decode(path):
    im = np.array(Image.open(path).convert('RGB')).astype(int)
    mask = (im[:,:,0]>170)&(im[:,:,1]>170)&(im[:,:,2]<im[:,:,0]-25)&(im[:,:,2]<im[:,:,1]-25)
    y,x = np.where(mask)
    grid = np.zeros((8,15),int)
    for a,b in zip(x,y):
        r,c = round((b-3000)/20),round((a-2055)/20)
        if 0 <= r < 8 and 0 <= c < 15:
            grid[r,c] = 1
    assert all(grid[1:].sum(axis=1)%2 == 1)
    assert all(grid[:,1:].sum(axis=0)%2 == 1)
    values = np.array([64,32,16,8,4,2,1]) @ grid[1:]
    return values

if __name__ == '__main__':
    import glob
    values = [decode(p) for p in sorted(glob.glob('pdfpages/*.png'))]
    assert len(values) == 19
    assert all(np.array_equal(v,values[0]) for v in values)
    print('Validation: 19 pages concordantes; parités des données correctes.')
    if '--report' in sys.argv:
        v = values[0]
        answer = f'{v[5]:02d}/{v[6]:02d}/{2000+v[7]} {v[4]:02d}:{v[1]:02d} ' + ''.join(f'{v[i]:02d}' for i in [13,12,11,10])
        result = subprocess.run(['/CHEMIN_LOCAL/CTFHUB/.venv/bin/python','/CHEMIN_LOCAL/CTFHUB/agent_bridge.py','--challenge','Dreamer','--flag',answer,'--source','codex'],capture_output=True,text=True)
        print('Transmission réussie.' if result.returncode == 0 else 'Échec: '+result.stderr.splitlines()[-1])
