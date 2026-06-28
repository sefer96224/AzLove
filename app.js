// Telegram Web App obyektini çağırırıq
let tg = window.Telegram.WebApp;

// Pəncərə açılan kimi tam ekrana genişlənsin
tg.expand();

// HTML-dəki düymələri tapırıq
let btnPass = document.getElementById("btn-pass");
let btnLike = document.getElementById("btn-like");

// "Keç" düyməsinə basıldıqda
btnPass.addEventListener("click", function() {
    // Python-a "pass" sözünü göndəririk
    tg.sendData("pass"); 
    tg.close(); // Məlumat gedəndən sonra pəncərəni bağlayırıq
});

// "Bəyən" düyməsinə basıldıqda
btnLike.addEventListener("click", function() {
    // Python-a "like" sözünü göndəririk
    tg.sendData("like"); 
    tg.close();
});
