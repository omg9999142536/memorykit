#!/usr/bin/env python3
"""
sj-时钟 v2：哈希链 + 因果序 的时间锚点系统
- 哈希链：H_n = sha256(H_{n-1} + 内容_n + 时间_n) —— 篡改/倒流可检测（方向律密码学化）
- 因果序：条目带 seq 单调递增（Lamport 式 happens-before，不依赖绝对时间）
- 出环校验：锚点分「内证」（链哈希）与「外证」（date+NTP），每次运行同时记录
- 文件：research/axes/sj-时钟链.jsonl（append-only，JSON Lines）
"""
import json, hashlib, os, subprocess, sys, datetime

CHAIN = os.environ.get('MEMORY_KIT_CHAIN', os.path.expanduser('~/.memory-kit/clock-chain.jsonl'))
GENESIS = '0' * 64

def now_local():
    return subprocess.run(['date', '+%Y-%m-%d %H:%M:%S %Z (%A)'],
                          capture_output=True, text=True).stdout.strip()

def ntp_offset():
    """外证：与 NTP 源比对，返回偏移秒；失败返回 None"""
    import socket, struct, time
    for host in ['ntp.aliyun.com', 'cn.pool.ntp.org']:
        try:
            c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            c.settimeout(4)
            c.sendto(b'\x1b' + 47 * b'\0', (host, 123))
            t0 = time.time()
            d, _ = c.recvfrom(1024)
            t3 = time.time()
            srv = struct.unpack('!12I', d)[10] - 2208988800
            return round((t0 + t3) / 2 - srv, 3)
        except Exception:
            continue
    return None

def last_entry():
    if not os.path.exists(CHAIN):
        return None
    with open(CHAIN, encoding='utf-8') as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    return json.loads(lines[-1]) if lines else None

def verify_chain():
    """全链校验：哈希连续性 + seq 单调性"""
    if not os.path.exists(CHAIN):
        return True, 0, '空链（尚未建立）'
    with open(CHAIN, encoding='utf-8') as f:
        entries = [json.loads(l) for l in f.read().splitlines() if l.strip()]
    prev_h, prev_seq = GENESIS, 0
    for i, e in enumerate(entries):
        calc = hashlib.sha256((prev_h + e['content'] + e['time'] + str(e['seq'])).encode()).hexdigest()
        if calc != e['hash']:
            return False, i, f'第 {i} 条哈希断裂（内容或顺序被篡改）'
        if e['seq'] <= prev_seq:
            return False, i, f'第 {i} 条因果序倒退'
        prev_h, prev_seq = e['hash'], e['seq']
    return True, len(entries), f'{len(entries)} 条全部连续，因果序单调'

def append(kind, content):
    last = last_entry()
    prev_h = last['hash'] if last else GENESIS
    seq = (last['seq'] + 1) if last else 1
    t = now_local()
    h = hashlib.sha256((prev_h + content + t + str(seq)).encode()).hexdigest()
    entry = {'seq': seq, 'kind': kind, 'content': content, 'time': t, 'hash': h}
    with open(CHAIN, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return entry

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'tick':                       # cron 心跳：外证+追加
        off = ntp_offset()
        e = append('heartbeat', f'NTP偏移={off}s' if off is not None else 'NTP不可达(离线)')
        print(f"tick #{e['seq']} @ {e['time']}  hash={e['hash'][:16]}…  NTP偏移={off}s")
    elif cmd == 'note':                     # 事件锚点：note "内容"
        e = append('event', ' '.join(sys.argv[2:]) or '未命名事件')
        print(f"note #{e['seq']} @ {e['time']}  hash={e['hash'][:16]}…")
    elif cmd == 'verify':                   # 全链校验（防篡改/倒流）
        ok, n, msg = verify_chain()
        print(f"链校验: {'✓ 通过' if ok else '✗ ' + msg}")
        off = ntp_offset()
        print(f"外证: NTP偏移 = {off}s" if off is not None else "外证: NTP不可达（本次仅内证）")
    elif cmd == 'status':                   # 当前状态
        ok, n, msg = verify_chain()
        last = last_entry()
        print(f"sj-时钟链 v2")
        print(f"  完整性: {'✓ ' + msg if ok else '✗ ' + msg}")
        print(f"  最新锚点: #{last['seq']} {last['kind']} @ {last['time']}" if last else "  （空链）")
        off = ntp_offset()
        print(f"  外证 NTP偏移: {off}s" if off is not None else "  外证: 离线")
    elif cmd == 'when':                     # 因果查询: 某事件之前/之后
        kw = ' '.join(sys.argv[2:])
        with open(CHAIN, encoding='utf-8') as f:
            hits = [json.loads(l) for l in f if kw in l]
        for h in hits:
            print(f"  #{h['seq']} [{h['kind']}] {h['content']} @ {h['time']}")
        if not hits:
            print(f"  未找到含「{kw}」的锚点")
