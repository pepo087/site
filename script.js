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
            // Nascondi anche gli item di progetto
            sec.querySelectorAll('.project-item').forEach(item => {
                item.classList.remove('visible');
            });
            sec.style.display = "none"; // Nascondi tutte le sezioni
        });

        // Mostra la sezione cliccata
        section.style.display = "block"; // Mostra la sezione selezionata
        
        // Aggiungi un timeout per assicurarti che la sezione sia visibile prima di aggiungere la classe
        setTimeout(() => {
            const content = section.querySelector('.section-content');
            if (content) { // Controlla se l'elemento è presente
                content.classList.add('visible'); // Aggiungi la classe visibile alla sezione
            }

            // Mostra gli elementi di progetto uno alla volta
            const items = section.querySelectorAll('.project-item');
            items.forEach((item, index) => {
                setTimeout(() => {
                    item.classList.add('visible'); // Aggiungi la classe visibile a ciascun progetto
                }, index * 5000); // Ritardo incrementale per ciascun elemento (300 ms per esempio)
            });
        }, 50); // Breve ritardo per permettere alla sezione di essere visibile
    });
});

// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});

