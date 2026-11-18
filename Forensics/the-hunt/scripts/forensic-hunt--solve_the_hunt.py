#!/usr/bin/env python3
"""Decode The hunt's ICMP XOR exfiltration from a PCAP."""
import argparse, subprocess
KEY=b'n0rthstar_2024!!'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('pcap');a=ap.parse_args()
    cmd=['tshark','-r',a.pcap,'-Y','icmp.type==8 && ip.dst==203.0.113.15','-T','fields','-e','icmp.seq','-e','icmp.data']
    rows=[]
    for line in subprocess.check_output(cmd,text=True).splitlines():
        seq,hexdata=line.split('\t')
        if hexdata: rows.append((int(seq),bytes.fromhex(hexdata)))
    out=b''
    for _,data in sorted(rows):
        out += bytes(x ^ KEY[i%len(KEY)] for i,x in enumerate(data[4:]))
    print(out.decode(errors='replace'))
    print('EXPURGE')
if __name__=='__main__':main()
