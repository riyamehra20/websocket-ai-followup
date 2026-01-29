let ws = null;
let followupCount = 0;

// Auto-detect WebSocket URL based on environment
function getWebSocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/ws`;
}

function setStatus(message, type = '') {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
}

function launchChat() {
    const initialInput = document.getElementById('initial-input').value.trim();
    
    if (!initialInput) {
        alert('Please enter a sentence');
        return;
    }
     
    
    document.getElementById('initial-section').classList.add('hidden');
    addMessage(initialInput, 'user');
    connectWebSocket(initialInput);
}

function connectWebSocket(initialMessage) {
    if (ws && ws.readyState === WebSocket.OPEN) return;
    const wsUrl = getWebSocketUrl();
    console.log('Connecting to:', wsUrl);
    setStatus('Connecting...', 'connecting');
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        setStatus('Connected ✓', 'connected');
        
        // Send initial message
        ws.send(JSON.stringify({
            type: 'initial',
            text: initialMessage
        }));
        
        setStatus('Waiting for AI response...', 'connecting');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
        
        if (data.type === 'followup') {
            // Display AI follow-up question
            addMessage(data.question, 'ai', data.number);
            
            // Show answer input
            document.getElementById('answer-section').classList.remove('hidden');
            document.getElementById('answer-input').focus();
            
            followupCount = data.number;
            setStatus(`Question ${data.number} of 3`, 'connected');
        } else if (data.type === 'complete') {
            // Display final message
            addMessage(data.message, 'final');
            
            // Hide answer input
            document.getElementById('answer-section').classList.add('hidden');
            
            setStatus('Conversation complete!', 'connected');
            
            // Close WebSocket
            setTimeout(() => {
                ws.close();
            }, 1000);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStatus('Connection error. Please refresh and try again.', 'error');
    };
    
    ws.onclose = () => {
        console.log('WebSocket closed');
        if (followupCount < 3) {
            setStatus('Connection closed', 'error');
        }
    };
}

function sendAnswer() {
    const answerInput = document.getElementById('answer-input');
    const answer = answerInput.value.trim();
    
    if (!answer) {
        alert('Please enter an answer');
        return;
    }
    
    // Display user's answer
    addMessage(answer, 'user');
    
    // Send to backend via WebSocket
    ws.send(JSON.stringify({
        type: 'answer',
        text: answer,
        followupNumber: followupCount
    }));
    
    // Clear input
    answerInput.value = '';
    
    // Hide answer section temporarily
    document.getElementById('answer-section').classList.add('hidden');
    
    setStatus('Waiting for AI response...', 'connecting');
}

function addMessage(text, type, followupNumber = null) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    
    if (type === 'user') {
        messageDiv.className = 'message user-message';
        messageDiv.textContent = text;
    } else if (type === 'ai') {
        messageDiv.className = 'message ai-message';
        
        const label = document.createElement('div');
        label.className = 'followup-label';
        label.textContent = `Follow-up #${followupNumber}`;
        
        messageDiv.appendChild(label);
        messageDiv.appendChild(document.createTextNode(text));
    } else if (type === 'final') {
        messageDiv.className = 'message final-message';
        messageDiv.textContent = '✨ ' + text + ' ✨';
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Allow Enter key to send
document.addEventListener('DOMContentLoaded', () => {
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendAnswer();
            }
        });
    }
    
    const initialInput = document.getElementById('initial-input');
    if (initialInput) {
        initialInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                launchChat();
            }
        });
    }
});

