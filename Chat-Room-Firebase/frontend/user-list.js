// Configuration - API endpoint
const API_BASE_URL = 'http://localhost:8000';

// Get elements
const userList = document.getElementById('userList');
const totalUsers = document.getElementById('totalUsers');
const statusText = document.getElementById('statusText');

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
    const hue = username.charCodeAt(0) * 30 % 360;
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
        const response = await fetch(`${API_BASE_URL}/users`);
        
        if (!response.ok) {
            if (response.status === 404) {
                // Endpoint doesn't exist yet, show message
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
        
        // Update stats
        totalUsers.textContent = users.length;
        statusText.textContent = users.length > 0 ? 'Active' : 'Idle';
        
        // Render users list
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

// Load users on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    // Refresh every 5 seconds
    setInterval(loadUsers, 5000);
});
