import tkinter as tk
import customtkinter as ctk
import threading
from langchain.chat_models import init_chat_model

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

model = init_chat_model('llama3.2:1b', model_provider='ollama')


class ModernChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Assistant | Llama 3.2")
        self.geometry("800x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Chat Display Area
        self.chat_area = ctk.CTkTextbox(self, font=("Segoe UI", 14), state="disabled", corner_radius=15, wrap="word")
        self.chat_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # --- DEFINE COLOR TAGS HERE ---
        self.chat_area.tag_config("user_tag", foreground="#1f6aa5")
        self.chat_area.tag_config("ai_tag", foreground="#2cc985")
        self.chat_area.tag_config("system_tag", foreground="red")

        # 2. Input Area Frame
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message here...",
                                      height=45, font=("Segoe UI", 13))
        self.input_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_box.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=100, height=45,
                                          command=self.send_message, font=("Segoe UI", 13, "bold"))
        self.send_button.grid(row=0, column=1)

        self.conversation_history = []
        self.welcome_message()

    def welcome_message(self):
        self.update_chat("Assistant", "Hello! I'm your local AI. How can I help you today?")

    def update_chat(self, sender, message):
        self.chat_area.configure(state="normal")

        if sender == "You":
            tag = "user_tag"
        elif sender == "Assistant":
            tag = "ai_tag"
        else:
            tag = "system_tag"

        self.chat_area.insert("end", f"{sender}: ", tag)
        self.chat_area.insert("end", f"{message}\n\n")

        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")

    def send_message(self):
        user_message = self.input_box.get()
        if not user_message.strip():
            return

        self.input_box.delete(0, "end")
        self.update_chat("You", user_message)

        thread = threading.Thread(target=self.process_ai_response, args=(user_message,))
        thread.start()

    def process_ai_response(self, user_message):
        try:
            self.conversation_history.append(f"User: {user_message}")
            full_context = "\n".join(self.conversation_history)

            response = model.invoke(full_context)
            bot_message = response.content

            self.conversation_history.append(f"Assistant: {bot_message}")
            self.after(0, lambda: self.update_chat("Assistant", bot_message))

        except Exception as e:
            self.after(0, lambda: self.update_chat("System", f"Error: {str(e)}"))


if __name__ == "__main__":
    app = ModernChatApp()
    app.mainloop()