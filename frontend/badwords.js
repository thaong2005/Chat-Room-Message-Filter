const API_BASE_URL = 'http://localhost:8000';

const badWordsList = document.getElementById('badWordsList');
const addBadWordForm = document.getElementById('addBadWordForm');
const newBadWordInput = document.getElementById('newBadWord');
const searchInput = document.getElementById('searchBadWord');
const statusMessage = document.getElementById('statusMessage');
const totalCount = document.getElementById('totalCount');
const badWordsCount = document.getElementById('badWordsCount');

// Lưu trữ danh sách gốc để search local không cần gọi API liên tục
let allBadWords = [];

function showMessage(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.style.display = 'block';
    // Mapping style dựa trên class bạn đã có trong HTML/CSS
    statusMessage.className = `message ${type}`; 
    
    if (type !== 'loading') {
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 4000);
    }
}

// Render danh sách ra UI
function renderUI(words) {
    totalCount.textContent = allBadWords.length;
    badWordsCount.textContent = words.length;

    if (words.length === 0) {
        badWordsList.innerHTML = `
            <div class="empty-state">
                <p>📭 ${allBadWords.length === 0 ? 'No invalid words found.' : 'No words match your search.'}</p>
            </div>
        `;
        return;
    }

    badWordsList.innerHTML = words.map(word => `
        <div class="word-row">
            <span class="word-chip">${word}</span>
            <button type="button" class="remove-btn" onclick="deleteBadWord('${word}')">
                Delete
            </button>
        </div>
    `).join('');
}

// 1. Load data
async function loadBadWords() {
    try {
        const token = localStorage.getItem('token');

        showMessage('Loading data...', 'loading');
        const response = await fetch(`${API_BASE_URL}/badwords`, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        allBadWords = data.bad_words || [];
        
        renderUI(allBadWords);
        showMessage(`✅ Loaded ${allBadWords.length} words`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showMessage(`❌ Error: ${error.message}`, 'error');
    }
}

// 2. Add word
async function addBadWord(word) {
    const trimmedWord = word.trim();
    if (!trimmedWord) {
        showMessage('⚠️ Please enter a word', 'error');
        return;
    }

    try {
        const token = localStorage.getItem('token');

        showMessage('⏳ Adding...', 'loading');
        const response = await fetch(`${API_BASE_URL}/badwords?word=${encodeURIComponent(trimmedWord)}`, {
            method: 'POST',
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Cannot add word');

        newBadWordInput.value = '';
        await loadBadWords(); // Reload lại để đồng bộ
        newBadWordInput.focus();
    } catch (error) {
        showMessage(`❌ ${error.message}`, 'error');
    }
}

// 3. Delete word
async function deleteBadWord(word) {
    if (!confirm(`Delete "${word}"?`)) return;
    
    try {
        const token = localStorage.getItem('token')

        showMessage('⏳ Deleting...', 'loading');
        const response = await fetch(`${API_BASE_URL}/badwords?word=${encodeURIComponent(word)}`, {
            method: 'DELETE',
            headers: {
                "Authorization": "Bearer " + token 
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Cannot delete word');
        }
        
        await loadBadWords();
    } catch (error) {
        showMessage(`❌ ${error.message}`, 'error');
    }
}

// 4. Live Search logic
searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allBadWords.filter(w => w.toLowerCase().includes(term));
    renderUI(filtered);
});

// Event Listeners
addBadWordForm.addEventListener('submit', (e) => {
    e.preventDefault();
    addBadWord(newBadWordInput.value);
});

document.addEventListener('DOMContentLoaded', loadBadWords);