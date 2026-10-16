import fs from 'node:fs/promises';
import { parse } from 'yaml';
import { generateVariants } from './variants.mjs';

const configFile = process.argv[2] || 'config/media-variants.yaml';
const manifest = await generateVariants(parse(await fs.readFile(configFile,'utf8')));
console.log(`Verified ${manifest.assets.length} original assets; wrote ${manifest.assets.reduce((sum,a)=>sum+a.variants.length,0)} smaller WebP variants. Originals unchanged.`);
