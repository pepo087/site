// Funzione per mostrare/nascondere le sezioni al clic
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault(); // Impedisce il comportamento predefinito del link

        const sectionId = this.getAttribute('href'); // Ottieni l'ID della sezione
        const section = document.querySelector(sectionId); // Seleziona la sezione

        // Nascondi tutte le sezioni
        document.querySelectorAll('section').forEach(sec => {
            const content = sec.querySelector('.section-content');
            if (content) { // Controlla se l'elemento è presente
                content.classList.remove('visible'); // Rimuovi la classe visibile
            }
            sec.style.display = "none"; // Nascondi tutte le sezioni
        });

        // Mostra la sezione cliccata
        section.style.display = "block"; // Mostra la sezione selezionata
        
        // Aggiungi un timeout per assicurarti che la sezione sia visibile prima di aggiungere la classe
        setTimeout(() => {
            const content = section.querySelector('.section-content');
            if (content) { // Controlla se l'elemento è presente
                content.classList.add('visible'); // Aggiungi la classe visibile
            }
        }, 50); // Breve ritardo per permettere alla sezione di essere visibile
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

