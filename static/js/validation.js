
/**
 * Validation côté client pour PriceChecker
 * ADAPTÉ aux IDs existants dans vos templates
 */

// Validation en temps réel côté client
function validateProductName(name) {
    if (!name || name.trim().length < 3) {
        return "Le nom doit contenir au moins 3 caractères";
    }
    if (name.length > 100) {
        return "Le nom ne peut pas dépasser 100 caractères";
    }
    // Vérifier les caractères dangereux
    const dangerousChars = ['<', '>', '"', '&'];
    if (dangerousChars.some(char => name.includes(char))) {
        return "Le nom contient des caractères non autorisés";
    }
    return "";
}

function validateURL(url) {
    if (!url || (!url.startsWith('http://') && !url.startsWith('https://'))) {
        return "L'URL doit commencer par http:// ou https://";
    }
    if (url.length > 2000) {
        return "L'URL est trop longue";
    }
    // Vérifier les URLs suspectes
    const suspicious = ['localhost', '127.0.0.1', '0.0.0.0'];
    if (suspicious.some(domain => url.toLowerCase().includes(domain))) {
        return "Cette URL n'est pas autorisée";
    }
    return "";
}

function validateShopName(shopName) {
    if (!shopName || shopName.trim().length < 2) {
        return "Le nom de la boutique doit contenir au moins 2 caractères";
    }
    if (shopName.length > 50) {
        return "Le nom de la boutique ne peut pas dépasser 50 caractères";
    }
    return "";
}

function validateDescription(description) {
    if (description && description.length > 500) {
        return "La description ne peut pas dépasser 500 caractères";
    }
    return "";
}

// Afficher les messages de validation
function showValidationMessage(input, message) {
    // Supprimer l'ancien message
    let errorDiv = input.parentNode.querySelector('.validation-message');
    if (errorDiv) {
        errorDiv.remove();
    }

    // Créer le nouveau message
    errorDiv = document.createElement('div');
    errorDiv.className = 'validation-message mt-1';

    if (message) {
        errorDiv.innerHTML = `<small class="text-danger">❌ ${message}</small>`;
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
    } else if (input.value.trim()) {
        errorDiv.innerHTML = `<small class="text-success">✅ Valide</small>`;
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    } else {
        input.classList.remove('is-valid', 'is-invalid');
    }

    input.parentNode.appendChild(errorDiv);
}

// Validation en temps réel - ADAPTÉE À VOS IDs
function setupRealTimeValidation() {
    // ✅ VALIDATION NOM PRODUIT (votre ID: "name")
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.addEventListener('input', function() {
            const error = validateProductName(this.value);
            showValidationMessage(this, error);
        });
    }

    // ✅ VALIDATION DESCRIPTION (votre ID: "description")
    const descInput = document.getElementById('description');
    if (descInput) {
        descInput.addEventListener('input', function() {
            const error = validateDescription(this.value);
            showValidationMessage(this, error);
        });
    }

    // ✅ VALIDATION URL (pour template add_link - à vérifier)
    const urlInput = document.getElementById('url');
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const error = validateURL(this.value);
            showValidationMessage(this, error);
        });
    }

    // ✅ VALIDATION NOM BOUTIQUE (pour template add_link - à vérifier)
    const shopNameInput = document.getElementById('shop_name');
    if (shopNameInput) {
        shopNameInput.addEventListener('input', function() {
            const error = validateShopName(this.value);
            showValidationMessage(this, error);
        });
    }

    // ✅ SÉLECTEUR CSS (pour template add_link - à vérifier)
    const selectorInput = document.getElementById('css_selector');
    if (selectorInput) {
        selectorInput.addEventListener('input', function() {
            // Validation basique pour sélecteur CSS
            const error = (this.value.length > 200) ? "Sélecteur trop long" : "";
            showValidationMessage(this, error);
        });
    }
}

// Validation avant soumission
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required]');

    inputs.forEach(input => {
        let error = "";

        // ✅ SWITCH BASÉ SUR VOS IDs RÉELS
        switch(input.id) {
            case 'name': // Votre ID pour nom produit
                error = validateProductName(input.value);
                break;
            case 'description': // Votre ID pour description
                error = validateDescription(input.value);
                break;
            case 'url': // ID probable pour URL
                error = validateURL(input.value);
                break;
            case 'shop_name': // ID probable pour nom boutique
                error = validateShopName(input.value);
                break;
        }

        showValidationMessage(input, error);
        if (error) isValid = false;
    });

    return isValid;
}

// Initialisation quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    setupRealTimeValidation();

    // Validation des formulaires à la soumission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                // Scroller vers la première erreur
                const firstError = this.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        });
    });
});

// API de validation côté serveur (bonus)
async function validateWithServer(field, value) {
    try {
        const response = await fetch(`/api/validate/${field}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ [field.replace('-', '_')]: value })
        });

        const result = await response.json();
        return result.valid ? "" : result.message;
    } catch (error) {
        console.error('Erreur validation serveur:', error);
        return ""; // En cas d'erreur, on laisse la validation côté client
    }
}