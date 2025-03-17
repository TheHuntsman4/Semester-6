document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');

    // Simple function to show error
    function showError(input, message) {
        const errorElement = document.getElementById(`${input.id}Error`);
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    // Form submission handler
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let isValid = true;

        // Name validation
        const name = document.getElementById('name');
        if (!name.value.trim()) {
            showError(name, 'Name is required');
            isValid = false;
        } else if (name.value.length < 2) {
            showError(name, 'Name must be at least 2 characters');
            isValid = false;
        }

        // Email validation
        const email = document.getElementById('email');
        if (!email.value.trim()) {
            showError(email, 'Email is required');
            isValid = false;
        } else if (!email.value.includes('@')) {
            showError(email, 'Please enter a valid email');
            isValid = false;
        }

        // Message validation
        const message = document.getElementById('message');
        if (!message.value.trim()) {
            showError(message, 'Message is required');
            isValid = false;
        } else if (message.value.length < 10) {
            showError(message, 'Message must be at least 10 characters');
            isValid = false;
        }

        // Country validation
        const country = document.getElementById('country');
        if (!country.value) {
            showError(country, 'Please select a country');
            isValid = false;
        }

        if (isValid) {
            console.log('Form is valid, submitting...');
            // form.submit();
        }
    });
});