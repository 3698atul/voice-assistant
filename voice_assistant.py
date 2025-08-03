import google.generativeai as genai
import speech_recognition as sr  # type: ignore
import subprocess
import webbrowser
import sys
import pyperclip
from datetime import datetime
import gradio as gr

# Gemini API Key
GEMINI_API_KEY = "AIzaSyC9dyHYZWQxNkvU69iP89L3AUyj1K2n7j8"
genai.configure(api_key=GEMINI_API_KEY)                             #type: ignore

# defining the tools
def open_application(app_name: str):
    try:
        if sys.platform == "win32":
            subprocess.Popen([app_name])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen([app_name])
        return f"Successfully launched {app_name}."
    except FileNotFoundError:
        return f"Error: Could not find the application '{app_name}'."
    except Exception as e:
        return f"An error occurred while opening {app_name}: {e}"

def search_online(query: str):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching for '{query}' online."

def create_file(file_path: str, content: str = ""):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully created the file: {file_path}"
    except Exception as e:
        return f"Error creating file: {e}"

def read_clipboard() -> str:
    try:
        return f"The clipboard content is: {pyperclip.paste()}"
    except Exception as e:
        return f"Could not read clipboard: {e}"

def get_current_datetime() -> str:
    now = datetime.now()
    return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

# Model Setup 
model = genai.GenerativeModel(                                        # type: ignore
    model_name='gemini-2.5-pro',
    tools=[open_application, search_online, create_file, read_clipboard, get_current_datetime]
)
chat = model.start_chat(enable_automatic_function_calling=True)

#  Speech Recognition
recognizer = sr.Recognizer()

def listen_for_command() -> str | None:
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.pause_threshold = 1.0
        recognizer.adjust_for_ambient_noise(source)                                                                        # type: ignore
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)                                           #type: ignore
            print("Recognizing...")
            command = recognizer.recognize_google(audio)                                                                   # type: ignore
            print(f"You said: {command}")
            return command.lower()                                                                                      #type: ignore
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError as e:
            return f"Could not request results; {e}"
        except sr.WaitTimeoutError:
            return "Listening timed out."

def handle_text_input(command: str) -> str:
    if not command:
        return "Please type something."
    if "exit" in command.lower():
        return "Exiting assistant."
    response = chat.send_message(command)                                                                    # type: ignore
    return response.text or "Done."

def handle_voice_input() -> str:
    command = listen_for_command()
    if not command:
        return "No command received."
    return handle_text_input(command)

# gradio ka ui setup
custom_css = """
body { background-color: #121212; color: #ffffff; }
#component-0 { color: #ffffff !important; }
textarea, input, button {
    background-color: #1e1e1e !important;
    color: #ffffff !important;
    border: 1px solid #333 !important;
}
button:hover {
    background-color: #333 !important;
}
"""

with gr.Blocks(css=custom_css, theme="base") as demo:
    gr.Markdown("## 🎤 Gemini Voice Assistant (Dark UI)", elem_id="title")
    
    with gr.Row():
        input_box = gr.Textbox(label="Type your command")
        output_box = gr.Textbox(label="Assistant Response", lines=4)
    
    with gr.Row():
        text_btn = gr.Button("▶️ Send Text")
        voice_btn = gr.Button("🎙️ Use Voice")

    text_btn.click(handle_text_input, inputs=input_box, outputs=output_box)
    voice_btn.click(handle_voice_input, outputs=output_box)

# to run the voice assistant
if __name__ == "__main__":
    demo.launch(inbrowser=True)
