document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.type !== 'hidden' && input.type !== 'submit') {
            input.classList.add('form-control');
        }
    });

    const helpTexts = document.querySelectorAll('.helptext');
    helpTexts.forEach(helpText => {
        helpText.style.display = 'none';
    });

    const passwordInput = document.querySelector('#id_password1');
    
    const checklist = {
        length: document.querySelector('#length'),
        uppercase: document.querySelector('#uppercase'),
        lowercase: document.querySelector('#lowercase'),
        number: document.querySelector('#number'),
        special: document.querySelector('#special')
    };

    if (passwordInput) {
        const validatePassword = function() {
            const password = passwordInput.value;

            checklist.length.classList.toggle('valid', password.length >= 8);

            checklist.uppercase.classList.toggle('valid', /[A-Z]/.test(password));

            checklist.lowercase.classList.toggle('valid', /[a-z]/.test(password));

            checklist.number.classList.toggle('valid', /[0-9]/.test(password));

            checklist.special.classList.toggle('valid', /[^A-Za-z0-9]/.test(password));
        };

        passwordInput.addEventListener('input', validatePassword);
    }
});
