document.addEventListener('DOMContentLoaded', function() {
    const errorMessage = document.getElementById('error-message');
    if (errorMessage) {
        const observer = new MutationObserver(() => {
            if (!errorMessage.classList.contains('d-none')) {
                setTimeout(() => {
                    errorMessage.classList.add('d-none');
                }, 5000);
            }
        });

        observer.observe(errorMessage, { attributes: true, attributeFilter: ['class'] });
    }
});



document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const errorMessage = document.getElementById('error-message');
    const loginUrl = this.getAttribute('action');

    fetch(loginUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Invalid response');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            errorMessage.classList.remove('d-none');
            errorMessage.textContent = data.error;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});

