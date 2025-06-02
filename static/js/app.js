// JavaScript pour PriceCheck

// Fonction pour afficher les notifications
function showNotification(message, type = 'info') {
    // Implémentation simple avec Bootstrap alerts
    const alertDiv = document.createElement('div');
    alertDiv.className = lert alert- alert-dismissible fade show;
    alertDiv.innerHTML = 
        
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    ;
    
    // Ajouter en haut du container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Fonction pour les requêtes AJAX
async function makeRequest(url, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('Erreur de requête:', error);
        showNotification('Erreur de communication avec le serveur', 'danger');
        return null;
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('PriceCheck initialisé');
});
