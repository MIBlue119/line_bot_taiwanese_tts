# Line_Bot_Taiwanese_TTS

### Intro

- A simple app to call Chunghwa Telecom's https://iot.cht.com.tw/iot/developer taiwanese speech synthesizer
- Connect the app with Line bot
- Use [ngrok](https://ngrok.com/) to put localhost api with https

### Installation

- construct python environment
- install dependencies with `pip install -r requirements.txt`

### Usage

1. Apply the Chunghwa Telecom's API Key

   1. Get the Key as `TTS_API_KEY`
2. Construct a new Messaging API at [line developer](https://developers.line.biz/zh-hant/)

   1. Construct a provider with specified channel
   2. Get `LINE_CHANNEL_SECRET` at Basic Settings page
      1. Set at environment variable: ` export` LINE_CHANNEL_SECRET=xxxxx
   3. Set somethings at Messaging API page
      1. Enable `Allow bots to join group chats`
      2. Disable `Auto-reply messages`
      3. Disable `Greeting messages`
   4. Get `LINE_CHANNEL_ACCESS_TOKEN` at Messaging API page
      1. Set at environment variable: `export `LINE_CHANNEL_ACCESS_TOKEN=xxxxx
3. Execute the ngrok to forward the localhost default port 5000 to get the url with https

   ```
   ./ngrok http 5000
   ```
4. Set the ngrok url at api/index.py and run it

   - example url of ngrok : `https://f726-39-226-175-899.jp.ngrok.io`
   - Set it at environment variable
     - ```
       export APP_URL=https://f726-39-226-175-899.jp.ngrok.io
       ```

   ```python
   python -m api.index
   ```
5. Set the https url as the line bot webhook at webhook settings and open the `use webhook` slider

   - example: `https://f726-39-226-175-899.jp.ngrok.io`/webhook
     - verify the url to get success message

Note: Chunghwa Telecom may close the API.

### Resources

- https://github.dev/howarder3/GPT-Linebot-python-flask-on-vercel
- 用 Python 暢玩 Line bot - 08：Audio message part1 & 2

  - https://ithelp.ithome.com.tw/articles/10280411
  - https://ithelp.ithome.com.tw/m/articles/10280905
- line audiomessage

  - https://github.com/Marketing-Live-in-Code/line_bot_AudioSendMessage/blob/main/app.py
- Test webhook at local

  - https://cleanshadow.blogspot.com/2017/02/ngrokline-botwebhook.html
