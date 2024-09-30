// Mostra un messaggio di benvenuto quando la pagina si carica
window.onload = function() {
    alert("Benvenuto nella mia pagina web professionale!");
};

// Funzione per mostrare/nascondere le sezioni
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(event) {
        const sectionId = this.getAttribute('href');
        const section = document.querySelector(sectionId);
        
        if (section.style.display === "none" || section.style.display === "") {
            section.style.display = "block"; // Mostra la sezione
        } else {
            section.style.display = "none"; // Nascondi la sezione
        }
        event.preventDefault(); // Impedisce il comportamento predefinito del link
    });
});

// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});
