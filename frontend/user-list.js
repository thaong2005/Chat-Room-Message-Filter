// Configuration - API endpoint
const API_BASE_URL = 'http://localhost:8000';

// Get elements
const userList = document.getElementById('userList');
const totalUsers = document.getElementById('totalUsers');
const statusText = document.getElementById('statusText');

// Modal state
let pendingBanUserId = null;
let pendingBanUsername = null;
let pendingUnbanUserId = null;
let pendingUnbanUsername = null;

// Get current user role from token
function getCurrentUserRole() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    try {
        const decoded = JSON.parse(atob(token.split('.')[1]));
        return decoded.role;
    } catch {
        return null;
    }
}

// Format user initials for avatar
function getInitials(username) {
    return username
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
}

// Generate color from username
function getColorFromUsername(username) {
    const colors = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    ];
    const index = username.charCodeAt(0) % colors.length;
    return colors[index];
}

// Load all users
async function loadUsers() {
    try {
        const token = localStorage.getItem('token');
        const currentRole = getCurrentUserRole();

        if (!token) {
            userList.innerHTML = `
                <div class="empty-state">
                    <p>Not logged in</p>
                    <p style="font-size: 12px; margin-top: 10px;"><a href="index.html">Click here to login</a></p>
                </div>
            `;
            return;
        }

        const response = await fetch(`${API_BASE_URL}/users`, {
            method: "GET",
            headers: { "Authorization": "Bearer " + token }
        });

        if (!response.ok) {
            if (response.status === 404) {
                userList.innerHTML = `
                    <div class="empty-state">
                        <p>📭 No users available</p>
                        <p style="font-size: 12px; margin-top: 10px;">Users will appear here as they join chat rooms</p>
                    </div>
                `;
                totalUsers.textContent = '0';
                statusText.textContent = 'Ready';
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const users = data.users || data || [];

        totalUsers.textContent = users.length;
        statusText.textContent = users.length > 0 ? 'Active' : 'Idle';

        if (users.length === 0) {
            userList.innerHTML = `
                <div class="empty-state">
                    <p>📭 No users available</p>
                    <p style="font-size: 12px; margin-top: 10px;">Users will appear here as they join chat rooms</p>
                </div>
            `;
        } else {
            userList.innerHTML = users.map(user => `
                <div class="user-item">
                    <div class="user-avatar" style="background: ${getColorFromUsername(user.username || user.id)};">
                        ${getInitials(user.username || user.id)}
                    </div>
                    <div class="user-info">
                        <div class="user-username">
                            ${user.username || user.id}
                            ${user.role === 'admin' ? '<span class="user-status" style="background: #5865f2;"></span>' : '<span class="user-status"></span>'}
                        </div>
                        <div class="user-role">
                            ${user.role === 'admin' ? '👑 Admin' : user.is_banned ? '🚫 Banned' : '👤 User'}
                        </div>
                    </div>
                    ${currentRole === 'admin' ? `
                        <div class="user-actions">
                            <div class="actions-menu">
                                ${user.role !== 'admin' ? `
                                    ${user.is_banned
                                        ? `<button class="action-item success" onclick="showUnbanModal('${user.id}', '${user.username}')">
                                                ✅ Unban User
                                           </button>`
                                        : `<button class="action-item danger" onclick="showBanModal('${user.id}', '${user.username}')">
                                                🚫 Ban User
                                           </button>`
                                    }
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        userList.innerHTML = `
            <div class="message error">
                Failed to load users: ${error.message}
            </div>
        `;
        statusText.textContent = 'Error';
    }
}

// ── Ban modal ────────────────────────────────────────────
function showBanModal(userId, username) {
    pendingBanUserId = userId;
    pendingBanUsername = username;
    document.getElementById('banUsername').textContent = username;
    document.getElementById('banModal').classList.add('show');
}

function closeBanModal() {
    document.getElementById('banModal').classList.remove('show');
    pendingBanUserId = null;
    pendingBanUsername = null;
}

async function confirmBanUser() {
    if (!pendingBanUserId) return;

    try {
        const token = localStorage.getItem('token');

        const response = await fetch(`${API_BASE_URL}/users/${pendingBanUserId}/ban`, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        alert(`${pendingBanUsername} has been banned.`);
        closeBanModal();
        loadUsers();
    } catch (error) {
        console.error('Error banning user:', error);
        alert('Error: ' + error.message);
    }
}

// ── Unban modal ──────────────────────────────────────────
function showUnbanModal(userId, username) {
    pendingUnbanUserId = userId;
    pendingUnbanUsername = username;
    document.getElementById('unbanUsername').textContent = username;
    document.getElementById('unbanModal').classList.add('show');
}

function closeUnbanModal() {
    document.getElementById('unbanModal').classList.remove('show');
    pendingUnbanUserId = null;
    pendingUnbanUsername = null;
}

async function confirmUnbanUser() {
    if (!pendingUnbanUserId) return;

    try {
        const token = localStorage.getItem('token');

        const response = await fetch(`${API_BASE_URL}/users/${pendingUnbanUserId}/unban`, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        alert(`${pendingUnbanUsername} has been unbanned.`);
        closeUnbanModal();
        loadUsers();
    } catch (error) {
        console.error('Error unbanning user:', error);
        alert('Error: ' + error.message);
    }
}

// Load users on page load
document.addEventListener('DOMContentLoaded', () => {
    const token = requireAuth();
    if (!token) return;

    loadUsers();
    setInterval(loadUsers, 5000);
});