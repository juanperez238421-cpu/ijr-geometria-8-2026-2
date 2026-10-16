"use strict";
/* IJR 8°: 4 problem assessment. Answers, events and submission are stored in
 * private Supabase data through a constrained Edge Function. Never expose keys. */
(() => {
 const API="https://rlfxnjbqxbozjdzkbwlz.supabase.co/functions/v1/geometry8-canada-quiz";
 const KEY="ijr-geometry8-canada-quiz-v2";
 const MAX=3,COUNT=4;
 const $=id=>document.getElementById(id);
 const state={status:"welcome",problem:0,strikes:0,startedAt:null,
  session:null,answers:Array.from({length:COUNT},()=>({value:"",unit:"cm²",reasoning:""})),
  armed:false,locked:false,incidentBusy:false};
 let manifest=[];
 let saveTimer=0,focusTimer=0,saveChain=Promise.resolve(),serverReady=false;
 const qs=(selector)=>Array.from(document.querySelectorAll(selector));
 const show=(id)=>["welcomeView","examView","resultView"].forEach(x=>$(x).classList.toggle("hidden",x!==id));
 const two=x=>String(x).padStart(2,"0");
 const duration=()=>{const sec=state.startedAt?Math.max(0,Math.floor((Date.now()-new Date(state.startedAt).getTime())/1000)):0;return (sec>=3600?two(Math.floor(sec/3600))+":":"")+two(Math.floor(sec/60)%60)+":"+two(sec%60);};
 const correctValue=v=>/^\d+(?:[.,]\d+)?$/.test(v.trim())&&Number.isFinite(Number(v.replace(",",".")));
 const complete=a=>correctValue(a.value)&&a.unit==="cm²"&&a.reasoning.trim().length>=10;
 const warn=(message)=>{let e=$("runtimeNotice");if(!e){e=document.createElement("p");e.id="runtimeNotice";e.style.cssText="color:#ad3b44;font-size:12px;max-width:650px;margin:12px 0";$("previewStart").closest(".welcome-actions").after(e);}e.textContent=message;};
 const persistSession=()=>{try{sessionStorage.setItem(KEY,JSON.stringify({session:state.session,problem:state.problem}))}catch{}};
 const readSession=()=>{try{const obj=JSON.parse(sessionStorage.getItem(KEY)||"null");return obj?.session?.attempt_id&&obj?.session?.token?obj:null}catch{return null}};
 async function request(action,more={}){
   const body={action,...more};
   if(action!=="start"){
     if(!state.session)throw Error("La sesión no está disponible.");
     body.attempt_id=state.session.attempt_id;body.token=state.session.token;
   }
   const controller=new AbortController();const t=setTimeout(()=>controller.abort(),18000);
   try{
     const response=await fetch(API,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body),signal:controller.signal,cache:"no-store"});
     const data=await response.json();
     if(!response.ok){throw Error(data.error||"No se pudo conectar con el servidor");}
     return data;
   }catch(err){throw Error(err instanceof Error?err.message:"Error de conexión");}
   finally{clearTimeout(t);}
 }
 function updateStatus(){
   const names={welcome:"DISPONIBLE",active:"EN CURSO",paused:"SESIÓN PAUSADA",blocked:"BLOQUEADA",submitted:"ENTREGADA"};
   $("topStatus").innerHTML='<span class="status-dot"></span> '+(names[state.status]||"DISPONIBLE");
 }
 function updateProgress(){
   const done=state.answers.filter(complete).length;
   $("progress").textContent=done+" / "+COUNT;
   $("strikeDots").setAttribute("aria-label",state.strikes+" de "+MAX+" incidencias");
   Array.from($("strikeDots").children).forEach((n,i)=>n.classList.toggle("active",i<state.strikes));
   qs(".rail-item").forEach((b,i)=>{
      const sel=i===state.problem,ok=complete(state.answers[i]);
      b.classList.toggle("selected",sel);b.classList.toggle("complete",ok);
      b.querySelector(".rail-state").textContent=ok?"✓":"○";
      if(sel)b.setAttribute("aria-current","step");else b.removeAttribute("aria-current");
   });
 }
 function render(){
   const i=state.problem,p=manifest[i];
   if(!p)return;
   $("questionCounter").textContent="EJERCICIO "+two(i+1)+" DE "+two(COUNT);
   $("questionTitle").textContent=p.title;
   $("questionStatement").textContent=p.statement;
   $("diagramNumber").textContent=two(i+1);
   $("figureCount").textContent="Diagrama geométrico vectorial · HD";
   $("pageIndicator").textContent=two(i+1)+" / "+two(COUNT);
   $("prevButton").disabled=i===0;
   $("nextButton").textContent=i===COUNT-1?"Volver al primero ↺":"Siguiente →";
   const frame=$("diagramFrame");
   frame.replaceChildren();
   const img=document.createElement("img");
   img.className="problem-media";img.src=p.diagram+"?v=20261016-qa-r2";img.alt="Problema "+(i+1)+": "+p.title+". "+p.statement;
   img.loading="eager";img.decoding="async";
   img.addEventListener("error",()=>{frame.textContent="No se pudo cargar la figura. Informa al docente.";}, {once:true});
   frame.appendChild(img);
   const a=state.answers[i];
   $("areaValue").value=a.value;
   $("areaUnit").value="cm²";
   $("reasoning").value=a.reasoning;
   $("saveStatus").textContent="Las respuestas se guardan automáticamente.";
   updateProgress();
 }
 function snapshot(){
   const i=state.problem;
   state.answers[i]={value:$("areaValue").value.trim().slice(0,32),unit:"cm²",reasoning:$("reasoning").value.slice(0,5000)};
   updateProgress();
   return {problem_id:"P"+two(i+1),...state.answers[i]};
 }
 function queueSave(data){
   $("saveStatus").textContent="Guardando en servidor…";
   saveChain=saveChain.catch(()=>{}).then(async()=>{
     const answer=await request("answer",data);
     if(answer.saved)$("saveStatus").textContent="Guardado en servidor ✓";
   }).catch(e=>{
     $("saveStatus").textContent="Error al guardar. Intenta escribir nuevamente antes de enviar.";
     console.error("Save failure",e.message);
     throw e;
   });
   // prevent unhandled async rejection when user keeps typing
   saveChain.catch(()=>{});
   return saveChain;
 }
 function saveNow(){
   if(state.status!=="active")return saveChain;
   clearTimeout(saveTimer);
   return queueSave(snapshot());
 }
 function onInput(){
   if(state.status!=="active")return;
   const data=snapshot();
   clearTimeout(saveTimer);
   saveTimer=setTimeout(()=>queueSave(data),550);
 }
 function select(index){
   if(state.status!=="active"||index<0||index>=COUNT)return;
   saveNow();
   state.problem=index;persistSession();render();
 }
 async function fullscreen(){
   if(document.fullscreenElement)return true;
   if(!document.fullscreenEnabled||!document.documentElement.requestFullscreen){
     warn("El navegador no permite pantalla completa. Prueba Chrome o Edge en un computador, o informa al docente para una alternativa.");return false;
   }
   try{await document.documentElement.requestFullscreen({navigationUI:"hide"});return !!document.fullscreenElement;}
   catch{warn("No se pudo activar la pantalla completa. Verifica los permisos del navegador.");return false;}
 }
 async function loadManifest(){
   const r=await fetch("./manifest.json",{cache:"no-store"});
   if(!r.ok)throw Error("No se pudo cargar el examen.");
   const m=await r.json();
   if(!m.public_exam_enabled||!Array.isArray(m.problems)||m.problems.length!==COUNT||
      m.problems.some(p=>!p.ready||!p.statement||!p.title||!/^assets\/[a-z0-9/_-]+\.svg$/.test(p.diagram)))throw Error("El cuestionario no está completo.");
   manifest=m.problems;
 }
 async function start(){
   const name=$("studentName").value.trim().replace(/\s+/g," ");
   const group=$("studentGroup").value;
   if(name.length<3||!["8A","8B","8C","OTRO"].includes(group)||!$("studentAgree").checked){
     warn("Ingresa tu nombre, selecciona el grupo y acepta las instrucciones para comenzar.");return;
   }
   if(!manifest.length){warn("Las figuras aún no están disponibles. Recarga la página.");return;}
   const ok=await fullscreen();
   if(!ok)return;
   $("previewStart").disabled=true;
   try{
     const data=await request("start",{student_name:name,student_group:group,agreed:true});
     state.session={attempt_id:data.attempt_id,token:data.token,student_name:data.student_name,student_group:data.student_group};
     state.startedAt=data.started_at;state.strikes=data.strikes||0;state.status="active";state.armed=true;
     persistSession();show("examView");render();updateStatus();
   }catch(e){
     warn("No se pudo iniciar la evaluación: "+e.message);
     if(document.fullscreenElement)await document.exitFullscreen().catch(()=>{});
   }finally{$("previewStart").disabled=false;}
 }
 function modal(reason){
   const blocked=state.status==="blocked";
   $("modalEyebrow").textContent=blocked?"LÍMITE DE INCIDENCIAS":"CONTROL DE INTEGRIDAD";
   $("modalTitle").textContent=blocked?"Sesión bloqueada":"Salida detectada";
   $("modalText").textContent=blocked?"Se registraron tres incidencias y la sesión fue bloqueada. Contacta al docente para la revisión.":"Se detectó una salida ("+reason+"). Vuelve a pantalla completa para continuar.";
   $("modalStrikeCount").textContent=state.strikes+" de "+MAX+" incidencias";
   $("modalAction").textContent=blocked?"Ver comprobante de bloqueo":"Regresar a pantalla completa";
   $("modalSymbol").textContent=blocked?"×":"!";
   $("modalFoot").textContent="Los eventos quedan registrados con hora del servidor. Una salida no demuestra plagio por sí sola.";
   $("incidentModal").classList.remove("hidden");
 }
 async function incident(reason){
   if(state.status!=="active"||!state.armed||state.incidentBusy)return;
   state.armed=false;state.incidentBusy=true;
   state.status="paused";updateStatus();
   clearTimeout(saveTimer);
   // A single departure generates exactly one event ID even if blur, visibilitychange
   // and fullscreenchange fire together.
   try{
     await saveChain.catch(()=>{});
     const data=await request("incident",{event_id:crypto.randomUUID(),reason});
     state.strikes=data.strikes;
     if(data.state==="blocked")state.status="blocked";
   }catch(e){
     console.error("Incident request failed",e.message);
     warn("Incidencia pendiente de registrar: revisa tu conexión.");
   }finally{
     state.incidentBusy=false;updateStatus();updateProgress();modal(reason);
   }
 }
 async function resume(){
   if(state.status==="blocked"){showResult("blocked");return;}
   if(state.status!=="paused")return;
   const ok=await fullscreen();
   if(!ok)return;
   try{
     const s=await request("status");
     state.strikes=s.strikes;state.status=s.state;
     if(s.state!=="active"){showResult(s.state);return;}
     state.armed=true;$("incidentModal").classList.add("hidden");updateStatus();updateProgress();
   }catch(e){warn("No fue posible reanudar: "+e.message);}
 }
 function showResult(status, receipt, stamp){
   state.armed=false;state.status=status;
   $("incidentModal").classList.add("hidden");show("resultView");updateStatus();
   const blocked=status==="blocked";
   $("resultIcon").textContent=blocked?"!":"✓";
   $("resultHeading").textContent=blocked?"Evaluación bloqueada":"Evaluación enviada";
   $("resultDescription").textContent=blocked?"Se alcanzaron tres incidencias. No se calificará automáticamente: el docente debe revisar el registro.":"Tus respuestas quedaron guardadas de manera privada. No se publican las soluciones ni la nota en esta página.";
   $("resultSummary").textContent="Estudiante: "+(state.session?.student_name||"")+
     "\nGrupo: "+(state.session?.student_group||"")+
     "\nEjercicios con respuesta y desarrollo: "+state.answers.filter(complete).length+" de "+COUNT+
     "\nIncidencias: "+state.strikes+" de "+MAX+
     (stamp?"\nFecha de entrega: "+new Date(stamp).toLocaleString("es-CO"):"");
   $("receipt").textContent="Comprobante: "+(receipt||state.session?.attempt_id||"");
   persistSession();
   if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});
 }
 async function submit(){
   if(state.status!=="active")return;
   $("finishButton").disabled=true;
   try{
     await saveNow();
     const response=await request("submit");
     showResult("submitted",response.receipt,response.submitted_at);
   }catch(e){
     $("saveStatus").textContent="No se ha enviado: "+e.message+". Reintenta cuando vuelva la conexión.";
   }finally{$("finishButton").disabled=false;}
 }
 async function recover(){
   const saved=readSession();if(!saved)return;
   state.session=saved.session;state.problem=Number.isInteger(saved.problem)&&saved.problem>=0&&saved.problem<COUNT?saved.problem:0;
   try{
     const data=await request("status");
     state.startedAt=data.started_at;state.strikes=data.strikes;
     for(let i=0;i<COUNT;i++)state.answers[i]={value:String(data.answers?.["P"+two(i+1)]?.value||""),unit:"cm²",reasoning:String(data.answers?.["P"+two(i+1)]?.reasoning||"")};
     if(data.state==="active"){
       show("examView");render();state.status="active";state.armed=true;
       await incident("recarga o reingreso de página");
     }else if(data.state==="blocked"||data.state==="submitted"){showResult(data.state,data.attempt_id,data.submitted_at);}
     updateStatus();
   }catch(e){
     show("welcomeView");warn("No se pudo recuperar la sesión del servidor. Revisa tu conexión antes de comenzar otra.");
   }
 }
 function reset(){try{sessionStorage.removeItem(KEY)}catch{}state.session=null;state.status="welcome";state.armed=false;show("welcomeView");updateStatus();}
 async function init(){
   $("previewStart").addEventListener("click",start);
   $("prevButton").addEventListener("click",()=>select(state.problem-1));
   $("nextButton").addEventListener("click",()=>select(state.problem===COUNT-1?0:state.problem+1));
   qs(".rail-item").forEach(b=>b.addEventListener("click",()=>select(Number(b.dataset.problem))));
   $("areaValue").addEventListener("input",onInput);
   $("reasoning").addEventListener("input",onInput);
   $("modalAction").addEventListener("click",resume);
   $("finishButton").addEventListener("click",submit);
   $("restartButton").addEventListener("click",reset);
   document.addEventListener("fullscreenchange",()=>{
      if(state.status==="active"&&state.armed&&!document.fullscreenElement)incident("salida de pantalla completa");
   });
   document.addEventListener("visibilitychange",()=>{
      if(document.hidden)incident("cambio de pestaña");
      else if(["paused","blocked"].includes(state.status)&&!state.incidentBusy)modal("cambio de pestaña");
   });
   window.addEventListener("blur",()=>{
      clearTimeout(focusTimer);
      focusTimer=setTimeout(()=>{if(!document.hasFocus()&&!document.hidden)incident("pérdida de foco");},750);
   });
   window.addEventListener("focus",()=>clearTimeout(focusTimer));
   setInterval(()=>{if(state.startedAt&&["active","paused"].includes(state.status))$("clock").textContent=duration();},1000);
   try{await loadManifest();serverReady=true;}catch(e){warn("No se cargaron las figuras: "+e.message);$("previewStart").disabled=true;return;}
   await recover();
   updateStatus();
 }
 init();
})();