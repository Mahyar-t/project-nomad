#!/usr/bin/python3
"""Launch this machine's NOMAD setup; AI requires an explicit interactive choice."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,urllib.request,urllib.error,fcntl
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/'admin'; SETUP=ADMIN/'storage/offline-setup'
URL='http://localhost:8081'
def run(*args,check=True):
 return subprocess.run(args,cwd=ROOT,check=check)
def request(url,data=None,timeout=15):
 req=urllib.request.Request(url,None if data is None else json.dumps(data).encode(),{'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def wait(url):
 for _ in range(90):
  try:return request(url)
  except (OSError,urllib.error.URLError):time.sleep(1)
 raise RuntimeError('The service did not start: '+url)
def ollama_active():
 return run('/usr/bin/systemctl','is-active','--quiet','ollama',check=False).returncode==0
def system_ollama(action):
 print('Administrator authentication may be requested to '+action+' Ollama.',flush=True)
 run('/usr/bin/pkexec','/usr/bin/systemctl',action,'ollama')
def main():
 p=argparse.ArgumentParser();p.add_argument('--ai',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.ai:
  if a.check:
   print('AI launcher configuration checked. No AI was started.');return
  print('This launcher starts a local AI model and can increase heat and power use.')
  if input('Start local AI now? Type YES to consent: ').strip()!='YES':
   print('Cancelled. Local AI was not started.');return
 lock=open('/tmp/nomad-launch-'+str(os.getuid())+'.lock','w')
 fcntl.flock(lock,fcntl.LOCK_EX)
 print('Starting NOMAD databases...',flush=True)
 run('/usr/bin/docker','compose','-f',str(ROOT/'compose.yaml'),'up','-d','--wait')
 SETUP.mkdir(parents=True,exist_ok=True)
 (SETUP/'ai-paused').write_text('Automatic AI indexing is disabled. Local AI requires explicit consent.\n')
 run('/usr/bin/node','--env-file='+str(ADMIN/'.env'),str(ROOT/'launchers/configure-ai.mjs'),'on' if a.ai else 'off')
 if a.ai:
  run('/usr/bin/docker','start','nomad_qdrant')
  if not ollama_active():system_ollama('start')
  wait('http://127.0.0.1:11434/api/version')
  models=request('http://127.0.0.1:11434/api/tags')['models']
  if not any(m['name']=='gemma3:4b' for m in models):raise RuntimeError('gemma3:4b is not downloaded. No model was initialized.')
  print('Loading gemma3:4b (automatic document indexing stays paused)...',flush=True)
  request('http://127.0.0.1:11434/api/generate',{'model':'gemma3:4b','keep_alive':'10m','options':{'num_ctx':8192}},timeout=180)
 else:
  if ollama_active():
   for m in request('http://127.0.0.1:11434/api/ps').get('models',[]):
    request('http://127.0.0.1:11434/api/generate',{'model':m['name'],'keep_alive':0},timeout=60)
   system_ollama('stop')
  # Stop NOMAD's optional AI containers without changing other applications.
  for name in ['nomad_ollama','nomad_qdrant']:
   result=subprocess.run(['/usr/bin/docker','container','inspect',name],capture_output=True)
   if result.returncode==0:
    run('/usr/bin/docker','update','--restart=no',name)
    run('/usr/bin/docker','stop',name)
 print('Starting the web app...',flush=True)
 run('/usr/bin/systemctl','--user','start','project-nomad-server','project-nomad-workers')
 wait(URL+'/api/health')
 if not a.ai and ollama_active():raise RuntimeError('Ollama is still running; no-AI startup did not complete.')
 if a.check:print('No-AI startup passed. Browser opening skipped.');return
 print('Opening '+URL+' in Chrome.',flush=True)
 subprocess.Popen(['/usr/bin/google-chrome','--new-window',URL],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
if __name__=='__main__':
 try:main()
 except (Exception,KeyboardInterrupt) as error:
  print('\nNOMAD launch failed: '+str(error),file=sys.stderr)
  if sys.stdin.isatty():input('Press Enter to close...')
  sys.exit(1)
