from pathlib import Path
import json,subprocess,zipfile,sqlite3,re,math,collections,hashlib
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
import sys
R=Path(sys.argv[1]).resolve();results={}
def put(k,v):results[k]=v
p=R/'forensic/ghot/new/new/crtsh-dump.pem'
certs=[x509.load_pem_x509_certificate(b) for b in re.findall(rb'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',p.read_bytes(),re.S)]
root=x509.load_pem_x509_certificate((R/'forensic/ghot/il mandante/borealisCA-root.pem').read_bytes())
ski=root.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest
fleet=[]
for c in certs:
 try:
  if c.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier).value.key_identifier==ski:fleet.append(c)
 except x509.ExtensionNotFound:pass
ns=[c.public_key().public_numbers().n for c in fleet];pairs=[]
for i,a in enumerate(ns):
 for j,b in enumerate(ns[i+1:],i+1):
  g=math.gcd(a,b)
  if g>1:pairs.append({'relation':'module identique' if a==b else 'facteur propre partagé','bits':g.bit_length()})
put('Il Mandante',{'certificats':len(certs),'flotte_AKI':len(fleet),'tailles_bits':dict(collections.Counter(n.bit_length() for n in ns)),'relations_pgcd':pairs,'blob_octets':(R/'forensic/ghot/new/new/blob-capture-c2node.enc').stat().st_size,'note':'Aucun déchiffrement effectué.'})
p=R/'ghost/nordlink_device/data/data/nrv.nordlink/databases/nordlink.db'
c=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
put('Ghost Ratchet',{'messages':c.execute('select count(*) from messages').fetchone()[0],'directions':c.execute('select direction,count(*) from messages group by direction').fetchall(),'archive_dupliquee':hashlib.sha256((R/'ghost/GHOST-RATCHET.zip').read_bytes()).digest()==hashlib.sha256((R/'forensic/ghost/GHOST-RATCHET.zip').read_bytes()).digest()})
p=R/'forensic/memento/assets_scelle-P7.enc';b=p.read_bytes();put('Memento',{'octets':len(b),'en_tete_OpenSSL':b.startswith(b'Salted__'),'sel_octets':8,'chiffre_octets':len(b)-16,'out_bin_octets':(R/'forensic/memento/work/out.bin').stat().st_size})
put('Furgitif',{'archive':[{'nom':i.filename,'octets':i.file_size,'chiffre':bool(i.flag_bits&1)} for i in zipfile.ZipFile(R/'forensic/furgitif/confidential.zip').infolist()]})
# No archive extraction or execution; inspect the Docker manifest only.
m=json.loads((R/'forensic/hunt/relay/manifest.json').read_text());put('The hunt',{'images':len(m),'couches':len(m[0]['Layers']),'couches_toutes_presentes':all((R/'forensic/hunt/relay'/p).is_file() for p in m[0]['Layers'])})
for key,path in [('The hunt PCAP','forensic/hunt/capture.pcap'),('Il Mandante PCAP','forensic/ghot/capture-poste.pcap'),('Broken Handshake PCAP','misc/deaddrop/broken/challenge/tls_handshake.pcapng')]:
 r=subprocess.run(['tshark','-r',str(R/path),'-T','fields','-e','frame.number'],capture_output=True,text=True)
 put(key,{'code_retour':r.returncode,'paquets':len(r.stdout.splitlines())})
print(json.dumps(results,ensure_ascii=False,indent=2))
