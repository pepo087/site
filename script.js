// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});

// Funzione per mostrare/nascondere le sezioni quando un link di navigazione viene cliccato
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(event) {
        const sectionId = this.getAttribute('href');
        const section = document.querySelector(sectionId);
        
        // Mostra/Nascondi la sezione
        if (section.style.display === "none" || section.style.display === "") {
            section.style.display = "block"; // Mostra la sezione
        } else {
            section.style.display = "none"; // Nascondi la sezione
        }

        // Impedisci il comportamento predefinito del link
        event.preventDefault();
    });
});

// jQuery per l'effetto slide delle competenze
$(document).ready(function() {
    $('.skill-title').click(function() {
        // Toggle la visibilità del contenuto e gestisci l'animazione slide
        $(this).next('.skill-content').slideToggle(300);
    });
});
