let tg = window.Telegram.WebApp;
tg.expand();

// 1. Linkdən (URL) gələn məlumatları oxuyuruq
const urlParams = new URLSearchParams(window.location.search);
const candidateId = urlParams.get('id') || '0';
const name = urlParams.get('name') || 'Naməlum';
const age = urlParams.get('age') || '?';
const city = urlParams.get('city') || 'Bilinmir';
const bio = urlParams.get('bio') || 'Məlumat yoxdur.';
const photo = urlParams.get('photo') || 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80';

// 2. Məlumatları HTML-ə yerləşdiririk
if (window.location.search) {
    document.getElementById('user-name-age').innerHTML = `${name}, ${age} <span id="user-city">📍 ${city}</span>`;
    document.getElementById('user-bio').innerText = bio;
    document.getElementById('user-image').src = photo; // Şəkli dinamik dəyişir
}

// 3. Düymə funksiyaları
let btnPass = document.getElementById("btn-pass");
let btnLike = document.getElementById("btn-like");

btnPass.addEventListener("click", function() {
    let data = { action: "pass", id: candidateId };
    tg.sendData(JSON.stringify(data));
    tg.close();
});

btnLike.addEventListener("click", function() {
    let data = { action: "like", id: candidateId };
    tg.sendData(JSON.stringify(data));
    tg.close();
});
