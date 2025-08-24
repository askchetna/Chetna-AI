const chatBox = document.getElementById("chatBox");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const statusEl = document.getElementById("status");

function addBubble(text, who="me"){
  const div = document.createElement("div");
  div.className = bubble ${who};
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(){
  const text = (input.value || "").trim();
  if(!text) return;

  addBubble(text, "me");
  input.value = "";
  sendBtn.disabled = true; statusEl.textContent = "Thinking...";

  try{
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    addBubble(data.reply || "(no reply)", "ai");
  }catch(err){
    addBubble("Error: "+ err.message, "ai");
  }finally{
    sendBtn.disabled = false; statusEl.textContent = "";
    input.focus();
  }
}

sendBtn.addEventListener("click", sendMessage);
clearBtn.addEventListener("click", () => { chatBox.innerHTML=""; input.focus(); });
input.addEventListener("keydown", (e)=>{ if(e.key==="Enter" && (e.ctrlKey || e.metaKey)) sendMessage(); });
