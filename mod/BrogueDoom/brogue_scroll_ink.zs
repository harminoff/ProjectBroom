class BrogueScrollInk : BroguePickupProxyBase {
 override void Tick() {
  Super.Tick();
  if (master==null || master.bDestroyed) { Destroy(); return; }
  bInvisible=master.bInvisible;
  double x=-3.4+args[0]*0.7, y=2.4-args[1]*1.1;
  SetOrigin(master.Pos+(x*cos(master.Angle)-y*sin(master.Angle), x*sin(master.Angle)+y*cos(master.Angle),0.75),false);
  Angle=master.Angle;
 }
}
class BrogueFlavorScroll : BroguePickupProxyBase {}
class BrogueScrollInkA : BrogueScrollInk {}
class BrogueScrollInkB : BrogueScrollInk {}
class BrogueScrollInkC : BrogueScrollInk {}
class BrogueScrollInkD : BrogueScrollInk {}
class BrogueScrollInkE : BrogueScrollInk {}
class BrogueScrollInkF : BrogueScrollInk {}
class BrogueScrollInkG : BrogueScrollInk {}
class BrogueScrollInkH : BrogueScrollInk {}
class BrogueScrollInkI : BrogueScrollInk {}
class BrogueScrollInkJ : BrogueScrollInk {}
class BrogueScrollInkK : BrogueScrollInk {}
class BrogueScrollInkL : BrogueScrollInk {}
class BrogueScrollInkM : BrogueScrollInk {}
class BrogueScrollInkN : BrogueScrollInk {}
class BrogueScrollInkO : BrogueScrollInk {}
class BrogueScrollInkP : BrogueScrollInk {}
class BrogueScrollInkQ : BrogueScrollInk {}
class BrogueScrollInkR : BrogueScrollInk {}
class BrogueScrollInkS : BrogueScrollInk {}
class BrogueScrollInkT : BrogueScrollInk {}
class BrogueScrollInkU : BrogueScrollInk {}
class BrogueScrollInkV : BrogueScrollInk {}
class BrogueScrollInkW : BrogueScrollInk {}
class BrogueScrollInkX : BrogueScrollInk {}
class BrogueScrollInkY : BrogueScrollInk {}
class BrogueScrollInkZ : BrogueScrollInk {}
