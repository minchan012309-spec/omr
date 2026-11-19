/* Reproducible patch for the pinned SwiftLaTeX v20022022 binary, no WASM edits. */
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const root=path.join(__dirname,'../lib/latex/engine'),wasm=fs.readFileSync(path.join(root,'swiftlatexdvipdfm.wasm'));
if(crypto.createHash('sha256').update(wasm).digest('hex')!=='1bf8c0d424c87c1548d9d22d29251aa3308506fa6acc29d4f08dcd77ccc1f9b1')throw Error('Review the WASM call signature before patching a different engine');
const file=path.join(root,'swiftlatexdvipdfm.js'),source=fs.readFileSync(file,'utf8'),head='function invoke_iiiiiiiiiii(index,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10){',patch='/* Pinned v20022022 table slot 2 is dvipdfmx_main; argument 6 enables lossless zlib compression. */if(index===2)a6=1;';
if(!source.includes(head))throw Error('Pinned invocation signature missing');if(!source.includes(patch))fs.writeFileSync(file,source.replace(head,head+patch));console.log('PASS pinned xdvipdfmx lossless compression enabled');
