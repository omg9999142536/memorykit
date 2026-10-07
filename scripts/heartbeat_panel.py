#!/usr/bin/env python3
# 学习进步心跳v4:增量制——只报「自上次心跳以来」的新变化;无变化则完全静默(空输出)。
import json, os, re, datetime, glob, subprocess
import os
H=os.environ.get('MEMORY_KIT_HOME', os.path.expanduser('~'))
now=datetime.datetime.now()
STATE=os.environ.get('MEMORY_KIT_STATE', f'{H}/.memory-kit/state.json')

def load_state():
    try: return json.load(open(STATE))
    except: return {}

def save_state(st):
    try:
        os.makedirs(os.path.dirname(STATE) or '.', exist_ok=True)
        json.dump(st, open(STATE,'w'), ensure_ascii=False)
    except: pass

st=load_state()
last_ts=st.get('ts')
last=datetime.datetime.fromtimestamp(last_ts) if last_ts else now - datetime.timedelta(hours=1)

def changed_since(path):
    try: return os.path.getmtime(path) > last.timestamp()
    except: return False

# --- custom knowledge-base sections (optional, generic) ---
# Set MEMORY_KIT_KB="name:regex:path,name:regex:path" to track your own knowledge bases
cnts={}
items=[]
for spec in (os.environ.get('MEMORY_KIT_KB') or '').split(','):
    parts = spec.strip().split(':', 2)
    if len(parts) != 3:
        continue
    name, pat, rel = parts
    try:
        s=open(f'{H}/{rel}',encoding='utf-8').read()
        tot=len(set(re.findall(pat,s)))
        cnts[name]=tot
        prev=st.get('counts',{}).get(name)
        delta=(tot-prev) if prev is not None else 0
        items.append((name,tot,delta))
    except: pass
inv=' · '.join(f'{tot}{name}' for name,tot,_ in items)

# --- axis deltas (since last heartbeat) ---
# Axis names are generic defaults; override with MEMORY_KIT_AXES="ff-method,gj-tools,..."
AXES = (os.environ.get('MEMORY_KIT_AXES') or
        'ff-methods,gj-tools,hb-env,jn-memory,ph-prefs,rw-tasks,xm-projects,yj-research,sj-clock').split(',')
axes_dir = os.environ.get('MEMORY_KIT_AXES_DIR', f'{H}/axes')
touched=[a for a in AXES if os.path.exists(f'{axes_dir}/{a.strip()}.md') and changed_since(f'{axes_dir}/{a.strip()}.md')]

# --- artifact deltas (since last heartbeat, logs excluded) ---
# Override with MEMORY_KIT_ARTIFACTS="glob1,glob2,..."
pats=[g.strip().replace('~',H) for g in (os.environ.get('MEMORY_KIT_ARTIFACTS') or
      '~/*.md,~/*.py').split(',') if g.strip()]
SKIP=re.compile(r'\.(log|tmp|pyc|idsig)$|心跳面板历史|\.heartbeat_state|cron\.log')
artifacts=set()
for p in pats:
    for f in glob.glob(p):
        if SKIP.search(f): continue
        if changed_since(f): artifacts.add(os.path.basename(f))

# --- site visits (optional, since last heartbeat) ---
# Set MEMORY_KIT_VISITS_CMD to a command printing "total:X human:Y"
visits=None
vcmd = os.environ.get('MEMORY_KIT_VISITS_CMD')
if vcmd:
    try:
        r=subprocess.run(vcmd, shell=True, capture_output=True, text=True, timeout=30)
        m=re.search(r'total:(\d+)\s+human:(\d+)', r.stdout)
        if m:
            v_tot,v_hum=int(m.group(1)),int(m.group(2))
            prev_h=st.get('visits_human')
            if prev_h is None or v_hum>prev_h:
                visits=(v_tot,v_hum, v_hum-(prev_h or 0))
    except: pass

changed = bool(touched) or bool(artifacts) or bool(visits) or any(d>0 for _,_,d in items)
if not changed:
    save_state({'ts':now.timestamp(),'counts':cnts,'visits_human':(visits[1] if visits else st.get('visits_human'))})
    raise SystemExit(0)   # 空输出=不推送

ts=now.strftime('%m-%d %H:%M')
out=[f'⏱ {ts} | 🧠 库存: {inv}']
d_add=[f'+{d}{n}' for n,tot,d in items if d>0]
if d_add: out.append('📈 新增: '+' · '.join(d_add))
if touched: out.append('📝 动轴: '+' '.join('**'+a.split('-')[0]+'**' for a in touched))
if artifacts:
    names=sorted(artifacts)
    out.append('🛠 产出: '+' · '.join(names[:6])+(f' 等{len(names)}件' if len(names)>6 else ''))
if visits: out.append(f'🌐 站点: 今日访问{visits[0]} 真人{visits[1]}(+{visits[2]})')
for a in touched[:2]:
    try:
        L=[l for l in open(f'{axes_dir}/{a.strip()}.md',encoding='utf-8').read().split('\n')
           if l.strip().startswith('- **') or re.match(r'^[a-z]{2}-[0-9]+｜', l.strip())]
        if L:
            last_l=L[-1]
            m=re.search(r'(?:\*\*(.+?)\*\*|^[a-z]{2}-[0-9]+)｜(.+?)(?:（|｜|$)', last_l)
            tip=f'{m.group(1)[:12]}:{m.group(2)[:18]}' if m else last_l.strip('- *｜')[:22]
            out.append(f'· {a.split("-")[0]} {tip}')
    except: pass
parts=[]
if d_add: parts.append('入库/新增'+', '.join(d_add))
if artifacts: parts.append(f'产出{len(artifacts)}件')
if visits: parts.append(f'真人访问+{visits[2]}')
out.append('📌 '+(parts and '，'.join(parts)+'。' or '小幅推进。'))
print('\n'.join(out))

# archive (only when changed)
hist=os.environ.get('MEMORY_KIT_HISTORY', f'{H}/.memory-kit-heartbeat-history.md')
try:
    n=sum(1 for l in open(hist,encoding='utf-8') if l.startswith('## 心跳#'))
    os.makedirs(os.path.dirname(hist) or '.', exist_ok=True)
    with open(hist,'a',encoding='utf-8') as f:
        f.write(f'\n## 心跳#{n+1} · {ts}\n\n'+'\n'.join(out[1:])+'\n')
except Exception as e:
    import sys; print('ARCH_ERR:', e, file=sys.stderr)

save_state({'ts':now.timestamp(),'counts':cnts,'visits_human':(visits[1] if visits else st.get('visits_human'))})
