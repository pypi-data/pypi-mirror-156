
from datetime import date
from email import message
from slack import WebClient
from requests import Response
from typing import Optional, List
from .models import Author, Message, Color, Footer, Field
import json


class BotSlackPlugin:
    def __init__(self, slack_token: str, channel: str, **kwargs):
        """
        BotSlackPlugin

        Args:
            slack_token (str): Authentication token.
            channel (str): Channel or private group to send message to. Can be an ID, or a name.
        """
        self._channel = channel
        self._client = WebClient(token=slack_token, **kwargs)


    @property
    def client(self):
        """
        Slack client instance.

        Returns:
            client: The slack client instance.

        """
        return self._client

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, channel):
        self._channel = channel

    def _id_for_username(self, username):
        member_list = self.client.users_list().get("members")

        for member in member_list:
            if member["real_name"] == username:
                return member["id"]
        return None

    def _get_users_mention(self, users: List[str]):  
        if not users:
            return ""

        ids = []
        for user in users:
            ids.append(self._id_for_username(user))
        return " ".join([f"<@{id}>" for id in ids if id is not None])


    def send_simple_message(self, text: str, channel: Optional[str] = None, users: Optional[List[str]] = None,
                            attachment: Optional[bool] = False, **kwargs):
        """
       Sends a simple message.

       Args:
           text (str): The text of message.
           channel (str, optional): Channel or private group to send message to. Can be an ID, or a name.
           users (str): The usernames for mentions
           attachment (dict): For a simple message keep Default false.

       Returns:
           response: send message response.
       """
        return self.send_message(message=Message(text=text), channel=channel or self.channel, users=users,
                                 attachment=attachment, **kwargs)

    def send_message(self, message: Message, attachment: Optional[bool] = True, channel: Optional[str] = None,
                     users: Optional[List[str]] = None, **kwargs) -> Response:
        """
       Sends a more elaborate message via attachment.

       Args:
           message (Message): The full content of the message.See [Message][botcity.plugins.slack.models.Message].
           attachment (dict): For a message with attachment keep Default True.
           channel (str, optional): Channel or private group to send message to. Can be an ID, or a name.
           users (str): The usernames for mentions.
       Returns:
           response: send message response.
       """
        message.text = f"{self._get_users_mention(users)} {message.text}"
        return self.client.chat_postMessage(
            channel=channel or self.channel,
            attachments= "" if attachment == False else json.dumps([message.asdict()]),
            text= message.text, **kwargs)

    def update_message(self, response: Response, text: str, users: Optional[List[str]] = None) -> Response:
        """
        Update the message based on the response passed as argument.

        Args:
            response (Response): The response of sended message.
            text (str): The new text for message update.
            users (str): The usernames for mentions.
        Returns:
            response: update message response.
        """

        channel = response["channel"]

        ts = response["ts"]

        response.text = f"{self._get_users_mention(users)} {text}"
        return self.client.chat_update(channel=channel or self.channel,
                                       ts=ts, text=response.text)

    def delete_message(self, response: Response) -> Response:
        """
        Deletes the message based on the response passed as argument.

        Args:
            response (Response): The response of sended message. 
        Returns:
            response: delete message response.
        """
        channel = response["channel"]
        ts = response["ts"]
        return self.client.chat_delete(channel=channel, ts=ts)

    def upload_file(self, file: str, channel: Optional[str] = None, text_for_file: Optional[str] = None,
                  title_for_file: Optional[str] = None) -> Response:
        """
        Upload file to slack.

        Args:
            file (str): The file path.
            channel (str, optional): Channel or private channel to send message to. Can be an ID, or a name.
            text_for_file (str, optional): The text that comes before the file upload.
            text_for_file (str, optional): The File title.

        Returns:
            response: upload file response.
        """
        return self.client.files_upload(channels=channel or self.channel, file=file, initial_comment=text_for_file, title=title_for_file)

    def delete_file(self, response: Response) -> Response:
        """
        Deletes file based on the response of upload file passed as argument.

        Args:
            response (Response): Response of upload file.
        Returns:
            response: delete file response.
        """
        file_id = response["file"]["shares"]["public"]
        for key, value in file_id.items():
            value = value
            channel = key
        ts = [v["ts"] for v in value]
        return self.client.chat_delete(channel=channel, ts=ts)

