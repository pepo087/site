// Funzione per mostrare/nascondere le sezioni al clic
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(event) {
        // Solo impedire il comportamento predefinito per link specifici, se necessario

        const sectionId = this.getAttribute('href'); // Ottieni l'ID della sezione
        const section = document.querySelector(sectionId); // Seleziona la sezione

        // Nascondi tutte le sezioni aggiungendo la classe 'hidden'
        document.querySelectorAll('section').forEach(sec => {
            const content = sec.querySelector('.section-content');
            if (content) {
                content.classList.remove('visible'); // Rimuovi la classe visibile
            }
            sec.classList.add('hidden'); // Nascondi tutte le sezioni aggiungendo 'hidden'
        });

        // Mostra la sezione cliccata rimuovendo la classe 'hidden'
        section.classList.remove('hidden'); // Mostra la sezione selezionata
        
        // Aggiungi un timeout per assicurarti che la sezione sia visibile prima di aggiungere la classe
        setTimeout(() => {
            const content = section.querySelector('.section-content');
            if (content) {
                content.classList.add('visible'); // Aggiungi la classe visibile alla sezione
            }

            // Mostra gli elementi di progetto uno alla volta
            const items = section.querySelectorAll('.project-item');
            items.forEach((item, index) => {
                setTimeout(() => {
                    item.classList.add('visible'); // Aggiungi la classe visibile a ciascun progetto
                }, index * 1000); // Ritardo incrementale per ciascun elemento (1000 ms per esempio)
            });
        }, 50); // Breve ritardo per permettere alla sezione di essere visibile
    });
});

// Funzione per mostrare/nascondere cartelle
function toggleFolder() {
    var folderContainer = document.getElementById('folderContainer');
    folderContainer.classList.toggle('hidden'); // Usa la classe hidden per il toggle
}

// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.classList.add('hidden'); // Usa la classe hidden per nascondere le sezioni
});

// Mostra la sezione di benvenuto all'inizio
const welcomeSection = document.getElementById('welcome');
if (welcomeSection) {
    welcomeSection.classList.remove('hidden'); // Mostra la sezione di benvenuto
    const content = welcomeSection.querySelector('.section-content');
    if (content) {
        content.classList.add('visible'); // Aggiungi la classe visibile alla sezione di benvenuto
    }
}
