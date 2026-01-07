// 웹페이지에 주입될 코드
console.log("AI Assistant: YouTube Detected");

// 버튼 생성 UI
const btn = document.createElement("button");
btn.innerText = "🎵 AI 오디오 추출";
btn.style = "position: fixed; top: 10px; right: 10px; z-index: 9999; padding: 10px; background: red; color: white;";
btn.onclick = () => {
    const videoId = new URLSearchParams(window.location.search).get("v");
    if(videoId) {
        alert("서버로 요청을 보냅니다.");
        // FastAPI 서버로 요청
        fetch(`http://127.0.0.1:5000/yt-dl/process?video_id=${videoId}`, { method: "POST" });
    }
};

document.body.appendChild(btn);