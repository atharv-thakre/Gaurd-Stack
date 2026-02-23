const token = localStorage.getItem("token");
const statusBox = document.getElementById("status-message");
const sendOtpBtn = document.getElementById("sendOtpBtn");
const verifyForm = document.getElementById("verifyForm");

// 🔐 Redirect if not logged in
if (!token) {
    window.location.href = "/";
}

// 🔎 Check current user state
async function fetchMe() {
    try {
        const res = await fetch("/me", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.status === 401 || res.status === 403) {
            localStorage.removeItem("token");
            window.location.href = "/";
            return;
        }

        const data = await res.json();

        // If already active → go to dashboard
        if (data.is_active) {
            window.location.href = "/dashboard";
        }

    } catch (err) {
        console.error("FetchMe error:", err);
        window.location.href = "/";
    }
}

fetchMe();

// 📩 Send OTP
sendOtpBtn.addEventListener("click", async () => {
    statusBox.textContent = "Sending OTP...";

    try {
        const res = await fetch("/me/send-otp", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const data = await res.json();

        if (res.status === 401 || res.status === 403) {
            localStorage.removeItem("token");
            window.location.href = "/";
            return;
        }

        if (!res.ok) {
            statusBox.textContent = data.detail || "Failed to send OTP";
            return;
        }

        statusBox.textContent = "OTP sent to your email.";

    } catch (err) {
        console.error("Send OTP error:", err);
        statusBox.textContent = "Server error.";
    }
});

// ✅ Verify OTP & Activate
verifyForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(verifyForm);
    const otp = formData.get("otp");
    const phone = formData.get("phone");

    statusBox.textContent = "Verifying...";

    try {
        const res = await fetch("/me/activate", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                otp: otp,
                phone: phone || null
            })
        });

        const data = await res.json();

        if (res.status === 401 || res.status === 403) {
            localStorage.removeItem("token");
            window.location.href = "/";
            return;
        }

        if (!res.ok) {
            statusBox.textContent = data.detail || "Verification failed";
            return;
        }

        statusBox.textContent = "Account activated! Redirecting...";

        setTimeout(() => {
            window.location.href = "/dashboard";
        }, 1000);

    } catch (err) {
        console.error("Verify error:", err);
        statusBox.textContent = "Server error.";
    }
});