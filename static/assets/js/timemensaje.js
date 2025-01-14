// Duracion del mensaje solo con javascritp para poder usar lo que es 
window.onload = function () {
    setTimeout(function () {
        var alert = document.querySelector(".alert");
        if (alert) alert.style.display = "none";
    }, 5000); // 5000ms = 5s
};