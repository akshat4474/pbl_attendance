// JavaScript for form validation and password toggle
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form'); // Register form
const usernameInput = document.getElementById('username');
const errorMessage = document.getElementById('error-message');
const messageElement = document.getElementById('message');
const togglePassword = document.getElementById('toggle-password');
const registerUsernameInput = document.getElementById('register-username');
const registerTogglePassword = document.getElementById('register-toggle-password');
const loginTogglePassword = document.getElementById('login-toggle-password');
const loginPasswordInput = document.getElementById('password');
const registerPasswordInput = document.getElementById('register-password');


// Handle login form submission
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();  // Prevent form submission

        const username = usernameInput.value.trim();
        const password = loginPasswordInput.value.trim(); // Use loginPasswordInput instead of passwordInput

        if (!validateInput(username, password)) {
            displayError('Please fill in both fields.');
            return;
        }

        // Dummy credentials validation (replace with backend authentication)
        const xhr = new XMLHttpRequest();
        xhr.open("POST", loginForm.action, true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = xhr.responseText;
                if (response === 'success') {
                    window.location.href = "dashboard.html"; // Redirect on success
                } else {
                    displayError(response); // Show error message
                }
            }
        };

        xhr.send(`username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`);
    });
}

// Handle register form submission
if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();  // Prevent form submission
        const username = registerUsernameInput.value.trim();  
        const password = registerPasswordInput.value.trim();  

        if (!validateInput(username, password)) {
            displayError('Please fill in both fields.');
            return;
        }

        // Register user logic
        const xhr = new XMLHttpRequest();
        xhr.open("POST", registerForm.action, true); 
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.message === 'Registration successful!') {
                    displaySuccessMessage(response.message);  // Display success message
                    setTimeout(() => {
                        window.location.href = "/"; // Redirect to login page on success
                    }, 2000); // Redirect after 2 seconds for user to see the message
                } else {
                    displayError(response.message); // Show error message
                }
            } else if (xhr.status === 400) {
                const response = JSON.parse(xhr.responseText);
                displayError(response.message); // Show error message
            } else {
                displayError('An error occurred. Please try again.'); // Handle error response
            }
        };

        xhr.send(`username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`);
    });
}

// Function to display success message
function displaySuccessMessage(message) {
    const successMessageElement = document.getElementById('success-message');
    if (successMessageElement) {
        successMessageElement.textContent = message;
    }
}

// Function to display error message
function displayError(message) {
    const errorMessageElement = document.getElementById('error-message');
    if (errorMessageElement) {
        errorMessageElement.textContent = message;
    }
}

// Common validation function
function validateInput(username, password) {
    return username !== '' && password !== '';
}

function displayError(message) {
    errorMessage.textContent = message;
}



// Password visibility toggle functionality
function togglePasswordVisibility(toggleButton, passwordInput) {
    toggleButton.addEventListener('click', function() {
        // Toggle the password field type
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);

        // Toggle the eye icon
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });
}



if (loginTogglePassword && loginPasswordInput) {
    togglePasswordVisibility(loginTogglePassword, loginPasswordInput);
}

if (registerTogglePassword && registerPasswordInput) {
    togglePasswordVisibility(registerTogglePassword, registerPasswordInput);
}