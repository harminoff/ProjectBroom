"""Original 5x7 uppercase ink geometry, CC-BY-SA-4.0; no external font."""
PATTERNS={
'A':'01110/10001/10001/11111/10001/10001/10001','B':'11110/10001/10001/11110/10001/10001/11110',
'C':'01111/10000/10000/10000/10000/10000/01111','D':'11110/10001/10001/10001/10001/10001/11110',
'E':'11111/10000/10000/11110/10000/10000/11111','F':'11111/10000/10000/11110/10000/10000/10000',
'G':'01111/10000/10000/10111/10001/10001/01111','H':'10001/10001/10001/11111/10001/10001/10001',
'I':'11111/00100/00100/00100/00100/00100/11111','J':'00111/00010/00010/00010/10010/10010/01100',
'K':'10001/10010/10100/11000/10100/10010/10001','L':'10000/10000/10000/10000/10000/10000/11111',
'M':'10001/11011/10101/10101/10001/10001/10001','N':'10001/11001/10101/10011/10001/10001/10001',
'O':'01110/10001/10001/10001/10001/10001/01110','P':'11110/10001/10001/11110/10000/10000/10000',
'Q':'01110/10001/10001/10001/10101/10010/01101','R':'11110/10001/10001/11110/10100/10010/10001',
'S':'01111/10000/10000/01110/00001/00001/11110','T':'11111/00100/00100/00100/00100/00100/00100',
'U':'10001/10001/10001/10001/10001/10001/01110','V':'10001/10001/10001/10001/10001/01010/00100',
'W':'10001/10001/10001/10101/10101/11011/10001','X':'10001/10001/01010/00100/01010/10001/10001',
'Y':'10001/10001/01010/00100/00100/00100/00100','Z':'11111/00001/00010/00100/01000/10000/11111'}

def generate(root):
    from tools.pickup_models.detailed import build_parts,obj_text
    from tools.pickup_models.generate import CATEGORIES
    from tools.weapon_models import viewmodel as geo
    from PIL import Image
    out=root/'mod/BrogueDoom'; models=out/'models/pickups'
    parts=build_parts(next(c for c in CATEGORIES if c.symbol=='SCROLL'),None)
    parts=[p for p in parts if 'ink stroke' not in p.name and p.name!='Wax seal']
    (models/'scroll_titled.obj').write_text(obj_text(parts))
    Image.new('RGB',(1,1),(44,30,19)).save(out/'graphics/BRGSCINK.png')
    zs=['''class BrogueScrollInk : BroguePickupProxyBase {
 override void Tick() {
  Super.Tick();
  if (master==null || master.bDestroyed) { Destroy(); return; }
  bInvisible=master.bInvisible;
  double x=-3.4+args[0]*0.7, y=2.4-args[1]*1.1;
  SetOrigin(master.Pos+(x*cos(master.Angle)-y*sin(master.Angle), x*sin(master.Angle)+y*cos(master.Angle),0.75),false);
  Angle=master.Angle;
 }
}''','class BrogueFlavorScroll : BroguePickupProxyBase {}']
    defs=['Model BrogueFlavorScroll { Path "models/pickups" Model 0 "scroll_titled.obj" Skin 0 "graphics/BRGPICKS.png" FrameIndex ITM0 A 0 0 }']
    for ch,pattern in PATTERNS.items():
        part=geo.Part('Assigned title ink','steel')
        for row,line in enumerate(pattern.split('/')):
            for col,pixel in enumerate(line):
                if pixel!='1': continue
                start=len(part.vertices); x=col*.1; y=-row*.1
                for pt in ((x,y,0),(x+.1,y,0),(x+.1,y-.1,0),(x,y-.1,0)): part.vertex(pt,0,0)
                part.faces.extend([(start,start+2,start+1),(start,start+3,start+2)])
        (models/f'letter_{ch}.obj').write_text(obj_text([part]))
        zs.append(f'class BrogueScrollInk{ch} : BrogueScrollInk {{}}')
        defs.append(f'Model BrogueScrollInk{ch} {{ Path "models/pickups" Model 0 "letter_{ch}.obj" Skin 0 "graphics/BRGSCINK.png" FrameIndex ITM0 A 0 0 }}')
    (out/'brogue_scroll_ink.zs').write_text('\n'.join(zs)+'\n')
    (models/'SCROLLINK.txt').write_text('\n'.join(defs)+'\n')

if __name__=='__main__':
    from pathlib import Path
    generate(Path(__file__).resolve().parents[2])
