import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import sharp from 'sharp';

const hash = body => createHash('sha256').update(body).digest('hex');
const integer = (v, min, max) => Number.isSafeInteger(v) && v >= min && v <= max;
function relativeKey(value) {
  if (typeof value !== 'string' || !value || value.includes('\\') || value.startsWith('/') || value.split('/').some(p => !p || p === '.' || p === '..') || /[\s,\x00-\x1f?#]/.test(value)) throw new Error('Unsafe relative media path');
  return value;
}
export function validateConfig(config) {
  if (!config || typeof config !== 'object') throw new Error('Media configuration required');
  const allowed = ['sourceRoot','outputDirectory','manifestName','directories','widths','includeNativeWidth','quality','effort','maxInputPixels'];
  if (Object.keys(config).some(key => !allowed.includes(key))) throw new Error('Unknown media configuration field');
  if (typeof config.sourceRoot !== 'string' || !config.sourceRoot) throw new Error('Image source root required');
  relativeKey(config.outputDirectory); relativeKey(config.manifestName);
  if (!Array.isArray(config.directories) || !config.directories.length) throw new Error('Source directories required');
  config.directories.forEach(relativeKey);
  if (config.directories.some(d => d === config.outputDirectory || d.startsWith(config.outputDirectory + '/') || config.outputDirectory.startsWith(d + '/'))) throw new Error('Output cannot be a source');
  if (!Array.isArray(config.widths) || !config.widths.length || config.widths.length > 10 || !config.widths.every(w => integer(w, 1, 8192)) || new Set(config.widths).size !== config.widths.length) throw new Error('Unique positive bounded widths required');
  if (!integer(config.quality,1,100) || !integer(config.effort,0,6) || !integer(config.maxInputPixels,1,100000000) || typeof config.includeNativeWidth !== 'boolean') throw new Error('Invalid encoder limits');
  return config;
}
async function contained(root, key) {
  const target = path.resolve(root, relativeKey(key));
  if (!target.startsWith(root + path.sep)) throw new Error('Media path escaped root');
  // Reject existing symlink ancestors, including for output paths.
  let current = root;
  for (const part of key.split('/')) {
    current = path.join(current, part);
    try { if ((await fs.lstat(current)).isSymbolicLink()) throw new Error('Media symlinks forbidden'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  return target;
}
async function sources(root, directory) {
  const start = await contained(root,directory);
  let result = [];
  for (const item of (await fs.readdir(start,{withFileTypes:true})).sort((a,b)=>a.name.localeCompare(b.name))) {
    const key = `${directory}/${item.name}`;
    if (item.isSymbolicLink()) throw new Error('Media symlinks forbidden');
    if (item.isDirectory()) result.push(...await sources(root,key));
    else if (item.isFile() && /\.(png|jpe?g|webp)$/i.test(item.name)) result.push(key);
  }
  return result;
}
export async function generateVariants(configuration) {
  const config = validateConfig(configuration);
  const root = await fs.realpath(path.resolve(config.sourceRoot));
  const keys = [...new Set((await Promise.all(config.directories.map(d=>sources(root,d)))).flat())].sort();
  if (!keys.length) throw new Error('No approved image sources');
  const encoder = { format:'webp', quality:config.quality, effort:config.effort, sharp:sharp.versions.sharp };
  const manifest = { version:1, encoder, assets:[] };
  for (const key of keys) {
    const filename = await contained(root,key);
    const input = await fs.readFile(filename);
    const metadata = await sharp(input,{limitInputPixels:config.maxInputPixels}).metadata();
    if (!metadata.width || !metadata.height || (metadata.pages ?? 1) > 1 || (metadata.orientation ?? 1) !== 1) throw new Error(`Unsupported animated/oriented asset: ${key}`);
    const sourceHash = hash(input);
    const identity = hash(JSON.stringify({sourceHash,...encoder})).slice(0,16);
    const widths = [...new Set([...config.widths.filter(w=>w<=metadata.width), ...(config.includeNativeWidth ? [metadata.width] : [])])].sort((a,b)=>a-b);
    if (!widths.length) throw new Error(`Source is smaller than configured widths: ${key}`);
    const asset = { key, sha256:sourceHash, bytes:input.length, width:metadata.width, height:metadata.height, variants:[] };
    for (const width of widths) {
      const variantKey = `${config.outputDirectory}/${key.replace(/\.[^.]+$/, '')}-${identity}-${width}w.webp`;
      const target = await contained(root,variantKey);
      const {data,info} = await sharp(input,{limitInputPixels:config.maxInputPixels}).resize({width,withoutEnlargement:true}).webp({quality:config.quality,effort:config.effort}).toBuffer({resolveWithObject:true});
      if (data.length >= input.length) continue; // A derivative must actually reduce transfer.
      await fs.mkdir(path.dirname(target),{recursive:true});
      await fs.writeFile(target,data);
      asset.variants.push({key:variantKey,width:info.width,height:info.height,contentType:'image/webp',descriptor:`${info.width}w`,bytes:data.length,sha256:hash(data)});
    }
    if (hash(await fs.readFile(filename)) !== sourceHash) throw new Error('Original changed during generation');
    manifest.assets.push(asset);
  }
  const output = await contained(root,`${config.outputDirectory}/${config.manifestName}`);
  await fs.mkdir(path.dirname(output),{recursive:true});
  await fs.writeFile(output,JSON.stringify(manifest,null,2)+'\n');
  return manifest;
}
