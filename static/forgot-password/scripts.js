const forgotForm = document.getElementById('forgot-form');
const resetForm = document.getElementById('reset-form');
const statusMsg = document.getElementById('status-msg');

let userEmail = ""; // Store email to use in second request

// Step 1: Request OTP
forgotForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    userEmail = document.getElementById('email').value;
    
    try {
        const response = await fetch('/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: userEmail })
        });

        const result = await response.json();

        if (response.ok) {
            showMessage(result.message, "success");
            forgotForm.classList.add('hidden');
            resetForm.classList.remove('hidden');
        } else {
            showMessage(result.detail || "Something went wrong", "error");
        }
    } catch (err) {
        showMessage("Connection failed", "error");
    }
});

// Step 2: Verify OTP & Reset Password
resetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const otp = document.getElementById('otp').value;
    const newPassword = document.getElementById('new-password').value;

    try {
        const response = await fetch('/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email: userEmail, 
                otp: otp, 
                new_password: newPassword 
            })
        });

        const result = await response.json();

        if (response.ok) {
            showMessage("Success! Redirecting...", "success");
            setTimeout(() => {
                window.location.href = "/"; // Redirect to home/login
            }, 2000);
        } else {
            showMessage(result.detail || "Invalid OTP or request", "error");
        }
    } catch (err) {
        showMessage("Update failed", "error");
    }
});

function showMessage(text, type) {
    statusMsg.innerText = text;
    statusMsg.className = `message ${type}`;
}