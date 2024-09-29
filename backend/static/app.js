// JavaScript for form validation and password toggle
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const errorMessage = document.getElementById('error-message');
const togglePassword = document.getElementById('toggle-password');

loginForm.addEventListener('submit', function(e) {
    e.preventDefault();  // Prevent form submission

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!validateInput(username, password)) {
        displayError('Please fill in both fields.');
        return;
    }

    // Dummy credentials validation (you can replace this with backend authentication)
    if (username === 'admin' && password === 'password123') {
        displayError('');  // Clear any previous error
        alert('Login successful!');
        // Redirect to dashboard or other page
        window.location.href = "dashboard.html";  // Example
    } else {
        displayError('Invalid username or password.');
    }
});

function validateInput(username, password) {
    return username !== '' && password !== '';
}

function displayError(message) {
    errorMessage.textContent = message;
}

// Password visibility toggle functionality
togglePassword.addEventListener('click', function() {
    // Toggle the password field type
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);

    // Toggle the eye icon
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
});