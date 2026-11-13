import mysql from '../admin/node_modules/mysql2/promise.js'
import {createRequire} from 'node:module'
const require=createRequire(new URL('../admin/package.json',import.meta.url))
const {Queue}=require('bullmq')
// Pause automation in both modes. The AI launcher enables interactive chat only.
for(const name of ['file-embeddings','drug-ingest','benchmarks']){
 const q=new Queue(name,{connection:{host:process.env.REDIS_HOST,port:Number(process.env.REDIS_PORT)}})
 await q.pause();await q.close()
}
const enabled=process.argv[2]==='on'
const db=await mysql.createConnection({host:process.env.DB_HOST,port:Number(process.env.DB_PORT),user:process.env.DB_USER,password:process.env.DB_PASSWORD,database:process.env.DB_DATABASE})
try{
 await db.beginTransaction()
 for(const [key,value] of [['ai.remoteOllamaUrl',enabled?'http://127.0.0.1:11434':null],['chat.suggestionsEnabled','false'],['chat.lastModel','gemma3:4b'],['rag.defaultIngestPolicy','Manual']]){
  await db.execute('INSERT INTO kv_store (`key`,value,created_at,updated_at) VALUES (?,?,NOW(),NOW()) ON DUPLICATE KEY UPDATE value=VALUES(value),updated_at=NOW()',[key,value])
 }
 await db.execute('UPDATE services SET installed=?, installation_status=? WHERE service_name=?',[enabled?1:0,'idle','nomad_ollama'])
 await db.commit()
} catch(error){await db.rollback();throw error}finally{await db.end()}
console.log(enabled?'Interactive local AI enabled by launch choice; indexing stays paused.':'NOMAD AI disabled; AI queues paused.')
