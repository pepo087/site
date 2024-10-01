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
                }, index * 1000); // Ritardo incrementale per ciascun elemento (300 ms per esempio)
            });
        }, 50); // Breve ritardo per permettere alla sezione di essere visibile
    });
});
 function filterList() {
        const input = document.getElementById('searchInput');
        const filter = input.value.toLowerCase();
        const list = document.getElementById('linkList');
        const items = list.getElementsByTagName('li');

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            const text = item.textContent || item.innerText;
            item.style.display = text.toLowerCase().includes(filter) ? '' : 'none';
        }
    }

    function sortListByName() {
        const list = document.getElementById('linkList');
        const items = Array.from(list.getElementsByTagName('li'));

        items.sort((a, b) => {
            const nameA = a.textContent.toLowerCase();
            const nameB = b.textContent.toLowerCase();
            return nameA.localeCompare(nameB);
        });

        // Riaggiungi gli elementi ordinati alla lista
        items.forEach(item => list.appendChild(item));
    }

    function sortListByDate() {
        const list = document.getElementById('linkList');
        const items = Array.from(list.getElementsByTagName('li'));

        items.sort((a, b) => {
            const dateA = new Date(a.getAttribute('data-date'));
            const dateB = new Date(b.getAttribute('data-date'));
            return dateA - dateB;
        });

        // Riaggiungi gli elementi ordinati alla lista
        items.forEach(item => list.appendChild(item));
    }// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});

// Mostra la sezione di benvenuto all'inizio
const welcomeSection = document.getElementById('welcome');
if (welcomeSection) {
    welcomeSection.style.display = "block"; // Mostra la sezione di benvenuto
    const content = welcomeSection.querySelector('.section-content');
    if (content) {
        content.classList.add('visible'); // Aggiungi la classe visibile alla sezione di benvenuto
    }
}
