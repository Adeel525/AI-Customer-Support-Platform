interface ChatbotConfig {
  id: string;
  name: string;
  welcome_message: string;
  primary_color: string;
  theme: string;
  avatar_url?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  id?: string;
  confidence?: number;
}

class SupportAIWidget {
  private chatbotId: string;
  private apiUrl: string;
  private config: ChatbotConfig | null = null;
  private conversationId: string | null = null;
  private customerId: string;
  private messages: Message[] = [];
  private isOpen = false;
  private container: HTMLDivElement | null = null;

  constructor(chatbotId: string, apiUrl?: string) {
    this.chatbotId = chatbotId;
    this.apiUrl = apiUrl || "http://localhost:8000/api/v1";
    this.customerId = localStorage.getItem(`supportai_customer_${chatbotId}`) || this.generateId();
    localStorage.setItem(`supportai_customer_${chatbotId}`, this.customerId);
    this.conversationId = localStorage.getItem(`supportai_conv_${chatbotId}`);
    this.init();
  }

  private generateId(): string {
    return "cust_" + Math.random().toString(36).slice(2, 11);
  }

  private async init(): Promise<void> {
    try {
      const res = await fetch(`${this.apiUrl}/public/chat/${this.chatbotId}/config`);
      this.config = await res.json();
      this.render();
    } catch (e) {
      console.error("SupportAI Widget: Failed to load config", e);
    }
  }

  private render(): void {
    if (!this.config) return;
    const color = this.config.primary_color;

    this.container = document.createElement("div");
    this.container.id = "supportai-widget";
    this.container.innerHTML = `
      <style>
        #supportai-widget { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; position: fixed; bottom: 20px; right: 20px; z-index: 99999; }
        #supportai-btn { width: 56px; height: 56px; border-radius: 50%; background: ${color}; color: white; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; font-size: 24px; }
        #supportai-window { display: none; width: 380px; height: 520px; background: white; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); flex-direction: column; overflow: hidden; margin-bottom: 12px; }
        #supportai-window.open { display: flex; }
        #supportai-header { background: ${color}; color: white; padding: 16px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; }
        #supportai-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
        .sa-msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.4; }
        .sa-msg.user { align-self: flex-end; background: ${color}; color: white; }
        .sa-msg.assistant { align-self: flex-start; background: #f1f5f9; color: #1e293b; }
        .sa-typing { align-self: flex-start; padding: 10px; color: #94a3b8; font-size: 13px; }
        #supportai-input-area { padding: 12px; border-top: 1px solid #e2e8f0; display: flex; gap: 8px; }
        #supportai-input { flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; font-size: 14px; outline: none; }
        #supportai-send { background: ${color}; color: white; border: none; border-radius: 8px; padding: 8px 16px; cursor: pointer; font-size: 14px; }
        #supportai-escalate { background: none; border: none; color: ${color}; font-size: 12px; cursor: pointer; padding: 4px 16px; text-align: center; }
        .sa-feedback { display: flex; gap: 8px; padding: 4px 0; }
        .sa-feedback button { background: none; border: 1px solid #e2e8f0; border-radius: 4px; padding: 2px 8px; cursor: pointer; font-size: 12px; }
        @media (max-width: 480px) { #supportai-window { width: calc(100vw - 20px); height: calc(100vh - 100px); } }
      </style>
      <div id="supportai-window">
        <div id="supportai-header">
          <span>${this.config.name}</span>
          <button id="supportai-close" style="background:none;border:none;color:white;cursor:pointer;font-size:18px;">&times;</button>
        </div>
        <div id="supportai-messages"></div>
        <button id="supportai-escalate">Talk to a human agent</button>
        <div id="supportai-input-area">
          <input id="supportai-input" placeholder="Type your message..." />
          <button id="supportai-send">Send</button>
        </div>
      </div>
      <button id="supportai-btn">💬</button>
    `;

    document.body.appendChild(this.container);
    this.bindEvents();
    this.addMessage("assistant", this.config.welcome_message);
  }

  private bindEvents(): void {
    const btn = this.container!.querySelector("#supportai-btn")!;
    const close = this.container!.querySelector("#supportai-close")!;
    const send = this.container!.querySelector("#supportai-send")!;
    const input = this.container!.querySelector("#supportai-input") as HTMLInputElement;
    const escalate = this.container!.querySelector("#supportai-escalate")!;
    const window = this.container!.querySelector("#supportai-window")!;

    btn.addEventListener("click", () => {
      this.isOpen = !this.isOpen;
      window.classList.toggle("open", this.isOpen);
    });
    close.addEventListener("click", () => {
      this.isOpen = false;
      window.classList.remove("open");
    });
    send.addEventListener("click", () => this.sendMessage(input));
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.sendMessage(input);
    });
    escalate.addEventListener("click", () => this.escalate());
  }

  private async sendMessage(input: HTMLInputElement): Promise<void> {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    this.addMessage("user", text);
    this.showTyping();

    try {
      const res = await fetch(`${this.apiUrl}/public/chat/${this.chatbotId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          conversation_id: this.conversationId,
          customer_id: this.customerId,
        }),
      });
      const data = await res.json();
      this.hideTyping();
      this.conversationId = data.conversation_id;
      localStorage.setItem(`supportai_conv_${this.chatbotId}`, data.conversation_id);
      this.addMessage("assistant", data.content, data.message_id);
      if (data.should_escalate) {
        this.addMessage("assistant", "I've connected you with our support team. A ticket has been created.");
      }
    } catch {
      this.hideTyping();
      this.addMessage("assistant", "Sorry, I'm having trouble connecting. Please try again.");
    }
  }

  private async escalate(): Promise<void> {
    if (!this.conversationId) return;
    await fetch(`${this.apiUrl}/public/chat/${this.chatbotId}/escalate?conversation_id=${this.conversationId}`, {
      method: "POST",
    });
    this.addMessage("assistant", "A support agent will be with you shortly. A ticket has been created.");
  }

  private addMessage(role: "user" | "assistant", content: string, messageId?: string): void {
    const messagesEl = this.container!.querySelector("#supportai-messages")!;
    const div = document.createElement("div");
    div.className = `sa-msg ${role}`;
    div.textContent = content;
    messagesEl.appendChild(div);

    if (role === "assistant" && messageId) {
      const feedback = document.createElement("div");
      feedback.className = "sa-feedback";
      feedback.innerHTML = `<button data-rating="up" data-id="${messageId}">👍</button><button data-rating="down" data-id="${messageId}">👎</button>`;
      feedback.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", () => this.submitFeedback(messageId, btn.getAttribute("data-rating")!));
      });
      messagesEl.appendChild(feedback);
    }

    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  private async submitFeedback(messageId: string, thumbs: string): Promise<void> {
    await fetch(`${this.apiUrl}/public/chat/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_id: messageId, rating: thumbs === "up" ? 5 : 1, thumbs }),
    });
  }

  private showTyping(): void {
    const el = this.container!.querySelector("#supportai-messages")!;
    const typing = document.createElement("div");
    typing.className = "sa-typing";
    typing.id = "sa-typing";
    typing.textContent = "Typing...";
    el.appendChild(typing);
    el.scrollTop = el.scrollHeight;
  }

  private hideTyping(): void {
    this.container!.querySelector("#sa-typing")?.remove();
  }
}

function init(): void {
  const script = document.currentScript as HTMLScriptElement;
  const chatbotId = script?.getAttribute("data-chatbot-id");
  const apiUrl = script?.getAttribute("data-api-url");
  if (chatbotId) {
    new SupportAIWidget(chatbotId, apiUrl || undefined);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
