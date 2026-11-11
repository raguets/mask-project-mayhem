"""Transport to an already installed local Blender MCP add-on, not a renderer."""
import argparse,json,socket,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command');p.add_argument('--port',type=int,default=9876);p.add_argument('--host',choices=['127.0.0.1','localhost','::1'],default='127.0.0.1');p.add_argument('--timeout',type=float,default=45);p.add_argument('--code-file');p.add_argument('--params-file');p.add_argument('--output');p.add_argument('--quiet',action='store_true');a=p.parse_args()
    if not 1<=a.port<=65535:p.error('port must be between 1 and 65535')
    params=json.loads(Path(a.params_file).read_text(encoding='utf-8-sig')) if a.params_file else {}
    if a.code_file:params['code']=Path(a.code_file).read_text(encoding='utf-8-sig')
    sent=False
    try:
        with socket.create_connection((a.host,a.port),timeout=5) as connection:
            connection.settimeout(a.timeout);connection.sendall(json.dumps({'type':a.command,'params':params}).encode());sent=True;data=bytearray()
            while True:
                chunk=connection.recv(65536)
                if not chunk:raise ConnectionError('Connection closed before complete response')
                data.extend(chunk)
                try:result=json.loads(data);break
                except json.JSONDecodeError:continue
    except (OSError,ConnectionError) as exc:
        print(json.dumps({'status':'unknown_may_still_be_running' if sent else 'not_connected','error':str(exc),'instruction':'Inspect scene/job markers before resubmitting an already sent command.' if sent else 'Verify the installed add-on connection and port.'}));return 2 if sent else 3
    if a.output:
        path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'status':result.get('status'),'output':a.output,'message':result.get('message')},ensure_ascii=False) if a.quiet else json.dumps(result,indent=2,ensure_ascii=False))
    return 1 if result.get('status')=='error' else 0

if __name__=='__main__':sys.exit(main())
