from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")

username = env_vars.get("Username", "User")
assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Ensure the Data directory exists
data_dir = "Data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Path to the chat log file
chatlog_path = os.path.join(data_dir, "Chatlog.json")

# Load chat messages with proper error handling
if not os.path.exists(chatlog_path) or os.stat(chatlog_path).st_size == 0:
    messages = []
    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)
else:
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)
    except Exception:
        print("Warning: Chatlog.json is empty or corrupted. Resetting to default.")
        messages = []
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

# System prompt setup
system = f"""Hello, I am {username}. You are a very accurate and advanced AI chatbot named {assistantname} with real-time up-to-date information from the internet.
*** Do not tell time unless asked. Keep responses concise and direct. ***
*** Reply only in English, even if the question is in Hindi. ***
*** Do not provide notes in the output, just answer the question. Never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": system}]

def RealtimeInformation():
    """Generate real-time date and time information."""
    current_date_time = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed,\n"
        f"Day: {current_date_time.strftime('%A')} \n"
        f"Date: {current_date_time.strftime('%d')} \n"
        f"Month: {current_date_time.strftime('%B')} \n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H')} hours:"
        f"{current_date_time.strftime('%M')} minutes:"
        f"{current_date_time.strftime('%S')} seconds.\n"
    )

def AnswerModifier(answer):
    """Remove empty lines from the AI response."""
    return "\n".join([line for line in answer.split("\n") if line.strip()])

def ChatBot(query):
    """Process user query and return chatbot response."""
    global messages
    try:
        # Append user query
        messages.append({"role": "user", "content": query})

        # Get AI response
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in completion:
            if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s", "")

        # Append assistant response
        messages.append({"role": "assistant", "content": answer})

        # Save updated chat history
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)
    
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, an error occurred while processing your request."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))
