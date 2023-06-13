from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError
from connection_data import access_token
from pprint import pprint
class VkTools:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)

    def bdate_toyear(self, bdate):
        user_yera = bdate.split('.')[2] if bdate is not None else None
        now = datetime.now().year
        return now - int(user_yera)


    def get_profile_info(self, user_id):
        try:
            info, = self.vkapi.method('users.get',
                                {'users_id': user_id,
                                 'fields': 'city,sex,relation,bdate'
                                 }
                                 )
        except ApiError as e:
            info ={}
            print(f'error = {e}')
        result = {'name': (info['first_name']+ '' + info['last_name']) if
                  'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'year': self.bdate_toyear(info.get('bdate'))
                 }
        return result


    def search_worksheet(self, params, offset):
        try:
            users = self.vkapi.method('users.search',
                                      {
                                     'count': 50,
                                      'offset': offset,
                                    'hometown': params['city'],
                                     'sex': 1 if params['sex'] == 2 else 2,
                                     'has_photo': True,
                                     'age_from': params['year'] - 3,
                                     'age_to': params['year'] + 3
                                    }
                                    )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{'name': item['first_name'] + '' + item['last_name'],
                    'id': item['id'],
                   } for item in users['items'] if item['is_closed'] is False
                  ]
        return result


    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get',
                                    {'owner_id': id,
                                     'album_id': 'profile',
                                     'extended': 1,
                                     'photo_sizes': 1
                                     }
                                    )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                    'id': item['id'],
                    'likes': item['likes']['count'],
                    'comments': item['comments']['count']
                   } for item in photos['items']
                  ]
        result.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)
        return result








if __name__ == '__main__':
    user_id = 806571703
    tools = VkTools(access_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params, 50)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])
    pprint(photos)
