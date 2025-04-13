# JARVIS - AI Personal Assistant 🤖

JARVIS is an advanced AI personal assistant that combines speech recognition, natural language processing, and automation capabilities to help you with various tasks.

## Features 🌟

- **Voice Interaction**: Natural speech recognition and text-to-speech capabilities
- **Real-time Information**: Access to up-to-date information through web searches
- **Application Control**: Open and close applications with voice commands
- **Media Control**: Play music and videos through voice commands
- **Content Generation**: Generate text content like letters and applications
- **Image Generation**: Create images using AI with voice prompts
- **System Control**: Manage system volume and other settings
- **Multi-language Support**: Support for multiple input languages
- **Modern GUI**: Clean and intuitive graphical interface

## Prerequisites 📋

- Python 3.8 or higher
- Windows operating system
- Internet connection

## Installation 🔧

1. Clone the repository:
```bash
git clone https://github.com/yourusername/JARVIS.git
cd JARVIS
```

2. Install required packages:
```bash
pip install -r Requirements.txt
```

3. Set up API keys in `.env` file:
```env
Username = 'your_username'
Assistantname = 'Jarvis'
GroqAPIKey = 'your_groq_api_key'
HuggingFaceAPIKey = 'your_huggingface_api_key'
CohereAPIKey = 'your_cohere_api_key'
InputLanguage = 'en'
AssistantVoice = 'en-CA-LiamNeural'
```

## Usage 🚀

1. Run the main application:
```bash
python Main.py
```

2. Click the microphone icon to toggle voice input
3. Speak commands naturally - examples:
   - "Open Chrome"
   - "What's the weather like?"
   - "Play music on YouTube"
   - "Generate an image of a sunset"
   - "Write an application for leave"

## Project Structure 📁

- `Backend/`: Core functionality modules
  - `Model.py`: Decision-making model
  - `ChatBot.py`: Conversational AI
  - `SpeechToText.py`: Voice recognition
  - `TextToSpeech.py`: Voice synthesis
  - `ImageGeneration.py`: AI image generation
  - `Automation.py`: System automation
  - `RealtimeSearchEngine.py`: Web search functionality

- `Frontend/`: User interface components
  - `GUI.py`: Main graphical interface
  - `Files/`: Runtime data storage
  - `Graphics/`: UI assets

- `Data/`: Storage for generated content and chat logs

## API Keys Required 🔑

- [Groq API](https://console.groq.com/keys)
- [HuggingFace API](https://huggingface.co/)
- [Cohere API](https://dashboard.cohere.com/api-keys)

## Voice Customization 🎙️

You can customize the assistant's voice by changing the `AssistantVoice` variable in the `.env` file. Available voices can be found [here](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462).

## Language Support 🌍

Change the input language by updating the `InputLanguage` variable in the `.env` file. Language codes can be found [here](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes).

## Contributing 🤝

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](your-repo-issues-link).

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 👏

- Edge-TTS for voice synthesis
- HuggingFace for image generation
- Groq for language processing
- Cohere for decision making

## Disclaimer ⚠️

This project is for educational purposes only. Some features may require API keys from third-party services.