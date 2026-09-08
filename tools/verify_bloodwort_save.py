"""Real seed-one bloodwort route and native recording restoration, no fixtures."""
from collections import deque
import ctypes as C
import json
from pathlib import Path
from tools.test_brogue_saves import NativeSaveTests

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'artifacts/bloodwort/save'
    out.mkdir(parents=True,exist_ok=True)
    NativeSaveTests.setUpClass()
    h=NativeSaveTests()
    h.setUp()
    try:
        h.new(1)
        result=C.create_string_buffer(1024*1024)
        # N, 27 E, pod bump N, entry N, WAIT. Every command is native gameplay.
        for action in [0]+[2]*27+[0,0,8]:
            h.assertEqual(h.dll.brogue_bridge_perform_action(action,result),0)
        h.call(7)
        h.assertEqual(h.state.turns,31)
        h.call(8,out/'before.json')
        h.call(2,out/'bloodwort-turn31.broguesave')
        h.dll.brogue_bridge_shutdown(); h.call(7)
        h.call(0,h.root/'resume.broguesave')
        h.call(3,out/'bloodwort-turn31.broguesave')
        while h.state.phase==2: h.call(4)
        h.assertEqual(h.state.turns,31)
        h.call(5)
        h.call(8,out/'restored.json')
        before=json.loads((out/'before.json').read_text())
        restored=json.loads((out/'restored.json').read_text())
        # Memory bookkeeping can settle during replay; compare native terrain,
        # gas identities and volumes rather than claiming raw hash identity.
        def terrain(snapshot):
            return [(c['x'],c['y'],c['layers'],c['volume']) for c in snapshot['levels'][0]['cells']]
        h.assertEqual(terrain(before),terrain(restored))
        h.wait(); h.call(8,out/'continued.json')
        h.assertEqual(h.state.turns,32)
        print('BLOODWORT real-route=31 native-save-load=OK all-cell-layers-volume=identical continued=32')
        def travel(stairs, target_depth):
            for step in range(250):
                h.call(8,out/'travel.json')
                level=json.loads((out/'travel.json').read_text())['levels'][0]
                if level['depth']==target_depth: return
                cells={(c['x'],c['y']):c for c in level['cells']}
                start=next(p for p,c in cells.items() if c['flags']&4)
                goal=(level[stairs]['x'],level[stairs]['y'])
                queue=deque([goal]); distances={goal:0}
                directions=[(0,-1,0),(1,0,2),(0,1,4),(-1,0,6)]
                while queue:
                    x,y=queue.popleft()
                    for dx,dy,_ in directions:
                        p=(x+dx,y+dy); c=cells.get(p)
                        if not c or p in distances: continue
                        flags=c['terrainFlags']
                        if flags&((1<<7)|(1<<8)|(1<<13)): continue
                        if flags&1 and c['layers']['dungeon']['symbol']!='DOOR': continue
                        distances[p]=distances[(x,y)]+1; queue.append(p)
                options=[(distances.get((start[0]+dx,start[1]+dy),99999),action) for dx,dy,action in directions]
                distance,action=min(options)
                h.assertLess(distance,99999,'No safe stair route')
                h.assertEqual(h.dll.brogue_bridge_perform_action(action,result),0)
                h.call(7)
            raise AssertionError('Depth travel did not finish')
        travel('downStairs',2)
        print(f'BLOODWORT depth=2 turn={h.state.turns}')
        h.call(8,out/'depth2.json')
        h.call(2,out/'bloodwort-depth2.broguesave')
        h.dll.brogue_bridge_shutdown(); h.call(7)
        h.call(0,h.root/'return.broguesave'); h.call(3,out/'bloodwort-depth2.broguesave')
        while h.state.phase==2: h.call(4)
        h.call(5)
        travel('upStairs',1)
        h.call(8,out/'revisited.json')
        h.call(2,out/'bloodwort-depth-return.broguesave')
        revisited=json.loads((out/'revisited.json').read_text())['levels'][0]
        stalk=next(c for c in revisited['cells'] if (c['x'],c['y'])==(64,24))
        h.assertEqual(stalk['layers']['surface']['symbol'],'BLOODFLOWER_STALK')
        print(f'BLOODWORT depth-return=1 turn={h.state.turns} stalk=preserved')
    finally:
        h.tearDown()


if __name__=='__main__': main()
