/**
 * Student Support Assistant — Chat Client JS
 * Handles message sending, rendering, and UI interactions.
 */

// ── State ──────────────────────────────────────────────
const sessionId = sessionStorage.getItem('chat_session_id') || generateSessionId();
sessionStorage.setItem('chat_session_id', sessionId);

let isWaiting = false;

// ── DOM Elements ───────────────────────────────────────
const messagesContainer = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const typingIndicator = document.getElementById('typing-indicator');
const clearButton = document.getElementById('clear-button');
const welcomeCard = document.getElementById('welcome-card');

// ── Helpers ────────────────────────────────────────────

function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).slice(2, 9);
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  });
}

function autoResizeInput() {
  messageInput.style.height = 'auto';
  messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

function setWaiting(waiting) {
  isWaiting = waiting;
  sendButton.disabled = waiting;
  messageInput.disabled = waiting;

  if (waiting) {
    typingIndicator.classList.add('active');
  } else {
    typingIndicator.classList.remove('active');
  }
  scrollToBottom();
}

function hideWelcomeCard() {
  if (welcomeCard) {
    welcomeCard.style.display = 'none';
  }
}

// ── Markdown Rendering ─────────────────────────────────

function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    marked.setOptions({
      breaks: true,
      gfm: true,
    });
    return marked.parse(text);
  }
  // Fallback: simple line-break conversion
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}

// ── Message Rendering ──────────────────────────────────

function addMessage(role, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = role === 'user' ? '🧑‍🎓' : '🤖';

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';

  if (role === 'assistant') {
    contentDiv.innerHTML = renderMarkdown(content);
  } else {
    contentDiv.textContent = content;
  }

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(contentDiv);

  // Insert before the typing indicator
  messagesContainer.insertBefore(messageDiv, typingIndicator);
  scrollToBottom();
}

// ── API Calls ──────────────────────────────────────────

async function sendMessage(text) {
  if (!text.trim() || isWaiting) return;

  hideWelcomeCard();
  addMessage('user', text.trim());

  messageInput.value = '';
  messageInput.style.height = 'auto';
  setWaiting(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text.trim(),
        session_id: sessionId,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      addMessage('assistant', data.response);
    } else {
      addMessage('assistant', `⚠️ Error: ${data.error || 'Something went wrong. Please try again.'}`);
    }
  } catch (error) {
    addMessage('assistant', '⚠️ Could not connect to the server. Please make sure the Flask server is running.');
    console.error('Chat error:', error);
  } finally {
    setWaiting(false);
    messageInput.focus();
  }
}

async function clearHistory() {
  try {
    await fetch('/api/clear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });

    // Remove all messages from the UI (keep typing indicator)
    const messages = messagesContainer.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());

    // Show welcome card again
    if (welcomeCard) {
      welcomeCard.style.display = '';
    }
  } catch (error) {
    console.error('Clear error:', error);
  }
}

// ── Quick Actions ──────────────────────────────────────

function sendQuickAction(text) {
  messageInput.value = text;
  sendMessage(text);
}

// ── Event Listeners ────────────────────────────────────

// Send button click
sendButton.addEventListener('click', () => {
  sendMessage(messageInput.value);
});

// Enter key to send, Shift+Enter for new line
messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage(messageInput.value);
  }
});

// Auto-resize textarea
messageInput.addEventListener('input', autoResizeInput);

// Clear button
if (clearButton) {
  clearButton.addEventListener('click', clearHistory);
}

// Quick action buttons
document.querySelectorAll('.quick-action-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    sendQuickAction(btn.dataset.query);
  });
});

// Welcome topic cards
document.querySelectorAll('.welcome-topic').forEach(card => {
  card.addEventListener('click', () => {
    sendQuickAction(card.dataset.query);
  });
});

// Focus input on page load
window.addEventListener('DOMContentLoaded', () => {
  messageInput.focus();
});
