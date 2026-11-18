#!/usr/bin/env python3
"""TERVALIS 06 forensic solver: extraction, audit, GPS correction, SIGINT triangulation."""
import argparse,csv,io,json,math,sqlite3,statistics,zipfile,re,collections,pathlib
from datetime import datetime,timezone
P=pathlib.Path

def rows(p):
 with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def hav(a,b,c,d):
 r=6371; p1,p2=map(math.radians,(a,c)); dp=p2-p1; dl=math.radians(d-b)
 return 2*r*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2)))
def section(s):print('\n'+'='*16+' '+s+' '+'='*16)
def stamp(s):return s.replace('Z','+00:00')
def inspect_db(p):
 c=sqlite3.connect(str(p)); c.row_factory=sqlite3.Row
 for t, in c.execute("select name from sqlite_master where type='table'"):
  print('TABLE',t)
  for x in c.execute('select * from "'+t+'" limit 30'):print(dict(x))
 c.close()
def read_evidence(root):
 z=root/'evidence_files.zip'; out=root/'_extracted_evidence';out.mkdir(exist_ok=True)
 with zipfile.ZipFile(z) as f:
  for x in f.infolist():
   dest=(out/x.filename).resolve()
   if not dest.is_relative_to(out.resolve()):continue
   f.extract(x,out)
 for p in sorted(out.rglob('*')):
  if p.is_file():
   print('\nFILE',p.relative_to(out))
   if p.suffix=='.db':inspect_db(p)
   else:print(p.read_text(errors='replace')[:15000])
 return out

def fit_gps(pings,registry):
 # GPS obfuscation may be an affine transform; report candidate shifts rather than assume.
 section('GPS: observations et hypothèses de décalage')
 for x in pings[::max(1,len(pings)//18)]:print(x['timestamp_utc'],x['latitude'],x['longitude'],x['speed_kmh'],x['status'])
 last=pings[-1]; print('Dernier point brut:',dict(last))
 # Physical coordinates can be recovered by calibrating to a known HQ departure.
 hq=next((x for x in registry if x['code']=='TSD-HQ'),None)
 if hq:
  for x in pings:
   if '2024-11-03T14:15'<=x['timestamp_utc']<='2024-11-03T14:20':
    offlat=float(x['latitude'])-float(hq['latitude']);offlon=float(x['longitude'])-float(hq['longitude'])
    print('Hypothèse offset GPS à HQ:',round(offlat,5),round(offlon,5))
    print('Dernière position corrigée:',round(last['latitude']-offlat,5),round(last['longitude']-offlon,5))
    break

def triangulate(records,stations,diag):
 section('SIGINT: triangulation et corrections')
 print('Nombre de captures fréquence cible:',len(records))
 for d in diag:
  print('DIAGNOSTIC',json.dumps(d,ensure_ascii=False)[:1800])
 bytime=collections.defaultdict(list)
 for x in records:
  t=x['timestamp'][:16];bytime[t].append(x)
 for t,grp in sorted(bytime.items()):
  if not ('2024-11-03T14:00'<=t<='2024-11-03T17:30'):continue
  if len(set(x['station_id'] for x in grp))<2:continue
  # Bearings: true azimuth clockwise from north. Convert to local east/north.
  lines=[]
  for x in grp:
   st=stations.get(x['station_id']);
   if not st:continue
   bearing=float(x['bearing_deg']);rad=math.radians(bearing)
   lat,lon=float(st['lat']),float(st['lon']); east=lon*math.cos(math.radians(64))*111.2;north=lat*111.2
   dx,dy=math.sin(rad),math.cos(rad); nx,ny=-dy,dx
   lines.append((nx,ny,nx*east+ny*north,x['station_id']))
  aa=bb=cc=dd=ee=0
  for nx,ny,k,_ in lines:
   aa+=nx*nx;bb+=nx*ny;cc+=ny*ny;dd+=nx*k;ee+=ny*k
  det=aa*cc-bb*bb
  if abs(det)<1e-8:continue
  east=(dd*cc-bb*ee)/det;north=(aa*ee-bb*dd)/det
  lat=north/111.2;lon=east/(math.cos(math.radians(64))*111.2)
  if -90<=lat<=90 and -180<=lon<=180:print(t,'estimate',round(lat,5),round(lon,5),'stations',len(lines))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('zip',nargs='?',default='challenge.zip');ap.add_argument('--full',action='store_true',help='Print forensic evidence and transfer DB');a=ap.parse_args()
 z=P(a.zip).expanduser().resolve();root=z.parent/'tervalis_extracted';root.mkdir(exist_ok=True)
 with zipfile.ZipFile(z) as f:
  for item in f.infolist():
   dest=(root/item.filename).resolve()
   if not dest.is_relative_to(root.resolve()):raise ValueError('unsafe ZIP path')
   f.extract(item,root)
 if (root/'challenge').exists():root=root/'challenge'
 section('PROTOCOLE');print((root/'reporting_format.md').read_text())
 section('REGISTRE');fac=rows(root/'facility_registry.csv');print(*fac,sep='\n')
 section('FORENSIC');e=read_evidence(root) if a.full else None
 if not a.full:
  with zipfile.ZipFile(root/'evidence_files.zip') as f:
   for name in f.namelist():
    if any(k in name for k in ['shift_notes','gate_map','manifest_VLD-2024-1103']):print(name,'\n',f.read(name).decode(errors='replace'))
 section('CHECKPOINTS')
 checkpoints=[x for x in rows(root/'checkpoint_logs.csv') if x['vehicle_plate']=='VLD-74-OPS' and x['timestamp_utc'].startswith('2024-11-03')]
 for x in checkpoints:print(x)
 section('DISPATCH')
 for line in (root/'dispatch_records.jsonl').open():
  x=json.loads(line)
  if x.get('vehicle')=='VLD-74-OPS' and x.get('timestamp_utc','').startswith('2024-11-03'):print(x)
 section('VEHICLE DB')
 db=sqlite3.connect(root/'vehicle_tracking.db');db.row_factory=sqlite3.Row
 pings=[dict(x) for x in db.execute("select * from gps_pings where plate=? and timestamp_utc between ? and ? order by timestamp_utc",('VLD-74-OPS','2024-11-03T13:30','2024-11-03T18:00'))]
 print('GPS points:',len(pings))
 for x in db.execute("select * from alerts where plate=? and timestamp_utc like ?",('VLD-74-OPS','2024-11-03%')):print('ALERT',dict(x))
 if pings:fit_gps(pings,fac)
 db.close()
 stations={x['id']:x for x in json.loads((root/'sigint_stations.json').read_text())};diag=json.loads((root/'station_diagnostics.json').read_text())
 records=[x for x in rows(root/'signal_intel.csv') if abs(float(x['frequency_mhz'])-148.325)<.001]
 triangulate(records,stations,diag)
 section('CANDIDATS')
 for x in fac:
  if x['region']=='Nordvelt':
   print(x['code'],x['region'],x['latitude'],x['longitude'],'(coordonnées absentes => ne pas inventer)')
 print('\nFormat: EXPURGE')
 print('IMPORTANT: identifier le décalage/calibration SIGINT et la destination réelle avant soumission.')
if __name__=='__main__':main()
