const API_BASE_URL = "http://localhost:8000";
const WS_BASE_URL = "ws://localhost:8000";

let currentUser = null;
let currentRoom = null;
let ws = null;

document.addEventListener('DOMContentLoaded', function() {
    const params = new URLSearchParams(window.location.search);
    const roomId = params.get('room') || 'room1';
    const roomName = params.get('roomName') || 'Room';
    
    // Setup current user (demo: use localStorage)
    currentUser = {
        id: localStorage.getItem('userId') || `user_${Math.random().toString(36).substr(2, 9)}`,
        username: localStorage.getItem('username') || `User_${Math.random().toString(36).substr(2, 5).toUpperCase()}`
    };
    localStorage.setItem('userId', currentUser.id);
    localStorage.setItem('username', currentUser.username);
    
    currentRoom = {
        id: roomId,
        name: roomName
    };

    document.getElementById('room-name').textContent = roomName;

    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');

    // Load existing messages from backend
    loadMessages(roomId);

    // Connect to WebSocket for real-time chat
    connectWebSocket(roomId);

    // Handle form submission
    chatForm.onsubmit = async function(e) {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (text) {
            // Send via WebSocket if connected
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ text: text }));
            } else {
                // Fallback: send via HTTP API
                await sendMessageViaAPI(roomId, text);
            }
            messageInput.value = '';
        }
    };

    // Load initial messages
    async function loadMessages(roomId) {
        try {
            const response = await fetch(`${API_BASE_URL}/rooms/${roomId}/messages?limit=50`);
            if (response.ok) {
                const messages = await response.json();
                messages.forEach(msg => {
                    addMessageToUI(msg.username, msg.text, msg.is_filtered);
                });
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            // Demo: load fake messages if API fails
            const demoMessages = [
                {user: 'Alice', text: 'Hello everyone!'},
                {user: 'Bob', text: 'Welcome to the chat!'},
            ];
            demoMessages.forEach(msg => addMessageToUI(msg.user, msg.text, false));
        }
    }

    // Connect to WebSocket
    function connectWebSocket(roomId) {
        const wsUrl = `${WS_BASE_URL}/ws/${roomId}/${currentUser.id}`;
        console.log('Connecting to WebSocket:', wsUrl);
        
        ws = new WebSocket(wsUrl);

        ws.onopen = function() {
            console.log('WebSocket connected');
            // Notify room that user joined
            addMessageToUI('System', `${currentUser.username} joined the room`, false);
        };

        ws.onmessage = function(event) {
            console.log('WebSocket message:', event.data);
            const data = JSON.parse(event.data);
            
            if (data.type === 'message') {
                const msg = data.message;
                addMessageToUI(msg.username, msg.text, msg.is_filtered);
            } else if (data.type === 'user_left') {
                addMessageToUI('System', `${data.username} left the room`, false);
            } else if (data.error) {
                addMessageToUI('Error', data.error, false);
            }
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            addMessageToUI('System', 'Connection error', false);
        };

        ws.onclose = function() {
            console.log('WebSocket disconnected');
            addMessageToUI('System', 'Connection closed', false);
        };
    }

    // Send message via REST API (fallback)
    async function sendMessageViaAPI(roomId, text) {
        try {
            const response = await fetch(`${API_BASE_URL}/rooms/${roomId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room_id: roomId,
                    user_id: currentUser.id,
                    username: currentUser.username,
                    text: text
                })
            });

            if (response.ok) {
                const result = await response.json();
                addMessageToUI(currentUser.username, result.data.text, result.was_filtered);
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    // Add message to UI
    function addMessageToUI(user, text, isFiltered = false) {
        const div = document.createElement('div');
        div.className = 'message';
        
        let userClass = '';
        if (user === 'System') {
            userClass = ' system';
        } else if (user === 'Error') {
            userClass = ' error';
        } else if (user === currentUser.username) {
            userClass = ' own';
        }
        
        let filterBadge = isFiltered ? ' <span class="filter-badge">⚠ Filtered</span>' : '';
        div.innerHTML = `<strong class="username${userClass}">${user}:</strong> ${text}${filterBadge}`;
        
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
