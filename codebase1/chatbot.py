import tkinter as tk
from tkinter import scrolledtext
import random

greetings = ["hello", "hi", "hey", "greetings", "sup", "what's up"]
greeting_responses = [
    "Hi there! How can I help you today?",
    "Hello! What can I do for you?",
    "Hey! Nice to chat with you!",
    "Hi! How are you doing?"
]

farewell = ["bye", "goodbye", "quit", "exit", "see you"]
farewell_responses = [
    "Goodbye! Have a great day!",
    "See you later!",
    "Bye! Take care!",
    "Thanks for chatting! Goodbye!"
]

how_are_you = ["how are you", "how do you do", "how's it going", "what's up"]
how_are_you_responses = [
    "I'm doing great, thanks for asking! How about you?",
    "I'm fine, thank you! How are you?",
    "All good here! What about you?",
    "Doing well! How can I help you today?"
]

name_questions = ["what's your name", "who are you", "your name"]
name_responses = [
    "I'm a simple chatbot built with Python!",
    "You can call me ChatBot! I'm here to help!",
    "I'm your friendly Python chatbot!"
]

joke_keywords = ["joke", "funny", "laugh"]
jokes = [
    "Why don't programmers like nature? It has too many bugs! 😄",
    "Why do Python programmers prefer dark mode? Because light attracts bugs! 😂",
    "What's a programmer's favorite hangout? The Foo Bar! 🍺"
]

help_keywords = ["help", "what can you do", "capabilities", "commands"]
help_responses = [
    "I can chat with you, answer simple questions, and keep you company!",
    "I can respond to greetings, tell jokes, and have conversations with you!",
    "Try asking me about my name, how I'm doing, or ask me to tell a joke!"
]

thanks_keywords = ["thank", "thanks", "appreciate"]
thanks_responses = [
    "You're welcome!",
    "Happy to help!",
    "No problem at all!",
    "Anytime!"
]

def get_response(user_input):
    user_input = user_input.lower().strip()

    if any(word in user_input for word in farewell):
        return random.choice(farewell_responses)

    if any(word in user_input for word in greetings):
        return random.choice(greeting_responses)

    if any(phrase in user_input for phrase in how_are_you):
        return random.choice(how_are_you_responses)

    if any(phrase in user_input for phrase in name_questions):
        return random.choice(name_responses)

    if any(word in user_input for word in joke_keywords):
        return random.choice(jokes)

    if any(word in user_input for word in help_keywords):
        return random.choice(help_responses)

    if any(word in user_input for word in thanks_keywords):
        return random.choice(thanks_responses)

    default_responses = [
        "That's interesting! Tell me more.",
        "I see. What else would you like to talk about?",
        "Hmm, I'm not sure about that. Can you rephrase?",
        "Interesting point! What do you think about it?",
        "I'm still learning! Try asking me something else."
    ]
    return random.choice(default_responses)

def send_message(event=None):
    user_message = input_box.get()

    if not user_message.strip():
        return

    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"You: {user_message}\n", "user")
    chat_area.config(state=tk.DISABLED)

    input_box.delete(0, tk.END)

    bot_response = get_response(user_message)

    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"Bot: {bot_response}\n\n", "bot")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)

window = tk.Tk()
window.title("Simple Chatbot")
window.geometry("760x560")
window.minsize(640, 480)

# Bigger default font across the app
window.option_add("*Font", "Arial 14")

chat_area = scrolledtext.ScrolledText(
    window,
    wrap=tk.WORD,
    state=tk.DISABLED,
    bg="#f0f0f0",
    padx=10,
    pady=10
)
chat_area.pack(padx=12, pady=12, fill=tk.BOTH, expand=True)

chat_area.tag_config("user", foreground="#0066cc", justify="right")
chat_area.tag_config("bot", foreground="#cc0000")

input_frame = tk.Frame(window)
input_frame.pack(padx=12, pady=(0, 12), fill=tk.X)

# Taller input box
input_box = tk.Entry(input_frame)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
input_box.bind("<Return>", send_message)

# Bigger button with padding so the label is always readable
send_button = tk.Button(
    input_frame,
    text="Send",
    command=send_message,
    bg="#1f6feb",
    fg="white",
    activebackground="#1a5fd0",
    activeforeground="white",
    relief=tk.FLAT,
    bd=0,
    padx=20,
    pady=10
)
send_button.pack(side=tk.RIGHT)


chat_area.config(state=tk.NORMAL)
chat_area.insert(tk.END, "Bot: Hi there! I'm your chatbot. How can I help?\n\n", "bot")
chat_area.config(state=tk.DISABLED)

input_box.focus()
window.mainloop()