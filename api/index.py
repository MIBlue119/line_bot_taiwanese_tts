from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioSendMessage
from api.tts import TTS

from pydub import AudioSegment
import random
import math
import os
from pathlib import Path
import time


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

CHT_TTS_API_KEY = os.getenv("TTS_API_KEY")

app = Flask(__name__)
tts_processor = TTS()


def trans_wav_to_mp3(file_path, static_dir):
    """Convert wav file to mp3 file

    Args:
        file_path (str): wav file path

    Returns:
        int: audio duration in seconds
    """
    sound = AudioSegment.from_file(file_path, format="wav")
    file_name = Path(file_path).stem
    aac_file_path = os.path.join(static_dir, f"{file_name}.mp3")
    sound.export(aac_file_path, format="mp3")
    return math.ceil(sound.duration_seconds)


def trans_wav_to_aac(file_path, static_dir):
    """Convert wav file to aac file

    Args:
        file_path (str): wav file path

    Returns:
        int: audio duration in seconds
    """
    sound = AudioSegment.from_file(file_path, format="wav")
    file_name = Path(file_path).stem
    aac_file_path = os.path.join(static_dir, f"{file_name}.aac")
    sound.export(aac_file_path, format="mp4")
    return math.ceil(sound.duration_seconds)


# domain root
@app.route("/")
def home():
    return "Hello, World!"


@app.route("/webhook", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "台語":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="我可以合成台語囉，歡迎來跟我互動 ^_^ ")
        )
        return

    if event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我合成，請跟我說 「台語」 > <"),
        )
        return

    if working_status:
        desired_text = event.message.text
        print(f"Desired text: {desired_text}")

        tts_processor.desired_text = desired_text

        random_num = time.strftime("%Y%m%d-%H%M%S")
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        os.makedirs(static_dir, exist_ok=True)

        tts_audio_export_path = f"{static_dir}/audio_{random_num}.wav"
        try:
            tts_processor.generate_taiwanese_tts(
                text=tts_processor.desired_text,
                tts_key=CHT_TTS_API_KEY,
                output_path=tts_audio_export_path,
            )
        except Exception as e:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"合成失敗，請稍後再試，或是聯絡我們，謝謝 > <. {e}"),
            )
            return

        # Trans wav to mp3

        audio_duration = trans_wav_to_mp3(tts_audio_export_path, static_dir)
        print("Audio duration: ", audio_duration)

        audio_message = AudioSendMessage(
            original_content_url="https://f726-36-226-175-222.jp.ngrok.io"
            + "/static/"
            + "audio_"
            + str(random_num)
            + ".mp3",
            duration=(audio_duration * 1000),
        )
        line_bot_api.reply_message(event.reply_token, audio_message)


if __name__ == "__main__":
    app.run()
