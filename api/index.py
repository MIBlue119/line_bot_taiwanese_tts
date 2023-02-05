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

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

CHT_TTS_API_KEY = os.getenv("TTS_API_KEY")

app = Flask(__name__)
tts_processor = TTS()


def trans_wav_to_aac(file_path):
    """Convert wav file to aac file

    Args:
        file_path (str): wav file path

    Returns:
        int: audio duration in seconds
    """
    sound = AudioSegment.from_file(file_path, format="wav")
    file_name = Path(file_path).stem
    sound.export(f"./audio_{file_name}.aac", format="mp4")
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

    if event.message.text == "合成台語":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="我可以合成台語囉，歡迎來跟我互動 ^_^ ")
        )
        return

    if event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我繼續說話，請跟我說 「說話」 > <"),
        )
        return

    if working_status:
        desired_text = event.message.text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"開始合成囉，請稍等一下，我會說出來的 > < ，你說的是：{desired_text}"),
        )
        tts_processor.desired_text = desired_text

        random_num = random.randint(0, 100000)
        tts_audio_export_path = f"./audio_{random_num}.wav"
        tts_processor.generate_taiwanese_tts(
            text=tts_processor.desired_text,
            X_API_KEY=CHT_TTS_API_KEY,
            output_file_name=tts_audio_export_path,
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"合成完畢，將檔案存到 {tts_audio_export_path}"),
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"將檔案轉換成 aac 格式"),
        )
        # Trans wav to aac
        audio_duration = trans_wav_to_aac(tts_audio_export_path)

        line_bot_api.reply_message(
            event.reply_token,
            AudioSendMessage(
                original_content_url="./audio_" + str(random_num) + ".aac",
                duration=(audio_duration * 1000),
            ),
        )


if __name__ == "__main__":
    app.run()
