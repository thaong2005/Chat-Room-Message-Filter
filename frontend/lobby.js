const API_BASE_URL = "http://localhost:8000";

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
    loadRooms();
    setupSearch();
});

async function loadRooms() {
    const roomsList = document.getElementById('rooms-list');
    roomsList.innerHTML = '';

    try {
        // Try to fetch from backend
        const response = await fetch(`${API_BASE_URL}/rooms`);
        if (!response.ok) throw new Error('Backend not available');
        
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

        roomItem.innerHTML = `
            <div class="room-info">
                <div class="room-icon" style="background: ${iconColor};">${iconLetter}</div>
                <div class="room-details">
                    <h3>${room.name}</h3>
                    <span>${room.description}</span>
                </div>
            </div>
            <div class="user-count">
                <div class="dot" style="background-color: ${statusColor};"></div>
                ${statusText} / ${room.max_users}
            </div>
        `;

        roomsList.appendChild(roomItem);
    });
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
