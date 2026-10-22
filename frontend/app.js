const form=document.querySelector("#auth-form"), loginTab=document.querySelector("#login-tab"), registerTab=document.querySelector("#register-tab");
const nameField=document.querySelector("#name-field"), nameInput=document.querySelector("#name"), emailInput=document.querySelector("#email"), passwordInput=document.querySelector("#password");
const notice=document.querySelector("#notice"), submitButton=document.querySelector("#submit-button"), submitLabel=document.querySelector("#submit-label");
let mode="login";
function icons(){if(window.lucide)window.lucide.createIcons()}
function clearErrors(){document.querySelectorAll(".field-error").forEach(e=>e.textContent="")}
function hideNotice(){notice.textContent="";notice.className="notice hidden"}
function showNotice(msg,type){notice.textContent=msg;notice.className="notice "+type}
function setMode(next){
 mode=next;const reg=mode==="register";nameField.classList.toggle("hidden",!reg);nameInput.required=reg;
 loginTab.classList.toggle("active",!reg);registerTab.classList.toggle("active",reg);
 loginTab.setAttribute("aria-selected",String(!reg));registerTab.setAttribute("aria-selected",String(reg));
 document.querySelector("#form-kicker").textContent=reg?"COMECE SUA JORNADA":"BEM-VINDA(O) DE VOLTA";
 document.querySelector("#form-title").textContent=reg?"Crie sua conta.":"Que bom ter você aqui.";
 document.querySelector("#form-subtitle").textContent=reg?"Só precisamos de alguns dados para começar.":"Entre com seus dados para continuar.";
 submitLabel.textContent=reg?"Criar minha conta":"Entrar na minha conta";passwordInput.autocomplete=reg?"new-password":"current-password";
 document.querySelector("#password-hint").textContent=reg?"Use pelo menos 10 caracteres.":"Use a senha cadastrada na sua conta.";
 document.querySelector("#switch-copy").innerHTML=reg?'Já tem uma conta? <button type="button" id="switch-action">Entrar</button>':'Ainda não tem uma conta? <button type="button" id="switch-action">Criar conta grátis</button>';
 document.querySelector("#switch-action").addEventListener("click",()=>setMode(reg?"login":"register"));clearErrors();hideNotice();form.reset();icons()
}
loginTab.addEventListener("click",()=>setMode("login"));registerTab.addEventListener("click",()=>setMode("register"));
document.querySelector("#toggle-password").addEventListener("click",()=>{const show=passwordInput.type==="password";passwordInput.type=show?"text":"password";document.querySelector("#toggle-password").innerHTML=`<i data-lucide="${show?"eye-off":"eye"}"></i>`;icons()});
form.addEventListener("submit",async e=>{
 e.preventDefault();clearErrors();hideNotice();const name=nameInput.value.trim(),email=emailInput.value.trim(),password=passwordInput.value;let valid=true;
 if(mode==="register"&&name.length<2){document.querySelector("#name-error").textContent="Informe seu nome (pelo menos 2 caracteres).";valid=false}
 if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){document.querySelector("#email-error").textContent="Digite um e-mail válido.";valid=false}
 if(mode==="register"&&password.length<10){document.querySelector("#password-error").textContent="A senha precisa ter pelo menos 10 caracteres.";valid=false}
 if(!password){document.querySelector("#password-error").textContent="Digite sua senha.";valid=false}if(!valid)return;
 const originalMode=mode;submitButton.disabled=true;submitLabel.textContent=originalMode==="register"?"Criando sua conta...":"Verificando acesso...";
 try{
  const response=await fetch(originalMode==="register"?"/api/auth/register":"/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(originalMode==="register"?{name,email,password}:{email,password})});
  const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.error||"Não foi possível concluir a operação.");
  if(originalMode==="register"){setMode("login");emailInput.value=email;showNotice(data.message||"Conta criada. Agora você pode entrar.",data.welcome_email_queued===false?"error":"success")}
  else showNotice(data.message||"Login realizado com sucesso.","success");
 }catch(err){showNotice(err.message||"Não foi possível conectar ao servidor.","error")}
 finally{submitButton.disabled=false;submitLabel.textContent=mode==="register"?"Criar minha conta":"Entrar na minha conta"}
});
icons();
