// Create tooltip element
const tooltip = document.createElement("div");
tooltip.id = "phishguard-tooltip";
tooltip.style.cssText = `
  position: fixed;
  background: #1e1e2e;
  color: #ffffff;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  max-width: 280px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  z-index: 999999;
  display: none;
  pointer-events: none;
  border-left: 4px solid #666;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.4;
`;
document.body.appendChild(tooltip);

// Cache results to avoid repeated API calls
const cache = new Map();

// Function to display tooltip result
function showResult(result) {
  let icon = "🟢";
  let color = "#22c55e";
  let label = "SAFE";
  
  if (result.label === "phishing") {
    icon = "🔴";
    color = "#ef4444";
    label = "PHISHING";
  } else if (result.label === "suspicious") {
    icon = "🟡";
    color = "#f59e0b";
    label = "SUSPICIOUS";
  } else if (result.label === "unknown") {
    icon = "❓";
    color = "#666";
    label = "UNKNOWN";
  }
  
  tooltip.style.borderLeftColor = color;
  const confidencePercent = (result.confidence * 100).toFixed(1);
  const reasonsText = result.reasons && result.reasons.length > 0 
    ? result.reasons.slice(0, 2).join(" · ") 
    : "No additional data";
  
  tooltip.innerHTML = `
    <strong style="font-size:14px">${icon} ${label}</strong>
    <span style="color:#aaa; font-size:11px"> · ${confidencePercent}%</span>
    <br/>
    <small style="color:#ccc">${reasonsText}</small>
  `;
}

// Scan all links on page
function scanLinks() {
  const links = document.querySelectorAll("a[href]");
  
  links.forEach(link => {
    const url = link.href;
    if (!url || url.startsWith("javascript") || url.startsWith("#") || url.startsWith("mailto")) return;
    
    // Hover event
    link.addEventListener("mouseenter", async (e) => {
      tooltip.style.display = "block";
      tooltip.style.left = e.clientX + 15 + "px";
      tooltip.style.top = e.clientY + 15 + "px";
      tooltip.innerHTML = "🔍 Checking...";
      tooltip.style.borderLeftColor = "#666";
      
      if (cache.has(url)) {
        showResult(cache.get(url));
        return;
      }
      
      try {
        const result = await chrome.runtime.sendMessage({ type: "CHECK_URL", url });
        cache.set(url, result);
        showResult(result);
      } catch (err) {
        showResult({ label: "unknown", confidence: 0, reasons: ["Check failed"] });
      }
    });
    
    // Move tooltip with cursor
    link.addEventListener("mousemove", (e) => {
      tooltip.style.left = e.clientX + 15 + "px";
      tooltip.style.top = e.clientY + 15 + "px";
    });
    
    // Hide tooltip on leave
    link.addEventListener("mouseleave", () => {
      tooltip.style.display = "none";
    });
    
    // Double-click system for phishing links
    let clickCount = 0;
    let timeout;
    
    link.addEventListener("click", (e) => {
      const cached = cache.get(url);
      if (cached && cached.label === "phishing") {
        e.preventDefault();
        clickCount++;
        
        if (clickCount === 1) {
          tooltip.style.display = "block";
          tooltip.innerHTML = "⚠️ PHISHING DETECTED! Click again to proceed (not recommended)";
          tooltip.style.borderLeftColor = "#ef4444";
          tooltip.style.left = e.clientX + 15 + "px";
          tooltip.style.top = e.clientY + 15 + "px";
          
          timeout = setTimeout(() => {
            clickCount = 0;
            tooltip.style.display = "none";
          }, 2000);
        } else if (clickCount === 2) {
          clearTimeout(timeout);
          window.open(url, "_blank");
          clickCount = 0;
          tooltip.style.display = "none";
        }
      }
    });
  });
}

// Initialize when page loads
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", scanLinks);
} else {
  scanLinks();
}

// Watch for dynamically added links
const observer = new MutationObserver(() => scanLinks());
observer.observe(document.body, { childList: true, subtree: true });