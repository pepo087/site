// Funzione per mostrare/nascondere le sezioni al clic
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(event) {
        const sectionId = this.getAttribute('href');
        const section = document.querySelector(sectionId);
        
        // Nascondi tutte le sezioni
        document.querySelectorAll('section').forEach(sec => {
            sec.querySelector('.section-content').classList.remove('visible'); // Rimuovi la classe visibile
            sec.style.display = "none"; // Nascondi tutte le sezioni
        });

        // Mostra la sezione cliccata
        section.style.display = "block"; // Mostra la sezione selezionata

        // Aggiungi un timeout per assicurarti che la sezione sia visibile prima di aggiungere la classe
        setTimeout(() => {
            section.querySelector('.section-content').classList.add('visible'); // Aggiungi la classe visibile
        }, 50); // Breve ritardo per permettere alla sezione di essere visibile

        event.preventDefault(); // Impedisce il comportamento predefinito del link
    });
});

// Mostra/nascondi il contenuto delle competenze al passaggio del mouse
$(document).ready(function() {
    $('.skill-title').hover(
        function() {
            $(this).next('.skill-content').stop(true, true).slideDown(300);
        },
        function() {
            $(this).next('.skill-content').stop(true, true).slideUp(300);
        }
    );
});

// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});
