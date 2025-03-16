function expandImage(img) {
    const container = img.parentElement;
    if (container.classList.contains('expanded')) {
        container.classList.remove('expanded');
    } else {
        container.classList.add('expanded');
    }
}

// Fermer l'image agrandie en cliquant n'importe où
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('gallery-item') && 
        e.target.classList.contains('expanded')) {
        e.target.classList.remove('expanded');
    }
}); 