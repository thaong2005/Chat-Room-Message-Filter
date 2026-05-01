const API_BASE_URL = "http://localhost:8000";
const badwordBtn = document.getElementById('manage-badwords');
const createRoomBtn = document.getElementById('create-room');
const divider = document.getElementById('divider');

// Color palette for room icons
const iconColors = [
    "#5865f2",  // Discord Blurple
    "#e91e63",  // Pink
    "#f1c40f",  // Yellow
    "#1abc9c",  // Teal
    "#9b59b6",  // Purple
    "#e67e22",  // Orange
];

// Demo rooms if API is not available
const demoRooms = [
    {
        id: "room1",
        name: "Gaming Central",
        description: "Everything from RPGs to FPS",
        max_users: 100,
        current_users: 42,
        created_by: "admin"
    },
    {
        id: "room2",
        name: "Developers Den",
        description: "React, Python, and more",
        max_users: 50,
        current_users: 12,
        created_by: "admin"
    },
    {
        id: "room3",
        name: "Music Theory",
        description: "Sharing beats and vibes",
        max_users: 20,
        current_users: 8,
        created_by: "admin"
    },
    {
        id: "room4",
        name: "Art & Design",
        description: "Showcase your latest work",
        max_users: 60,
        current_users: 29,
        created_by: "admin"
    },
    {
        id: "room5",
        name: "Study Group",
        description: "Focused work only",
        max_users: 15,
        current_users: 5,
        created_by: "admin"
    },
    {
        id: "room6",
        name: "Cinema Talk",
        description: "Reviewing the latest hits",
        max_users: 40,
        current_users: 0,
        created_by: "admin"
    }
];

document.addEventListener('DOMContentLoaded', function() {
    // check if user is logged in 
    const token = requireAuth();
    if (!token) {
        return;
    }

    // manage bad words for admin only
    const role = localStorage.getItem('role');
    if (role != 'admin') {
        createRoomBtn.style.display = "none";
        badwordBtn.style.display = "none";
        divider.style.display = "none";
    }

    loadRooms();
    setupSearch();

    createRoomBtn.addEventListener('click', function() {
        addRoom();
    })
});

