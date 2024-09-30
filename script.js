// Funzione per mostrare/nascondere le sezioni al clic
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(event) {
        const sectionId = this.getAttribute('href');
        const section = document.querySelector(sectionId);
        
        // Nascondi tutte le sezioni
        document.querySelectorAll('section').forEach(sec => {
            sec.style.display = "none"; // Nascondi tutte le sezioni
        });

        // Mostra la sezione cliccata
        section.style.display = "block"; // Mostra la sezione selezionata

        event.preventDefault(); // Impedisce il comportamento predefinito del link
    });
});

// Mostra/nascondi il contenuto delle competenze al passaggio del mouse
$(document).ready(function() {
    $('.skill-title').hover(
        function() {
            // Mostra il contenuto con slide down
            $(this).next('.skill-content').stop(true, true).slideDown(300);
        }
    );
});
// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});
