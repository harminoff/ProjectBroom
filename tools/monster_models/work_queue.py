"""Durable coordinator ledger for the user-requested sequential model rollout.

This is project work tracking, never a runtime or spawn-order input.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / 'docs/creature-creation-queue.json'
DOC = ROOT / 'docs/creature-creation-queue.md'


def initialize():
    if QUEUE.exists():
        raise FileExistsError('Preserve the existing rollout queue')
    catalog = json.loads((ROOT/'assets/monsters/bestiary-index.json').read_text())
    excluded = ('HORDE_MACHINE_', 'HORDE_LEADER_CAPTIVE', 'HORDE_IS_SUMMONED',
                'HORDE_VAMPIRE_FODDER', 'HORDE_ALLIED_WITH_PLAYER', 'HORDE_SACRIFICE_TARGET')
    rows=[]
    for creature in catalog['creatures']:
        if creature['art']['status']!='authored-static':
            continue
        ordinary=[h for h in creature['hordeReferences']
                  if h['minLevelExpression'].isdigit() and int(h['minLevelExpression'])>0
                  and not any(flag in h['flags'] for flag in excluded)]
        rank=min([(int(h['minLevelExpression']),h['line']) for h in ordinary]
                 or [(999,creature['kind'])])
        rows.append(dict(symbol=creature['symbol'],kind=creature['kind'],name=creature['name'],
                         workId=creature['indexId'],nominalDepth=rank[0] if rank[0]!=999 else None,
                         sourceOrder=rank[1],status='pending',agent=None,report=None,
                         evidence=None,remainingAcceptance=[]))
    rows.sort(key=lambda r:(r['nominalDepth'] or 999,r['sourceOrder'],r['kind']))
    assert len(rows)==57, 'Review roster changes before initializing the requested 57-model queue'
    save(dict(schemaVersion=1,requestDate='2026-09-26',mode='one fresh agent per model, sequential',
              coordinator='current Codex task',items=rows))


def save(queue):
    QUEUE.write_text(json.dumps(queue,indent=2)+'\n',encoding='utf-8')
    rows=queue['items']
    counts={status:sum(r['status']==status for r in rows)
            for status in ('pending','active','review','verified','blocked')}
    lines=['# Remaining creature creation queue','',
           'User requested all 57 remaining static models be upgraded by fresh agents, one at a time. '
           'The coordinator reviews each result before dispatching the next. This file survives context resets.', '',
           '**Progress:** '+', '.join(f'{n} {status}' for status,n in counts.items() if n)+'.','',
           *([queue['agentAllocationNote'], ''] if queue.get('agentAllocationNote') else []),
           'Checked items mean the technical model pass is verified: authored source, runtime integration, '
           'deterministic export, relevant passing tests and inspected engine captures. They do not mean '
           'user art approval or exhaustive gameplay acceptance. Residual gates stay in the item report.', '',
           'Order uses nominal ordinary horde minimum depth and source-row order, followed by special, '
           'summoned and allied forms. It is a production priority, not a claim of guaranteed encounter order.', '',
           '## Create in sequence','']
    for i,r in enumerate(rows,1):
        check='x' if r['status']=='verified' else ' '
        depth=f"nominal depth {r['nominalDepth']}" if r['nominalDepth'] else 'special / associated form'
        slug=r['symbol'][3:].lower()
        report=f"; [report]({Path(r['report']).name})" if r.get('report') else ''
        lines.append(f"- [{check}] {i:02d}. **{r['name']}** — [{r['workId']}](creatures/{r['kind']:02d}_{slug}.md); {depth}; **{r['status']}**{report}")
        if r.get('remainingAcceptance'):
            lines.append('  - Remaining acceptance: '+'; '.join(r['remainingAcceptance'])+'.')
    lines += ['', '## Fresh-agent handoff contract','',
              'Read [creature-agent-handoff.md](creature-agent-handoff.md) before starting. '
              'The JSON ledger is coordinator-owned; agents write their own report and return a compact handoff. '
              'Do not start the next creature, publish, commit, delete baseline files or change gameplay.', '',
              'Already upgraded before this queue: rat, kobold, jackal, eel, monkey, bloat, pit bloat, '
              'goblin, goblin conjurer and toad. Their previous acceptance limitations remain unchanged.','']
    DOC.write_text('\n'.join(lines),encoding='utf-8')


def update(symbol,status,**fields):
    if status not in ('pending','active','review','verified','blocked'):
        raise ValueError(status)
    queue=json.loads(QUEUE.read_text(encoding='utf-8'))
    item=next(r for r in queue['items'] if r['symbol']==symbol)
    item.update(status=status,**fields)
    save(queue)


if __name__=='__main__': initialize()
