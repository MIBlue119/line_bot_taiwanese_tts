import urllib.request
import urllib.parse


class TTS:
    def __init__(self, desired_text=None):
        self.desired_text = desired_text

    def generate_taiwanese_tts(self, text, tts_key, output_path):
        """Generate taiwanese tts"""
        # Convert text to url encoding
        text_encoded = urllib.parse.quote(text)
        url = f"https://iot.cht.com.tw/apis/CHTIoT/tts/v1/tw/synthesisRaw?inputText={text_encoded}"
        headers = {"X-API-KEY": tts_key}
        # Send request
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        # Write response to file
        audio = response.read()
        with open(output_path, "wb") as f:
            f.write(audio)
        return
