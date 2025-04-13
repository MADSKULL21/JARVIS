from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "AI Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}. You are an advanced AI chatbot named {Assistantname}, 
which provides real-time, up-to-date information from the internet.

*** Provide answers in a professional manner with correct grammar, punctuation, and clarity. ***
*** Just answer the question based on the provided data in a professional way. ***"""

# Load previous chat logs or create a new one
chat_log_path = os.path.join("Data", "ChatLog.json")
if not os.path.exists(chat_log_path):
    with open(chat_log_path, "w") as f:
        dump([], f)

# Function to perform Google search
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    
    Answer += "[end]"
    return Answer

# Function to remove unnecessary whitespace from answers
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Initial chatbot system message
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "HI"},
    {"role": "assistant", "content": "Hello, how can I help you?"},
]

# Function to provide real-time date & time information
def Information():
    current_date_time = datetime.datetime.now()
    return (
        f"Use this real-time information if needed:\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H')} hours, "
        f"{current_date_time.strftime('%M')} minutes, "
        f"{current_date_time.strftime('%S')} seconds.\n"
    )

# Function to handle real-time search queries
def RealTimeSearchEngine(prompt):
    global SystemChatBot

    # Load chat history
    with open(chat_log_path, "r") as f:
        messages = load(f)

    # Append user search query to messages
    search_result = GoogleSearch(prompt)
    messages.append({"role": "user", "content": search_result})

    # Append system information
    SystemChatBot.append({"role": "system", "content": search_result})

    # AI model request
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat history
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        # Remove the last added system message to prevent duplication
        SystemChatBot.pop()
        return AnswerModifier(Answer)

    except Exception as e:
        return f"Error occurred: {e}"

# Main execution loop
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealTimeSearchEngine(prompt))
