

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
 $(document).ready(function() {
        $('.skill-title').click(function() {
            // Toggle la visibilità del contenuto e gestisci l'animazione slide
            $(this).next('.skill-content').slideToggle(300);
        });
    });
// Nascondi tutte le sezioni all'inizio
document.querySelectorAll('section').forEach(section => {
    section.style.display = "none";
});
