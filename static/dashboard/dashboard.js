const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "/";
}


async function fetchWithAuth(url, options = {}) {
    options.headers = {
        ...(options.headers || {}),
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };

    const response = await fetch(url, options);

    if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("token");
        window.location.href = "/";
        return null;
    }

    return response;
}

async function loadUser() {
    const response = await fetchWithAuth("/me");
    if (!response) return;

    const data = await response.json();

    if (!data.is_active) {
        window.location.href = "/complete-profile";
        return;
    }

    document.getElementById("welcome").textContent =
        `Welcome, ${data.email}`;

    document.getElementById("email").textContent = data.email;
    document.getElementById("role").textContent = data.role;
    document.getElementById("name").textContent = data.name || "—";
    document.getElementById("phone").textContent = data.phone || "—";
    document.getElementById("status").textContent =
        data.is_active ? "Active" : "Inactive";

    if (data.role === "admin") {
        document.getElementById("adminSection").classList.remove("hidden");
    }
}

async function updateProfile() {
    const name = document.getElementById("updateName").value;
    const phone = document.getElementById("updatePhone").value;

    const body = {};
    if (name) body.name = name;
    if (phone) body.phone = phone;

    const response = await fetchWithAuth("/me", {
        method: "PUT",
        body: JSON.stringify(body)
    });

    if (!response) return;

    const data = await response.json();
    document.getElementById("updateMessage").textContent =
        data.message || "Profile updated";

    loadUser();
}

async function changePassword() {
    const oldPassword = document.getElementById("oldPassword").value;
    const newPassword = document.getElementById("newPassword").value;

    const response = await fetchWithAuth("/me/password", {
        method: "PUT",
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword
        })
    });

    if (!response) return;

    const data = await response.json();
    document.getElementById("passwordMessage").textContent =
        data.message || "Password changed";

    document.getElementById("oldPassword").value = "";
    document.getElementById("newPassword").value = "";
}

function goToAdmin() {
    window.location.href = "/admin";
}

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "/";
});

loadUser();