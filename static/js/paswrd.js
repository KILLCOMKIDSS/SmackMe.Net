document.getElementById('passwordCheckerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const strengthResult = document.getElementById('strengthResult');
    
    const response = await fetch('/check_password_strength', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });

    const result = await response.json();
    strengthResult.innerHTML = `Password Strength: ${result.strength}`;
});

