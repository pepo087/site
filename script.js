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

// Mostra/nascondi il contenuto al passaggio del mouse
$(document).ready(function() {
    $('.skill-title').hover(
        function() {
            // Mostra il contenuto con slide down
            $(this).next('.skill-content').stop(true, true).slideDown(300);
        },
        function() {
            // Nascondi il contenuto con slide up
            $(this).next('.skill-content').stop(true, true).slideUp(300);
        }
    );
});

// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});
