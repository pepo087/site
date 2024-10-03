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




    function toggleFolder() {
        var folderContainer = document.getElementById('folderContainer');
        folderContainer.style.display = folderContainer.style.display === 'none' ? 'block' : 'none';
    }

    function toggleFolderContent(folder) {
        var nested = folder.nextElementSibling;
        if (nested) {
            // Toggle the display of the nested folder
            nested.style.display = nested.style.display === 'none' || nested.style.display === '' ? 'block' : 'none';
            // Toggle the 'open' class
            folder.classList.toggle('open');
        }
    }

    function filterList() {
        var input, filter, ul, li, a, i, txtValue;
        input = document.getElementById("searchInput");
        filter = input.value.toUpperCase();
        ul = document.getElementById("folderList");
        li = ul.getElementsByTagName("li");
        
        for (i = 0; i < li.length; i++) {
            a = li[i].getElementsByTagName("a")[0];
            txtValue = a.textContent || a.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = "";
            } else {
                li[i].style.display = "none";
            }
        }
    }

    function sortListByName() {
        var ul = document.getElementById("folderList");
        var li = Array.from(ul.getElementsByTagName("li"));
        
        li.sort(function(a, b) {
            var nameA = a.getElementsByTagName("a")[0].textContent.toLowerCase();
            var nameB = b.getElementsByTagName("a")[0].textContent.toLowerCase();
            return nameA.localeCompare(nameB);
        });

        ul.innerHTML = "";
        li.forEach(function(item) {
            ul.appendChild(item);
        });
    }



   
    // Nascondi tutte le sezioni all'inizio
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
// Carica Particles.js
document.addEventListener("DOMContentLoaded", function() {
    particlesJS.load('particles-js', 'Particles.json', function() {
        console.log('callback - particles.js config loaded');
    });
});