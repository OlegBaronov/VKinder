from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from connection_data import community_token, access_token
from core import VkTools
import psycopg2
import sqlalchemy



class Botinterface():
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 50

    def bdate_toyear(self, bdate):
        user_yera = bdate.split('.')[2] if bdate is not None else None
        now = datetime.now().year
        return now - int(user_yera) if user_yera is not None else None

    def request_city(self, user_id):
        self.message_send(
            user_id, 'Укажите место жительства')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                city = event.text.lower()
        return city

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                      {'user_id': user_id,
                       'message': message,
                       'attachment': attachment,
                       'random_id': get_random_id()}
                      )

    def worksheet_photo_string(self, id):
        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
        worksheet = self.worksheets.pop()
        photos = self.vk_tools.get_photos(worksheet['id'])
        photo_string = ''
        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
        return photo_string


    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет' or event.text.lower() == 'здравствуйте':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'привет, {self.params["name"]}')
                    if self.params['city'] is None:
                        self.params['city'] = {self.request_city('user_id')}
                elif event.text.lower() == 'поиск':
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    self.worksheet_photo_string("id")
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheet_photo_string("id")
                    self.offset += 50
                    self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                                      attachment=photo_string
                    )


                elif event.text.lower() == 'пока' or event.text.lower() == 'до свидания':
                    self.message_send(event.user_id, 'всего хорошего!')
                else:
                    self.message_send(event.user_id, 'непонял, измените вопрос')











if __name__ == '__main__':
    bot_interface = Botinterface(community_token, access_token)
    bot_interface.event_handler()