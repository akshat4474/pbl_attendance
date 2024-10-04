// JavaScript for form validation and password toggle
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form'); // Register form
const usernameInput = document.getElementById('username');
const errorMessage = document.getElementById('error-message');
const messageElement = document.getElementById('message');
const togglePassword = document.getElementById('toggle-password');
const registerUsernameInput = document.getElementById('register-username');
const registerTogglePassword = document.getElementById('register-toggle-password');
const registerPasswordInput = document.getElementById('register-password');
const loginTogglePassword = document.getElementById('login-toggle-password');
const loginPasswordInput = document.getElementById('password');

// Get the role field from the form
const registerRoleInput = document.getElementById('role');

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

        const xhr = new XMLHttpRequest();
        xhr.open("POST", loginForm.action, true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.message === 'success') {
                    // Redirect to the admin dashboard if login is successful
                    window.location.href = "/admin_dashboard";
                } else if (response.message === 'passkey_required') {
                    // Redirect to the passkey validation page if passkey is required
                    window.location.href = "/passkey";
                } else {
                    displayError('Invalid login details.');
                }
            } else {
                displayError('An error occurred. Please try again.');
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
        const role = registerRoleInput.value;  // Get the selected role value

        if (!validateInput(username, password)) {
            displayError('Please fill in all fields.');
            return;
        }

        // Register user logic
        const xhr = new XMLHttpRequest();
        xhr.open("POST", registerForm.action, true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.message === "Registration successful! Please login") {
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

        // Send username, password, and role to the backend
        xhr.send(`username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&role=${encodeURIComponent(role)}`);
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


if (registerTogglePassword && registerPasswordInput) {
    togglePasswordVisibility(registerTogglePassword, registerPasswordInput);
}


// If the login toggle password and password input exist, apply the toggle functionality
if (loginTogglePassword && loginPasswordInput) {
    togglePasswordVisibility(loginTogglePassword, loginPasswordInput);
}

// Function to show the selected section and hide others
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.style.display = 'none');

    // Show the selected section
    const sectionToShow = document.getElementById(sectionId);
    if (sectionToShow) {
        sectionToShow.style.display = 'block';
    }
}

// Add click event listener for the "Role Management" button
document.querySelector('a[onclick="showSection(\'role-management\')"]').addEventListener('click', function() {
    showSection('role-management');
});

// Function to show the selected section and hide others
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.style.display = 'none');

    // Show the selected section
    const sectionToShow = document.getElementById(sectionId);
    if (sectionToShow) {
        sectionToShow.style.display = 'block';
    }
}

// Add event listeners for sidebar menu links to show sections
document.querySelector('a[onclick="showSection(\'profile\')"]').addEventListener('click', function() {
    showSection('profile');
});

document.querySelector('a[onclick="showSection(\'role-management\')"]').addEventListener('click', function() {
    showSection('role-management');
});

// Function to populate the users table with all users
function loadUsers() {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_users', true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            const users = JSON.parse(xhr.responseText);
            const tableBody = document.querySelector('#users-table tbody');

            // Clear any existing rows in the table
            tableBody.innerHTML = '';

            // Loop through the users and create rows
            users.forEach(user => {
                const row = document.createElement('tr');

                // Username cell
                const usernameCell = document.createElement('td');
                usernameCell.textContent = user[0]; // Username
                row.appendChild(usernameCell);

                // Current role cell
                const roleCell = document.createElement('td');
                roleCell.textContent = user[1]; // Current role
                row.appendChild(roleCell);

                // New role dropdown cell
                const roleSelectCell = document.createElement('td');
                const roleSelectWrapper = document.createElement('div'); // Create a div for input-group
                roleSelectWrapper.classList.add('input-group'); // Add the input-group class
                const roleSelect = document.createElement('select');
                roleSelect.innerHTML = `
                    <option value="student" ${user[1] === 'student' ? 'selected' : ''}>Student</option>
                    <option value="teacher" ${user[1] === 'teacher' ? 'selected' : ''}>Teacher</option>
                    <option value="admin" ${user[1] === 'admin' ? 'selected' : ''}>Admin</option>
                `;
                
                // Disable the dropdown if the username is 'admin'
                if (user[0] === 'admin') {
                    roleSelect.disabled = true; // Disable dropdown for admin
                }

                roleSelectWrapper.appendChild(roleSelect); // Append select to the wrapper
                roleSelectCell.appendChild(roleSelectWrapper); // Append wrapper to the cell
                row.appendChild(roleSelectCell);

                // Assign role button
                const assignButtonCell = document.createElement('td');
                const assignButton = document.createElement('button');
                assignButton.textContent = 'Assign Role';
                assignButton.classList.add('assign-role-btn');

                // Disable the assign button if the username is 'admin'
                if (user[0] === 'admin') {
                    assignButton.disabled = true; // Disable button for admin
                }

                assignButton.addEventListener('click', function () {
                    assignRole(user[0], roleSelect.value);  // Pass username and selected role
                });

                assignButtonCell.appendChild(assignButton);
                row.appendChild(assignButtonCell);

                // Append the row to the table body
                tableBody.appendChild(row);
            });
        }
    };

    xhr.send();
}


// Function to assign a role to a user
function assignRole(username, newRole) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/assign_role', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

    xhr.onload = function () {
        if (xhr.status === 200) {
            alert(`Role assigned to ${username}!`);
            loadUsers();  // Reload the users table after assigning role
        } else {
            alert('Failed to assign role. Please try again.');
        }
    };

    xhr.send(`username=${encodeURIComponent(username)}&role=${encodeURIComponent(newRole)}`);
}

// Load the users when the page loads or when Role Management is shown
document.querySelector('a[onclick="showSection(\'role-management\')"]').addEventListener('click', function () {
    showSection('role-management');
    loadUsers();  // Load users when Role Management section is shown
});

// Get the passkey form by ID
const passkeyForm = document.getElementById('passkey-form');
// Handle passkey form submission
if (passkeyForm) {
    passkeyForm.addEventListener('submit', function(e) {
        e.preventDefault();  // Prevent form submission

        const passkeyInput = document.getElementById('passkey').value.trim();

        if (!passkeyInput) {
            displayError('Please enter the passkey.');
            return;
        }

        const xhr = new XMLHttpRequest();
        xhr.open("POST", passkeyForm.action, true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onload = function () {
            if (xhr.status === 200) {
                // If status is 200, we assume a redirect will occur from the server
                window.location.href = "/admin_dashboard";  // Optional, in case the redirect is slow
            } else {
                displayError('Invalid passkey. Please try again.');
            }
        };

        xhr.send(`passkey=${encodeURIComponent(passkeyInput)}`);
    });
}


// Function to display error messages
function displayError(message) {
    const errorMessageElement = document.getElementById('error-message');
    if (errorMessageElement) {
        errorMessageElement.textContent = message;
    }
}

