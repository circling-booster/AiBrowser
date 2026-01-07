(function() {
    console.log("AiPlugs: YouTube Summarizer Injected");
    
    // apiPort is injected by python/core/injector.py
    const apiPort = window.AiPlugsConfig ? window.AiPlugsConfig.apiPort : 8000;

    const btn = document.createElement("button");
    btn.innerText = "Summarize Video";
    btn.style.position = "fixed";
    btn.style.top = "10px";
    btn.style.right = "10px";
    btn.style.zIndex = 10000;
    document.body.appendChild(btn);

    btn.onclick = async () => {
        const videoId = new URLSearchParams(window.location.search).get("v");
        try {
            const res = await fetch(`http://localhost:${apiPort}/api/plugins/youtube-summarizer/summarize`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ video_id: videoId })
            });
            const data = await res.json();
            alert("Summary: " + data.summary);
        } catch (e) {
            alert("Error: " + e.message);
        }
    };
})();