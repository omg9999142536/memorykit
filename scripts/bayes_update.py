#!/usr/bin/env python3
# Bayesian prior update: each user decision is one observation
import json, sys, datetime
import os
D=os.environ.get('MEMORY_KIT_GATE', os.path.expanduser('~/.memory-kit/priors'))
priors=json.load(open(D+'/priors.json'))
cat, verdict = sys.argv[1], sys.argv[2]
p=priors[cat]
if verdict=='同意': p['alpha']+=1
elif verdict=='拒绝': p['beta']+=1
else: p['alpha']+=0.5; p['beta']+=0.5
p['updated']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
p['mean']=round(p['alpha']/(p['alpha']+p['beta']),3)
json.dump(priors, open(D+'/priors.json','w'), ensure_ascii=False, indent=1)
print(f"{cat}: 先验均值={p['mean']} (alpha={p['alpha']:.1f},beta={p['beta']:.1f}) - {p['note']}")
