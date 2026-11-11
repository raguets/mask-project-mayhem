"""Read-only audit client for the installed Blender MCP add-on socket API."""
import argparse
import json
import socket
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('command')
p.add_argument('--code-file')
p.add_argument('--params-file')
p.add_argument('--output')
p.add_argument('--quiet', action='store_true')
p.add_argument('--timeout', type=float, default=45, help='Response timeout for long live Blender operations')
a = p.parse_args()
params = json.loads(Path(a.params_file).read_text(encoding='utf-8-sig')) if a.params_file else {}
if a.code_file:
    params['code'] = Path(a.code_file).read_text(encoding='utf-8-sig')
with socket.create_connection(('localhost', 9876), timeout=5) as s:
    s.settimeout(a.timeout)
    s.sendall(json.dumps({'type': a.command, 'params': params}).encode())
    data = bytearray()
    while True:
        chunk = s.recv(65536)
        if not chunk:
            raise RuntimeError('Connection closed before a complete response')
        data.extend(chunk)
        try:
            result = json.loads(data)
            break
        except json.JSONDecodeError:
            pass
out = json.dumps(result, ensure_ascii=True, indent=2)
if a.output:
    Path(a.output).write_text(out, encoding='utf-8')
if a.quiet:
    print(json.dumps({'status':result.get('status'), 'output':a.output, 'message':result.get('message')},ensure_ascii=True))
else:
    print(out)
if result.get('status') == 'error':
    raise SystemExit(1)
