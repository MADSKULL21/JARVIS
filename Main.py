from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealTimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech
from Backend.ChatBot import ChatBot
from dotenv import dotenv_values
from time import sleep
import subprocess
import threading
import os
import json
import asyncio

# Ensure Temp Directory Exists
TEMP_DIR = "Temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
DefaultMessage = f'''{Username}: Hello {Assistantname}. How are you?
{Assistantname}: Welcome {Username}. I am doing well. How can I help you?'''
subprocesses = []
Functions = ["open", "close", "system", "play", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    """Ensure the chat log has default messages if empty."""
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as file:
            if len(file.read().strip()) < 5:
                with open(os.path.join(TEMP_DIR, "Database.data"), "w", encoding="utf-8") as db_file:
                    db_file.write("")
                with open(os.path.join(TEMP_DIR, "Responses.data"), "w", encoding="utf-8") as resp_file:
                    resp_file.write(DefaultMessage)
    except FileNotFoundError:
        os.makedirs("Data", exist_ok=True)
        with open("Data/ChatLog.json", "w", encoding="utf-8") as file:
            file.write("[]")
        with open(os.path.join(TEMP_DIR, "Database.data"), "w", encoding="utf-8") as db_file:
            db_file.write("")
        with open(os.path.join(TEMP_DIR, "Responses.data"), "w", encoding="utf-8") as resp_file:
            resp_file.write(DefaultMessage)

def ReadChatLogJson():
    """Read and return the chat log JSON data."""
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ChatLogIntegration():
    """Integrate chat log data into the database."""
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    
    with open(os.path.join(TEMP_DIR, "Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    """Display chats on the GUI."""
    with open(os.path.join(TEMP_DIR, "Database.data"), "r", encoding="utf-8") as file:
        data = file.read()
        if data:
            with open(os.path.join(TEMP_DIR, "Database.data"), "w", encoding="utf-8") as file:
                file.write(data)

def InitialExecution():
    """Initialize the application."""
    SetMicrophoneStatus("False")# Start with microphone muted
    SetAssistantStatus("Available")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    """Main execution logic for processing user queries."""
    
    # Check Microphone Status Before Executing SpeechRecognition
    if GetMicrophoneStatus() != "True":
        print("[🔇] Microphone is MUTED. Not processing queries.")
        return
    
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()  # Now won't run if muted
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    
    print(f"Decision: {Decision}")
    
    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)
    
    Merged_query = " and ".join([" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")])
    
    for queries in Decision:
        if "general" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
    
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                print(f"Executing Automation for: {queries}")  
                asyncio.run(Automation(list(Decision)))  # Fixed: Await Automation
                TaskExecution = True
            
    if ImageExecution:
        print(f"Image Generation Query: {ImageGenerationQuery}")  
    with open("Frontend/Files/ImageGeneration.data", "w") as file:
        file.write(f"{ImageGenerationQuery},True")
    
    try:
        p1 = subprocess.Popen(
            ["python", "Backend/ImageGeneration.py"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, shell=False
        )
        subprocesses.append(p1)
        print("ImageGeneration subprocess started successfully.")
    except Exception as e:
        print(f"Error starting ImageGeneration.py: {e}")
            
    if (G and R) or R:
        SetAssistantStatus("Searching...")
        Answer = RealTimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                os._exit(0)

def FirstThread():
    """First thread to handle microphone status and main execution."""
    while True:
        if GetMicrophoneStatus() == "True":
            print("[🎤] Microphone is ON. Listening...")
            MainExecution()
        else:
            print("[🔇] Microphone is MUTED. Not processing queries.")
        sleep(0.5)

def SecondThread():
    """Second thread to handle the GUI."""
    GraphicalUserInterface()

def ToggleMicrophone():
    """Toggles the microphone on/off."""
    status = GetMicrophoneStatus()
    new_status = "False" if status == "True" else "True"
    SetMicrophoneStatus(new_status)

    if new_status == "False":
        SetAssistantStatus("Muted 🎙️")
        print("[🔇] Microphone Muted")
    else:
        SetAssistantStatus("Listening 🎧")
        print("[🎤] Microphone Unmuted")

if __name__ == "__main__":
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()
