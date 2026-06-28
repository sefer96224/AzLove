let tg = window.Telegram.WebApp;
tg.expand();

// 1. Linkdən (URL) gələn məlumatları oxuyuruq
const urlParams = new URLSearchParams(window.location.search);
const candidateId = urlParams.get('id') || '0';
const name = urlParams.get('name') || 'Naməlum';
const age = urlParams.get('age') || '?';
const city = urlParams.get('city') || 'Bilinmir';
const bio = urlParams.get('bio') || 'Məlumat yoxdur.';

// 2. Əgər linkdə məlumat varsa, HTML-i dərhal dəyişirik
if (window.location.search) {
    document.getElementById('user-name-age').innerHTML = `${name}, ${age} <span id="user-city">📍 ${city}</span>`;
    document.getElementById('user-bio').innerText = bio;
}

// 3. Düymələrin funksiyaları (Python-a həm qərarı, həm də adamın ID-sini göndəririk)
let btnPass = document.getElementById("btn-pass");
let btnLike = document.getElementById("btn-like");

btnPass.addEventListener("click", function() {
    let data = { action: "pass", id: candidateId };
    tg.sendData(JSON.stringify(data)); // Məlumatı JSON formatında göndəririk
    tg.close();
});

btnLike.addEventListener("click", function() {
    let data = { action: "like", id: candidateId };
    tg.sendData(JSON.stringify(data));
    tg.close();
});
