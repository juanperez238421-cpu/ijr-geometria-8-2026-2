import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.4";

const ALLOWED_ORIGIN = "https://juanperez238421-cpu.github.io";
const ALLOWED_IDS = new Set(["P01","P02","P03","P04"]);
const ALLOWED_UNITS = new Set(["cm²"]);
const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const client = createClient(supabaseUrl, serviceRoleKey, {auth:{persistSession:false}});
const TABLE = "geo8_canada_quiz_attempts";

function headers(origin: string|null) {
  const allowed = origin === ALLOWED_ORIGIN || origin === "http://localhost:8000" || origin === "http://127.0.0.1:8000";
  return {
    "Access-Control-Allow-Origin": allowed ? origin! : ALLOWED_ORIGIN,
    "Access-Control-Allow-Headers": "content-type,apikey,authorization,x-client-info",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary":"Origin",
    "Content-Type":"application/json; charset=utf-8",
    "Cache-Control":"no-store"
  };
}
function respond(body: unknown, status=200, origin: string|null=null) {
 return new Response(JSON.stringify(body),{status,headers:headers(origin)});
}
function validUUID(value: unknown): value is string {
 return typeof value === "string" && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
}
async function digest(token: string) {
 const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token));
 return Array.from(new Uint8Array(bytes),b=>b.toString(16).padStart(2,"0")).join("");
}
function newToken() {
 const a = crypto.getRandomValues(new Uint8Array(32));
 return Array.from(a,b=>b.toString(16).padStart(2,"0")).join("");
}
function cleanName(value: unknown) {
 if(typeof value!=="string") return null;
 const s=value.trim().replace(/\s+/g," ").slice(0,120);
 return s.length>=3 && /^[\p{L}\p{M} .'-]+$/u.test(s) ? s : null;
}
function cleanEmail(value: unknown) {
 if(typeof value!== "string") return null;
 const email=value.trim().toLowerCase();
 return email.length<=160 && /^[a-z0-9][a-z0-9._+-]*@ijr\.edu\.co$/.test(email) ? email : null;
}
function studentView(row: Record<string,unknown>) {
 return {
   attempt_id:row.id,
   student_name:row.student_name,
   student_email:row.student_email ?? null,
   identity_mode:row.identity_mode ?? "legacy_name_only",
   student_group:row.student_group,
   state:row.state,
   strikes:row.strikes,
   started_at:row.started_at,
   submitted_at:row.submitted_at,
   answers:row.answers??{},
   events:Array.isArray(row.events)?row.events:[]
 };
}

Deno.serve(async(req:Request) => {
 const origin=req.headers.get("origin");
 if(req.method==="OPTIONS") return new Response(null,{status:204,headers:headers(origin)});
 if(req.method!=="POST") return respond({error:"METHOD_NOT_ALLOWED"},405,origin);
 if(origin && origin!==ALLOWED_ORIGIN && origin!=="http://localhost:8000" && origin!=="http://127.0.0.1:8000") {
   return respond({error:"ORIGIN_NOT_ALLOWED"},403,origin);
 }
 if(!serviceRoleKey || !supabaseUrl) return respond({error:"SERVER_MISCONFIGURED"},500,origin);
 let payload:Record<string,unknown>;
 try {
   if(Number(req.headers.get("content-length")||"0")>12000) return respond({error:"PAYLOAD_TOO_LARGE"},413,origin);
   payload=await req.json();
   if(!payload || typeof payload!=="object" || Array.isArray(payload)) throw Error("invalid");
 } catch {return respond({error:"INVALID_JSON"},400,origin);}
 const action=payload.action;
 try {
   if(action==="start"){
     const student_name=cleanName(payload.student_name);
     const student_group=payload.student_group;
     const student_email=cleanEmail(payload.student_email);
     if(!student_name || !student_email || !["8A","8B","8C","OTRO"].includes(String(student_group)) || payload.agreed!==true) {
       return respond({error:"INSTITUTIONAL_EMAIL_AND_STUDENT_INFO_REQUIRED"},400,origin);
     }
     const token=newToken();
     const token_hash=await digest(token);
     const {data,error}=await client.from(TABLE).insert({student_name,student_group,student_email,identity_mode:"institutional_email_declared",token_hash}).select("id,state,strikes,started_at").single();
     if(error || !data) return respond({error:"START_UNAVAILABLE"},500,origin);
     return respond({attempt_id:data.id,token,student_name,student_group,student_email,identity_mode:"institutional_email_declared",state:data.state,strikes:data.strikes,started_at:data.started_at},200,origin);
   }

   if(!validUUID(payload.attempt_id) || typeof payload.token!=="string" || !/^[a-f0-9]{64}$/.test(payload.token)) {
     return respond({error:"SESSION_REQUIRED"},401,origin);
   }
   const hash=await digest(payload.token);
   const {data:row,error:fetchError}=await client.from(TABLE).select("id,student_name,student_group,student_email,identity_mode,token_hash,answers,strikes,events,state,started_at,submitted_at").eq("id",payload.attempt_id).eq("token_hash",hash).maybeSingle();
   if(fetchError) return respond({error:"SESSION_LOOKUP_FAILED"},500,origin);
   if(!row) return respond({error:"INVALID_SESSION"},401,origin);

   if(action==="status") return respond(studentView(row),200,origin);
   if(row.state!=="active") return respond({error:row.state==="blocked"?"SESSION_BLOCKED":"ALREADY_SUBMITTED",...studentView(row)},409,origin);

   if(action==="answer") {
     const problem_id=payload.problem_id;
     if(typeof problem_id!=="string"||!ALLOWED_IDS.has(problem_id)) return respond({error:"INVALID_PROBLEM"},400,origin);
     const value=typeof payload.value==="string"?payload.value.trim():"";
     const unit=payload.unit;
     const reasoning=typeof payload.reasoning==="string"?payload.reasoning.trim():"";
     if(value.length>32||(!/^\d+(?:[.,]\d+)?$/.test(value)&&value!=="")||typeof unit!=="string"||(!ALLOWED_UNITS.has(unit)&&unit!=="")||reasoning.length>5000) {
       return respond({error:"INVALID_ANSWER"},400,origin);
     }
     const answers={...(row.answers??{}),[problem_id]:{value,unit,reasoning}};
     const {error}=await client.from(TABLE).update({answers,updated_at:new Date().toISOString()}).eq("id",row.id).eq("state","active");
     if(error) return respond({error:"SAVE_FAILED"},500,origin);
     return respond({saved:true,problem_id},200,origin);
   }

   if(action==="incident"){
     const event_id=payload.event_id;
     if(!validUUID(event_id)) return respond({error:"INVALID_EVENT_ID"},400,origin);
     const oldEvents=Array.isArray(row.events)?row.events:[];
     if(oldEvents.some((e:any)=>e && e.event_id===event_id)) return respond({strikes:row.strikes,state:row.state,duplicate:true},200,origin);
     const reason=String(payload.reason||"salida").replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ 0-9_-]/g,"").slice(0,90);
     const strikes=Math.min(3,Number(row.strikes)+1);
     const next= {event_id,reason,occurred_at:new Date().toISOString(),strike:strikes};
     const state=strikes>=3?"blocked":"active";
     const events=[...oldEvents.slice(-9),next];
     const {error}=await client.from(TABLE).update({strikes,state,events,updated_at:new Date().toISOString()}).eq("id",row.id).eq("state","active");
     if(error) return respond({error:"INCIDENT_FAILED"},500,origin);
     return respond({strikes,state},200,origin);
   }

   if(action==="submit"){
     const now=new Date().toISOString();
     const {error}=await client.from(TABLE).update({state:"submitted",submitted_at:now,updated_at:now}).eq("id",row.id).eq("state","active");
     if(error) return respond({error:"SUBMIT_FAILED"},500,origin);
     return respond({state:"submitted",receipt:row.id,submitted_at:now,strikes:row.strikes},200,origin);
   }
   return respond({error:"UNKNOWN_ACTION"},400,origin);
 } catch (error) {
   console.error("Geometry quiz action failed",String(error));
   return respond({error:"INTERNAL_ERROR"},500,origin);
 }
});