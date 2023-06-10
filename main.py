from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from connection_data import community_token, access_token
import psycopg2
import sqlalchemy



class Botinterface():
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        # self.api = VkTools(access_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                      {'user_id': user_id,
                       'message': message,
                       'attachment': attachment,
                       'random_id': get_random_id()}
                      )


    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет' or event.text.lower() == 'здравствуйте':
                    self.message_send(event.user_id, 'привет')
                elif event.text.lower() == 'поиск':
                    self.message_send(event.user_id, 'начинаем поиск')
                elif event.text.lower() == 'пока' or event.text.lower() == 'до свидания':
                    self.message_send(event.user_id, 'всего хорошего!')
                else:
                    self.message_send(event.user_id, 'непонял, измените вопрос')































if __name__ == '__main__':
    bot_interface = Botinterface(community_token, access_token)
    bot_interface.event_handler()