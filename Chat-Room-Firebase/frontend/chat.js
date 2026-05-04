const API_BASE_URL = "http://localhost:8000";

let currentUser = null;
let currentRoom = null;
let unsubscribe = null;

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

    // Load existing messages and listen for new ones using Firestore Realtime
    listenForMessages(roomId);

    // Handle form submission
    chatForm.onsubmit = async function(e) {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (text) {
            await sendMessageViaAPI(roomId, text);
            messageInput.value = '';
        }
    };

    // Listen to Firebase directly for real-time updates
    function listenForMessages(roomId) {
        if (typeof firebase === 'undefined' || firebase.apps.length === 0) {
            // Fallback if Firebase isn't configured
            console.warn("Firebase not configured. Listening via HTTP proxy is not implemented. Please setup firebase-config.js.");
            addMessageToUI('System', 'Firebase is not initialized. Please configure it.', false);
            return;
        }

        const db = firebase.firestore();
        
        unsubscribe = db.collection('messages')
            .where('room_id', '==', roomId)
            .orderBy('timestamp', 'asc')
            .onSnapshot((snapshot) => {
                snapshot.docChanges().forEach((change) => {
                    if (change.type === 'added') {
                        const msg = change.doc.data();
                        addMessageToUI(msg.username, msg.text, msg.is_filtered);
                    }
                });
            }, (error) => {
                console.error("Error listening to Firestore:", error);
                addMessageToUI('Error', 'Failed to read real-time messages', false);
            });
            
        addMessageToUI('System', `${currentUser.username} joined the real-time room`, false);
    }

    // Send message via REST API (which filters it and saves to Firebase)
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

            if (!response.ok) {
                const res = await response.json();
                addMessageToUI('Error', res.detail || 'Could not send message', false);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessageToUI('Error', 'Network Error', false);
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
    
    window.addEventListener('beforeunload', () => {
        if (unsubscribe) unsubscribe();
    });
});
