function toggleChatbot() {
    let chatbot = document.getElementById("chatbot-container");
    chatbot.style.display = chatbot.style.display === "flex" ? "none" : "flex";
}

async function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return;

    let messagesContainer = document.getElementById("chatbot-messages");

    // Display user message
    let userMessage = document.createElement("div");
    userMessage.className = "message user-message";
    userMessage.textContent = userInput;
    messagesContainer.appendChild(userMessage);

    document.getElementById("user-input").value = "";

    // Call AI API (Gemini/GPT)
    let aiResponse = await getAIResponse(userInput);

    // Display AI Response
    let aiMessage = document.createElement("div");
    aiMessage.className = "message bot-message";
    aiMessage.textContent = aiResponse;
    messagesContainer.appendChild(aiMessage);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function getAIResponse(message) {
    // Replace with real AI API request
    const response = await fetch('/chatbot_api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();
    return data.reply || "Sorry, I couldn't understand that.";
}