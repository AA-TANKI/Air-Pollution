document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    // Clear previous error message
    document.getElementById('error-message').textContent = '';

    // Get form values
    const username = document.getElementById('username').value.trim();
    const countryName = document.getElementById('countryName').value.trim();
    const age = document.getElementById('age').value.trim();

    // Simple validation
    if (!username || !countryName || !age) {
        document.getElementById('error-message').textContent = 'All fields are required!';
        return;
    }

    // Validate age
    const ageNumber = parseInt(age, 10);
    if (isNaN(ageNumber) || ageNumber < 1 || ageNumber > 120) {
        document.getElementById('error-message').textContent = 'Please enter a valid age between 1 and 120.';
        return;
    }

    // Dummy validation (you can add more complex checks here)
    if (username.length >= 3 && countryName.length > 0) {
        alert(`Login successful!\nUsername: ${username}\nCountry Name: ${countryName}\nAge: ${ageNumber}`);
    } else {
        document.getElementById('error-message').textContent = 'Invalid username or country name!';
    }
});
