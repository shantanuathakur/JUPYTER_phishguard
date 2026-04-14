const API_URL = "https://phishguard-api-jqnn.onrender.com/predict";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CHECK_URL") {
    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: message.url })
    })
    .then(response => response.json())
    .then(data => sendResponse(data))
    .catch(error => sendResponse({ 
      label: "unknown", 
      confidence: 0, 
      reasons: ["Cannot connect to server"] 
    }));
    
    return true;
  }
});