async function loadRooms() {
    const roomsList = document.getElementById('rooms-list');
    roomsList.innerHTML = '';
    const token = localStorage.getItem('token');
    console.log("Token:", token);

    
    try {
        // Try to fetch from backend

        const response = await fetch(`${API_BASE_URL}/rooms`, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        if (response.status === 401) {
            logout(); // token expired, log out user
            return;
        }

        if (!response.ok) throw new Error();
        
        const rooms = await response.json();
        if (rooms.length === 0) {
            // If no rooms from backend, use demo rooms
            renderRooms(demoRooms);
        } else {
            renderRooms(rooms);
        }
    } catch (error) {
        console.warn('Backend not available, using demo rooms:', error);
        // Use demo rooms if backend is not available
        renderRooms(demoRooms);
    }
}

function renderRooms(rooms) {
    const roomsList = document.getElementById('rooms-list');
    roomsList.innerHTML = '';
    const role = localStorage.getItem('role');

    rooms.forEach((room, index) => {
        const roomItem = document.createElement('a');
        roomItem.href = `chat.html?room=${room.id}&roomName=${encodeURIComponent(room.name)}`;
        roomItem.className = 'room-item';

        // Get icon letter and color
        const iconLetter = room.name.charAt(0).toUpperCase();
        const iconColor = iconColors[index % iconColors.length];

        // Determine if room is full
        const isFull = room.current_users >= room.max_users;
        const statusColor = isFull ? '#80848e' : '#23a55a';
        const statusText = isFull ? 'FULL' : room.current_users;

        const adminMenu = role === "admin" ? `
            <div class="room-menu-container" onclick="event.preventDefault(); event.stopPropagation();">
                <button class="room-menu-btn" onclick="toggleRoomMenu('menu-${room.id}')">⋮</button>
                <div class="room-dropdown" id="menu-${room.id}">
                    <button onclick="deleteRoom('${room.id}', '${room.name}')">🗑️ Delete Room</button>
                </div>
            </div>
        `: "";

        roomItem.innerHTML = `
            <div class="room-info">
                <div class="room-icon" style="background: ${iconColor};">${iconLetter}</div>
                <div class="room-details">
                    <h3>${room.name}</h3>
                    <span>${room.description}</span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div class="user-count">
                    <div class="dot" style="background-color: ${statusColor};"></div>
                    ${statusText} / ${room.max_users}
                </div>
                ${adminMenu}
            </div>  
        `;

        roomsList.appendChild(roomItem);

        document.addEventListener('click', function() {
            document.querySelectorAll('.room-dropdown').forEach(d => d.classList.remove('active'));
        });        
    });
}

function toggleRoomMenu(menuId) {
    document.querySelectorAll('.room-dropdown').forEach(d => {
        if (d.id !== menuId) d.classList.remove('active');
    });
    document.getElementById(menuId).classList.toggle('active');
}

async function deleteRoom(roomId, roomName) {
    // Close the dropdown
    document.querySelectorAll('.room-dropdown').forEach(d => d.classList.remove('active'));

    if (!confirm(`Are you sure you want to delete "${roomName}"? This cannot be undone.`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/rooms/${roomId}`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (response.status === 403) {
            alert("Failed to delete room. Admin privilege required.")
            return;
        }
        
        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Failed to create room");
            return
        }

        // reload rooms
        alert("Deleted room successfully!");
        loadRooms();
    } catch (error) {
        alert("Could not connect to server");
        return;
    }
}

function setupSearch() {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const roomItems = document.querySelectorAll('.room-item');

        roomItems.forEach(item => {
            const roomName = item.querySelector('h3').textContent.toLowerCase();
            const roomDesc = item.querySelector('span').textContent.toLowerCase();

            if (roomName.includes(searchTerm) || roomDesc.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// Open modal
function openCreateRoomModal() {
    document.getElementById('createRoomModal').style.display = 'flex';
    document.getElementById('roomName').value = '';
    document.getElementById('roomDescription').value = '';
    document.getElementById('roomMaxUsers').value = '';
    document.getElementById('createRoomError').style.display = 'none';
    document.getElementById('roomName').focus();
}

// Close modal
function closeCreateRoomModal() {
    document.getElementById('createRoomModal').style.display = 'none';
}

// Close modal when clicking outside the box
document.getElementById('createRoomModal').addEventListener('click', function(e) {
    if (e.target === this) closeCreateRoomModal();
});


// submit create room
async function submitCreateRoom() {
    const name = document.getElementById('roomName').value.trim();
    const description = document.getElementById('roomDescription').value.trim();
    const maxUsers = parseInt(document.getElementById('roomMaxUsers').value);
    const errorDiv = document.getElementById('createRoomError');
    const submitBtn = document.getElementById('createRoomSubmitBtn');
    
    errorDiv.style.display = 'none';
    
    if (!name) { showCreateRoomError('Room name is required.'); return; }
    if (!description) { showCreateRoomError('Description is required.'); return; }
    if (!maxUsers || maxUsers < 2 || maxUsers > 100) { showCreateRoomError('Max users must be between 2 and 100.'); return; }
    
    submitBtn.textContent = "Creating...";
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/rooms`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                id: crypto.randomUUID(), // generate unique id
                name: name,
                description: description,
                max_users: maxUsers,
                current_users: 0,
                created_by: localStorage.getItem('username')
            })
        });

        const data = await response.json();
        
        // check if logged in
        if (response.status === 401) {
            logout();
            return;
        }

        // check if user is admin
        if (response.status === 403) {
            showCreateRoomError("This action failed. Requires admin privilege to complete.");
            return;
        }

        if(!response.ok) {
            showCreateRoomError("Failed to create room");
            return;
        }
        
        
        // if successful
        closeCreateRoomModal();
        loadRooms();
        
    } catch (error) {
        showCreateRoomError("Could not connect to server.");
    } finally {
        submitBtn.textContent = "Create Room";
        submitBtn.disabled = false;
    }
}

function showCreateRoomError(msg) {
    const errorDiv = document.getElementById('createRoomError');
    errorDiv.textContent = msg;
    errorDiv.style.display = 'block';
}

function addRoom() {
    openCreateRoomModal();
}