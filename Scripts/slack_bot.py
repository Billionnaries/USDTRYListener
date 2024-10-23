import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackBot:
    def __init__(self, token, channel):

        self.client = WebClient(token=token)
        self.channel = channel

    async def on_ready(self):

        print(f"SlackBot is ready and will send messages to channel {self.channel}")

    async def send_message(self, text):
        """
        Function to send threshold exceeded message
        :param message:
        :return:
        """
        try:
            response = await self.client.chat_postMessage(
                channel=self.channel,
                text=text
            )
            print(f"Message sent to Slack channel {self.channel}: {text}")
        except SlackApiError as e:
            print(f"Error sending message to Slack: {e.response['error']}")
