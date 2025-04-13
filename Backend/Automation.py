from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars["GroqAPIKey"]

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzWSb YwPhnf", "pclqee", "tw-Data-text tw-tell-small tw-ta",
           "IZ6rdc", "05uRd", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there is anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

SystemChatBot = [{"role": "system", "content": "Hello, I am ChatBot. You're a content writer. You have to write content like a letter."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def OpenNotepad(File):
    default_text_editor = 'notepad.exe'
    subprocess.Popen([default_text_editor, File])

def ContentWriterAI(prompt):
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=SystemChatBot + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1.0,
        stream=False  
    )

    Answer = completion.choices[0].message.content  
    Answer = Answer.replace("</s>", "")

    messages.append({"role": "assistant", "content": Answer})

    topic_cleaned = prompt.replace("Content ", "").lower().replace(" ", "")
    file_path = rf"Data\{topic_cleaned}.txt"

    os.makedirs("Data", exist_ok=True)  

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(Answer)


    subprocess.Popen(["notepad.exe", file_path])

    return True


def Content(Topic):
    return ContentWriterAI(Topic)


def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYouTube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            responses = sess.get(url, headers=headers)

            if responses.status_code == 200:
                return responses.text
            else:
                print("Failed to retrieve search results.")
                return None

        html = search_google(app)

        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])

        return True


def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True)
        except:
            return False


def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volumeup():
        keyboard.press_and_release("volumeup")

    def volumedown():
        keyboard.press_and_release("volumedown")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volumeup":
        volumeup()
    elif command == "volumedown":
        volumedown()
    return True


async def TranslateAndExecute(commands: list[str]):
    func = []
    for command in commands:
        if command.startswith("open "):
            if "open it" in command or "open file" in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                func.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            func.append(fun)
        elif command.startswith("play"):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            func.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            func.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            func.append(fun)
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            func.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            func.append(fun)
        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*func)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result


async def Automation(commands: list[str]):
    async for results in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    asyncio.run(Automation(["play afsanay","open whatsapp",]))