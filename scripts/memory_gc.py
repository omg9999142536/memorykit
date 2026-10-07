#!/usr/bin/env python3
"""记忆GC — 主记忆动态循环的「出口」端。
新记忆持续进来（写入端=我），本脚本定期把「冷了的」压出去（遗忘端）：

规则（保守，宁可漏压不误压）：
1. Red-line/constitution sections (keywords: red line, discipline, never violate) — never touch
2. 封闭项目段（含：已归档/已放下/已搁置/勿再提/告一段落）——压成一行指针，
   original text appended to the archive file's GC section
3. 带日期戳（MM-DD）且距今 >7 天的任务型条目——压缩为一行
4. 每段 >150 字且无日期戳的环境事实段——压成一行（细节应已外置，冗余即删）

安全：先写备份 ~/.hermes/memories/MEMORY.md.bak，再改；dry-run 模式只报告。
用法：python3 memory_gc.py [--dry]
"""
import re, sys, datetime, shutil, subprocess

import os
MEM = os.environ.get('MEMORY_KIT_MEM', os.path.expanduser('~/.hermes/memories/MEMORY.md'))
ARCHIVE = os.environ.get('MEMORY_KIT_ARCHIVE', os.path.expanduser('~/.memory-kit/archive.md'))
BAK = MEM + '.bak'

PROTECTED = ['红线', '明令', '纪律', '宪法', '检验四问', '对账纪律', '记忆宪法']
CLOSED = ['已归档', '已放下', '已搁置', '勿再提', '告一段落', '已收口']


def seg_date(seg):
    """找段里最新的 MM-DD 日期戳"""
    ds = re.findall(r'(1[0-2])-([0-3]\d)', seg)
    if not ds:
        return None
    today = datetime.date.today()
    best = None
    for m, d in ds:
        try:
            dt = datetime.date(today.year, int(m), int(d))
            if dt > today:  # 未来日期=去年
                dt = datetime.date(today.year - 1, int(m), int(d))
            if best is None or dt > best:
                best = dt
        except ValueError:
            pass
    return best


def one_line(seg):
    """压成一行：保留第一句 + 指针"""
    first = re.split(r'[。；;]', seg)[0].strip()
    return first[:80] + '（GC压缩，详=MEMORY-INDEX/轴文件）'


def main():
    dry = '--dry' in sys.argv
    txt = open(MEM).read()
    segs = [s.strip() for s in txt.split('§') if s.strip()]
    today = datetime.date.today()
    out, archived = [], []

    for seg in segs:
        if len(seg) <= 100:  # 已经很短，不动
            out.append(seg)
            continue
        if any(k in seg for k in PROTECTED):
            out.append(seg)
            continue
        reason = None
        if any(k in seg for k in CLOSED):
            reason = '封闭项目'
        else:
            dt = seg_date(seg)
            if dt and (today - dt).days > 7:
                reason = f'任务条目{(today-dt).days}天未动'
            elif len(seg) > 150 and not dt:
                reason = '无日期长段(环境事实)'
        if reason:
            archived.append((reason, seg))
            out.append(one_line(seg))
        else:
            out.append(seg)

    new = '§\n'.join(out)
    saved = len(txt) - len(new)
    print(f'原 {len(txt)} 字 → 新 {len(new)} 字（省 {saved}）')
    for r, s in archived:
        print(f'  [{r}] {s[:50]}...')

    if dry or not archived:
        print('dry-run 或无变化，未写盘')
        return

    shutil.copy(MEM, BAK)
    open(MEM, 'w').write(new)
    # 归档原文进 jn 轴
    with open(ARCHIVE, 'a') as f:
        f.write(f"\n## GC归档 {datetime.date.today()}（原文备份，主记忆已压成指针）\n")
        for r, s in archived:
            f.write(f"- [{r}] {s}\n")
    print(f'已写盘，备份={BAK}，原文归档={ARCHIVE}')


if __name__ == '__main__':
    main()
