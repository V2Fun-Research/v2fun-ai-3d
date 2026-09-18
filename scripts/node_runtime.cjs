'use strict';
const fs=require('node:fs'),path=require('node:path'),{createRequire}=require('node:module');

function loadModule(name,a={},project=process.cwd()){
 const dirs=[a.modules,process.env.V2FUN_NODE_MODULES,path.join(project,'node_modules')].filter(Boolean);
 for(const dir of dirs){
  try{return require(require.resolve(name,{paths:[path.dirname(path.resolve(dir)),path.resolve(dir)]}));}catch{}
 }
 try{return createRequire(path.join(path.resolve(project),'package.json'))(name);}catch{
  throw Error('Missing '+name+'; use --modules /installed/node_modules or V2FUN_NODE_MODULES, or run v2fun.py deps. No automatic installation.');
 }
}
function threeDir(a={},project=process.cwd()){
 const dirs=[a['three-dir']&&path.resolve(a['three-dir']),path.join(project,'vendor'),
  a.modules&&path.join(path.resolve(a.modules),'three'),
  process.env.V2FUN_NODE_MODULES&&path.join(process.env.V2FUN_NODE_MODULES,'three'),
  path.join(project,'node_modules/three')].filter(Boolean);
 for(const dir of dirs)if(fs.existsSync(path.join(dir,'build/three.module.js')))return dir;
 throw Error('Three.js not found; pass --three-dir /installed/three or run v2fun.py deps');
}
function doctor(project,a={}){
 const report={node:process.version,modules:{}};
 try{const dir=threeDir(a,project),p=path.join(dir,'package.json');report.modules.three={available:true,path:dir,version:fs.existsSync(p)?JSON.parse(fs.readFileSync(p,'utf8')).version:null};}
 catch{report.modules.three={available:false};}
 for(const name of ['playwright','sharp']){
  try{const m=loadModule(name,a,project);report.modules[name]={available:true};
   if(name==='playwright'){const p=m.chromium.executablePath();report.browser={path:process.env.V2FUN_BROWSER||p,available:fs.existsSync(process.env.V2FUN_BROWSER||p)};}
  }catch{report.modules[name]={available:false};}
 }
 return report;
}
module.exports={loadModule,threeDir,doctor};
if(require.main===module){try{console.log(JSON.stringify(doctor(path.resolve(process.argv[2]||'.'))));}catch{console.error(JSON.stringify({status:'needs_attention',error:'Node environment inspection failed'}));process.exitCode=1;}}
