async function saveUserInfo(event) {
    event.preventDefault();
    const nameInput = document.querySelector('input[name="name"]');
    const phoneInput = document.querySelector('input[name="phone"]');
    const name = nameInput.value.trim();
    const phone = phoneInput.value.trim();

    if (name && phone) {
        const response = await fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, phone: phone })
        });

        const responseData = await response.json();
        if (responseData.message) {
            document.getElementById('user-info-form').style.display = 'none';
            document.getElementById('chat-form').style.display = 'flex';
            addUserMessage(`Name: ${name}, Phone: ${phone} saved successfully.`);
        }
    }
}

function addUserMessage(message) {
    const messagesDiv = document.getElementById('messages');
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.textContent = message;
    messagesDiv.appendChild(userMessageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addBotMessage(message) {
    const messagesDiv = document.getElementById('messages');
    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot';
    botMessageDiv.textContent = message;
    messagesDiv.appendChild(botMessageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addBotTyping() {
    const messagesDiv = document.getElementById('messages');
    const botTypingDiv = document.createElement('div');
    botTypingDiv.id = 'bot-typing';
    botTypingDiv.className = 'message bot';
    botTypingDiv.textContent = 'The bot is typing...';
    messagesDiv.appendChild(botTypingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeBotTyping() {
    const botTypingDiv = document.getElementById('bot-typing');
    if (botTypingDiv) {
        botTypingDiv.remove();
    }
}

async function sendMessage(event) {
    event.preventDefault();
    const queryInput = document.querySelector('input[name="query"]');
    const userMessage = queryInput.value;
    if (userMessage.trim() === '') return;

    addUserMessage(userMessage);
    addBotTyping();
    queryInput.value = '';

    const response = await fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
    });

    const responseData = await response.json();
    removeBotTyping();
    addBotMessage(responseData.bot_response);
}
