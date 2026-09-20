"""EduCPU M3 browser datapath visualizer."""
from __future__ import annotations
import argparse,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from educpu import CPU
from eduasm import assemble_text,debug_map
from edudis import disassemble
from microcode import MicroStepper
HTML="""<!doctype html><html><head><meta charset="utf-8"><title>EduCPU Visualizer</title>
<style>body{font-family:system-ui;margin:20px;max-width:1200px}button{margin:3px;padding:8px}.box{border:2px solid #777;border-radius:8px;padding:12px}.active{outline:4px solid currentColor}.flow{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.regs{display:grid;grid-template-columns:repeat(4,1fr);gap:5px}pre{white-space:pre-wrap}</style></head><body>
<h1>EduCPU datapath teaching view</h1><p>Pedagogical visualization, not a frozen FPGA microarchitecture.</p>
<button onclick="act('micro')">Micro-step</button><button onclick="act('step')">Instruction step</button><button onclick="act('reset')">Reset</button>
<h3 id="src"></h3><pre id="ins"></pre><div class="flow"><div class="box" id="pc">PC</div>→<div class="box" id="memory">Memory</div>→<div class="box" id="decode">Decode / IR</div>→<div class="box" id="registers">Registers</div>↔<div class="box" id="alu">ALU</div>→<div class="box" id="flags">FLAGS</div></div>
<h3>Registers</h3><div class="regs" id="regvals"></div><h3>Control</h3><pre id="control"></pre><h3>Teaching phase</h3><pre id="phase"></pre>
<script>
const ids=['pc','memory','decode','registers','alu','flags'];
function activeFor(p){let m={FETCH_ADDR:['pc','memory'],FETCH_OPCODE:['memory','decode'],DECODE:['decode'],READ_OPERANDS:['decode','registers','memory'],ALU:['registers','alu'],MEM_READ:['memory','registers'],MEM_WRITE:['registers','memory'],CONTROL:['decode','pc'],STACK:['registers','memory'],EXECUTE:['decode','registers'],FLAGS:['alu','flags'],WRITEBACK:['alu','registers'],PC:['pc']};return m[p]||[]}
function hex(v,n){return v.toString(16).padStart(n,'0').toUpperCase()}
function draw(s){ids.forEach(x=>document.getElementById(x).classList.remove('active'));activeFor(s.phase).forEach(x=>document.getElementById(x).classList.add('active'));document.getElementById('phase').textContent=(s.phase||'READY')+'\n'+(s.text||'');document.getElementById('ins').textContent=hex(s.pc,4)+': '+s.instruction;document.getElementById('src').textContent=s.source?(s.source.file+':'+s.source.line+' — '+s.source.text):'';document.getElementById('regvals').innerHTML=s.registers.map((v,i)=>'<div>R'+i+' = '+hex(v,2)+'</div>').join('');document.getElementById('control').textContent='PC='+hex(s.pc,4)+' SP='+hex(s.sp,4)+' FLAGS='+hex(s.flags,2)+' HALT='+s.halted+' TRAP='+(s.trap||'-')}
async function act(a){draw(await (await fetch('/api/'+a,{method:'POST'})).json())}act('state');
</script></body></html>"""
class Visualizer:
 def __init__(self,data,debug=None):
  self.cpu=CPU();self.initial_memory=bytes(self.cpu.mem);self.cpu.mem[:len(data)]=data;self.initial=bytes(data);self.debug=debug or {};self.by_addr={x["address"]:x for x in self.debug.get("instructions",[])};self.micro=MicroStepper(self.cpu);self.phase=None
 def snapshot(self):
  pc=self.cpu.pc;rows=disassemble(bytes(self.cpu.mem[pc:pc+4]));ins=rows[0][2] if rows else "?";row=self.by_addr.get(pc);src=None if not row else {"file":self.debug.get("source") or "<source>","line":row["line"],"text":row["source"].strip()}
  return {"pc":pc,"sp":self.cpu.sp,"flags":self.cpu.flags,"registers":self.cpu.r.copy(),"halted":self.cpu.halted,"trap":self.cpu.trap,"instruction":ins,"phase":self.phase.phase if self.phase else None,"text":self.phase.text if self.phase else None,"source":src}
 def action(self,name):
  if name=="micro":
   self.phase,committed=self.micro.next()
   if committed:self.phase=None
  elif name=="step":self.micro.cancel();self.cpu.step();self.phase=None
  elif name=="reset":self.cpu.reset();self.cpu.mem[:]=self.initial_memory;self.cpu.mem[:len(self.initial)]=self.initial;self.micro.cancel();self.phase=None
  return self.snapshot()
def serve(v,host,port):
 class H(BaseHTTPRequestHandler):
  def do_GET(self):
   if self.path=="/":self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers();self.wfile.write(HTML.encode())
   else:self.send_error(404)
  def do_POST(self):
   name=self.path.removeprefix("/api/")
   if name=="state":data=v.snapshot()
   elif name in ("micro","step","reset"):data=v.action(name)
   else:self.send_error(404);return
   body=json.dumps(data).encode();self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 print("EduCPU visualizer: http://%s:%d"%(host,port));ThreadingHTTPServer((host,port),H).serve_forever()
def load_program(path,debug_path=None):
 p=Path(path)
 if p.suffix==".eduasm":
  data,_,rows=assemble_text(p.read_text());return data,debug_map(rows,str(p))
 dp=Path(debug_path) if debug_path else p.with_suffix(p.suffix+".dbg.json");dbg=json.loads(dp.read_text()) if dp.exists() else None;return p.read_bytes(),dbg
def main():
 p=argparse.ArgumentParser(prog="eduvis");p.add_argument("program",help="EduASM source or assembled binary");p.add_argument("-g","--debug-map");p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=8080);a=p.parse_args();data,dbg=load_program(a.program,a.debug_map);serve(Visualizer(data,dbg),a.host,a.port)
if __name__=="__main__":main()
