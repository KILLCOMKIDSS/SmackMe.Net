document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message');
    const messages = document.getElementById('messages');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = input.value;
        if (message.trim()) {
            socket.emit('message', { message }); // Emit 'message' event to server
            input.value = '';
        }
    });

    socket.on('message', (data) => {
        const { username, message } = data;
        const msgElement = document.createElement('div');
        msgElement.classList.add('message');
        msgElement.innerHTML = `<span class="username">${username}</span>: <span class="text">${message}</span>`;
        messages.appendChild(msgElement);
        messages.scrollTop = messages.scrollHeight;
    });
});

