"""Abstract byte-programming controller. No electrical timing or actual SDP emulation."""
class Programmer:
 def __init__(self,rom):self.rom=rom;self.pending=None;self.trace=[]
 def request(self,address,value,*,power,run,executing_ram):
  if self.pending is not None or not (power and run and executing_ram) or not 0x7800<=address<0x8000 or not 0<=value<=255:return False
  self.pending=(address,value);self.trace.extend([(0x5555,0xaa),(0x2aaa,0x55),(0x5555,0xa0),(address,value)]);return True
 def complete(self,*,power,run):
  if self.pending is None:return False
  a,v=self.pending;self.pending=None
  if not(power and run):return False
  self.rom[a]=v;return True
 def reset(self):self.pending=None
