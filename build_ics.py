import re
import json,glob,os,sys,datetime
src=sys.argv[1]; out=sys.argv[2]
OPEN={"brief","filming","editing","revisions"}
def esc(t): return (t or "").replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
def fold(line):
    b=line.encode(); res=[]
    while len(b)>73:
        cut=73
        while (b[cut]&0xC0)==0x80: cut-=1
        res.append(b[:cut].decode()); b=b" "+b[cut:]
    res.append(b.decode()); return "\r\n".join(res)
evs=[]
for f in sorted(glob.glob(os.path.join(src,"*.json"))):
    j=json.load(open(f)); d=j.get("data",j)
    if d.get("status") in OPEN and d.get("due"): evs.append((d["due"],os.path.basename(f)[:-5],d))
evs.sort(key=lambda x:(x[0],x[1]))
now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
L=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//UGC Portal//EN","CALSCALE:GREGORIAN","METHOD:PUBLISH","X-WR-CALNAME:UGC Portal","X-PUBLISHED-TTL:PT6H","REFRESH-INTERVAL;VALUE=DURATION:PT6H"]
for due,i,d in evs:
    day=datetime.date.fromisoformat(due); nxt=day+datetime.timedelta(days=1)
    title=d.get("title","").replace("Gig: ","")
    b=d.get("brand","").strip()
    if b:
        title=re.sub(r"\b"+re.escape(b)+r"(\s+One)?\b","",title,flags=re.I)
        title=re.sub(r"\s+(with|for|by|at|x|from)\s*$","",title.strip(),flags=re.I)
        title=re.sub(r"\s{2,}"," ",title).strip(" -,:")
    L+=["BEGIN:VEVENT",f"UID:{i}@ugc-portal",f"DTSTAMP:{now}",f"DTSTART;VALUE=DATE:{day:%Y%m%d}",f"DTEND;VALUE=DATE:{nxt:%Y%m%d}",
        fold("SUMMARY:"+esc(f'UGC - {d.get("brand","")}, {title}')),"TRANSP:TRANSPARENT",
        "BEGIN:VALARM","ACTION:DISPLAY",fold("DESCRIPTION:"+esc(title+" is due tomorrow")),"TRIGGER:-PT15H","END:VALARM","END:VEVENT"]
L.append("END:VCALENDAR")
open(out,"w",newline="").write("\r\n".join(L)+"\r\n")
print(len(evs),"events")
for due,i,d in evs: print(due,d.get("brand"),d.get("title"))
