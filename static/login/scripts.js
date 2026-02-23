const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});


// Select Forms
const signUpForm = document.querySelector('.sign-up form');
const signInForm = document.querySelector('.sign-in form');


// 🔹 SIGN UP
signUpForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = signUpForm.querySelector('input[type="text"]').value;
    const email = signUpForm.querySelector('input[type="email"]').value;
    const password = signUpForm.querySelector('input[type="password"]').value;

    try {
        const response = await fetch("http://localhost:8000/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                password,
                name
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert("❌ " + data.detail);
            return;
        }

        alert("✅ User registered! Please login.");
        container.classList.remove("active");

    } catch (err) {
        alert("❌ Server error");
        console.error(err);
    }
});


// 🔹 SIGN IN
signInForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = signInForm.querySelector('input[type="email"]').value;
    const password = signInForm.querySelector('input[type="password"]').value;

    try {
        const response = await fetch("http://localhost:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail);
            return;
        }

        localStorage.setItem("token", data.access_token);

        // Redirect to protected dashboard
        window.location.href = "/dashboard";

    } catch (err) {
        alert("❌ Server error");
        console.error(err);
    }
});