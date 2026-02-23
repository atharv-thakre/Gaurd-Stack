const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "/";
}

async function apiRequest(url, method = "GET", body = null) {
    const options = {
        method: method,
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("token");
        window.location.href = "/";
        return;
    }

    return response.json();
}

async function loadUsers() {
    const data = await apiRequest("/admin/users");
    document.getElementById("usersOutput").textContent = JSON.stringify(data, null, 2);
}

async function getUser() {
    const uid = document.getElementById("getUid").value;
    const data = await apiRequest(`/admin/users/${uid}`);
    document.getElementById("singleUserOutput").textContent = JSON.stringify(data, null, 2);
}

async function updateUser() {
    const uid = document.getElementById("updateUid").value;
    const role = document.getElementById("updateRole").value;
    const is_active = document.getElementById("updateActive").value;

    const body = {};
    if (role) body.role = role;
    if (is_active !== "") body.is_active = parseInt(is_active);

    const data = await apiRequest(`/admin/users/${uid}`, "PUT", body);
    document.getElementById("updateOutput").textContent = JSON.stringify(data, null, 2);
}

async function deleteUser() {
    const uid = document.getElementById("deleteUid").value;
    const data = await apiRequest(`/admin/users/${uid}`, "DELETE");
    document.getElementById("deleteOutput").textContent = JSON.stringify(data, null, 2);
}

async function createUser() {
    const email = document.getElementById("newEmail").value;
    const password = document.getElementById("newPassword").value;
    const role = document.getElementById("newRole").value;

    const body = {
        email,
        password,
        role: role || "user"
    };

    const data = await apiRequest("/admin/users", "POST", body);
    document.getElementById("createOutput").textContent = JSON.stringify(data, null, 2);
}

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "/";
});