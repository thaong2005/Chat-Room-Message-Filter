function requireAuth() {
    const token = localStorage.getItem('token');

    if (!token) {
        window.location.href = "/loginPage.html";
        return null;
    }

    return token;
}


function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    };
}

function logout() {
    localStorage.clear();
    window.location.href = "/loginPage.html";
}