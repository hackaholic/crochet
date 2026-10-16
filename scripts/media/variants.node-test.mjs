import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import sharp from 'sharp';
import { generateVariants, validateConfig } from './variants.mjs';
const config = root => ({sourceRoot:root,outputDirectory:'optimized',manifestName:'manifest.json',directories:['hero'],widths:[48,96],includeNativeWidth:true,quality:84,effort:6,maxInputPixels:1000000});
test('preserves originals, aspect and verified content-addressed derivatives',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'sulocraft-media-'));
  try {
    await fs.mkdir(path.join(root,'hero'));
    const body=await sharp({create:{width:192,height:108,channels:3,background:'#a24528'}}).png({compressionLevel:0}).toBuffer();
    await fs.writeFile(path.join(root,'hero','sample.png'),body);
    const result=await generateVariants(config(root));
    assert.equal(result.assets.length,1); assert.equal(result.assets[0].variants.length,3);
    for(const variant of result.assets[0].variants){
      const actual=await sharp(await fs.readFile(path.join(root,variant.key))).metadata();
      assert.equal(actual.format,'webp'); assert.equal(actual.width,variant.width);
      assert.equal(actual.height,variant.height); assert.equal(variant.width/variant.height,192/108);
      assert.ok(variant.bytes<body.length); assert.match(variant.key,/[a-f0-9]{16}-\d+w\.webp$/);
    }
    assert.deepEqual(await fs.readFile(path.join(root,'hero','sample.png')),body);
    assert.deepEqual(await generateVariants(config(root)),result);
  }finally{await fs.rm(root,{recursive:true,force:true});}
});
test('rejects traversal, unsafe limits and symlink input before output',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'sulocraft-media-'));
  try {
    for(const patch of [{outputDirectory:'../escape'},{outputDirectory:'hero/optimized'},{directories:['../elsewhere']},{widths:[0]},{widths:[48,48]},{quality:101},{includeNativeWidth:'yes'}]) assert.throws(()=>validateConfig({...config(root),...patch}));
    await assert.rejects(generateVariants(config(root)),/ENOENT/);
    await fs.mkdir(path.join(root,'hero')); await fs.symlink('/etc/passwd',path.join(root,'hero','fake.png'));
    await assert.rejects(generateVariants(config(root)),/symlinks forbidden/);
    await assert.rejects(fs.stat(path.join(root,'optimized')),/ENOENT/);
  }finally{await fs.rm(root,{recursive:true,force:true});}
});
