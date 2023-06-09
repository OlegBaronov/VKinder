from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from connection_data import community_token, access_token
from core import VkTools
from data_store import engine
from data_store import Viewed
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
        self.viewed = Viewed



    def bdate_toyear(self, bdate):
        user_yera = bdate.split('.')[2] if bdate is not None else None
        now = datetime.now().year
        return now - int(user_yera) if user_yera is not None else None


    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                      {'user_id': user_id,
                       'message': message,
                       'attachment': attachment,
                       'random_id': get_random_id()}
                      )

    def worksheet_photo_string(self, user_id, engine, worksheets):
        i = 1
        while i <= len(worksheets):
            worksheet = worksheets.pop()
            if self.viewed.check_user(engine, user_id, worksheet['id']) is False:
                photos = self.vk_tools.get_photos(worksheet["id"])
                photo_string = ''
                for photo in photos:
                    photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                break
            self.offset += 50
            i += 1
        return worksheet, photo_string


    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет' or event.text.lower() == 'здравствуйте':
                    self.params = {"event.user_id": self.vk_tools.get_profile_info(event.user_id)}
                    self.message_send(event.user_id, f'привет, {self.params["event.user_id"]["name"]}')
                    if self.params["event.user_id"].get('city') is None:
                        self.params["event.user_id"]['city'] = self.requests_city(event.user_id)
                    if self.params["event.user_id"].get('year') is None:
                        self.params["event.user_id"]['year'] = self.requests_bdate(event.user_id)
                elif event.text.lower() == 'поиск':
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    if self.worksheets:
                        worksheet, photo_string = self.worksheet_photo_string(event.user_id, engine, self.worksheets)



                    else:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                        worksheet, photo_string = self.worksheet_photo_string(event.user_id, engine, self.worksheets)
                       
                    self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                        attachment=photo_string
                        )

                    self.viewed.add_user(engine, event.user_id, worksheet['id'])

                elif event.text.lower() == 'пока' or event.text.lower() == 'до свидания':
                    self.message_send(event.user_id, 'всего хорошего!')


                else:
                    self.message_send(event.user_id, 'непонял, измените вопрос')



    def requests_city(self, user_id):
            self.message_send(user_id, 'укажите место жительства')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.message_send(user_id, 'место жительства добавлено')
                    return event.text.title()



    def requests_bdate(self, user_id):
        self.message_send(user_id, 'укажите ваш возраст(числом)')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if 10 < int(event.text) < 100:
                    self.message_send(user_id, 'возраст добавлен')
                    return int(event.text)
                else:
                    self.message_send(user_id, 'возраст указан некорректно')





if __name__ == '__main__':
    bot_interface = Botinterface(community_token, access_token)
    bot_interface.event_handler()
