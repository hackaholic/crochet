import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Serve an isolated build with read-only local instrumentation; never deployed.
const root = path.resolve(process.argv[2] || 'dist');
const port = Number(process.argv[3] || 4182);
if (!Number.isInteger(port) || port < 1024 || port > 65535 || !fs.existsSync(path.join(root, 'index.html'))) throw new Error('Expected built directory and valid port');
const probe = fs.readFileSync(fileURLToPath(new URL('./lab-probe.js', import.meta.url)));
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json', '.woff2': 'font/woff2' };
http.createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405).end(); return; }
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); } catch { res.writeHead(400).end(); return; }
  res.setHeader('Cache-Control', 'no-store');
  if (pathname === '/__lab-probe.js') { res.setHeader('Content-Type', 'text/javascript'); res.end(req.method === 'HEAD' ? undefined : probe); return; }
  let file = path.resolve(root, `.${pathname}`);
  if (!file.startsWith(root + path.sep) && file !== root) { res.writeHead(403).end(); return; }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404).end(); return; }
  res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  let content = fs.readFileSync(file);
  if (path.extname(file) === '.html') content = content.toString().replace('<head>', '<head><script src="/__lab-probe.js"></script>');
  res.end(req.method === 'HEAD' ? undefined : content);
}).listen(port, '127.0.0.1', () => console.log(`Local mobile lab on http://127.0.0.1:${port}; artifact ${root}`));
