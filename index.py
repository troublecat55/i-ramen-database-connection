import os
import csv
import secrets
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from vincenty import vincenty
from decimal import *
from itertools import islice, groupby
import requests
import re

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
  from dotenv import load_dotenv
  load_dotenv()
  SQLALCHEMY_DATABASE_URI_PRIVATE = os.getenv("SQLALCHEMY_DATABASE_URI_PRIVATE")
  app.debug = True
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI_PRIVATE
else:
  DATABASE_URL = os.environ.get('DATABASE_URL')
  app.debug = False
  app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# # #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# #---------------------------------initialize tables--------------------------
class Main_store(db.Model):
  __tablename__ = 'main_store'
  store_id = db.Column (db.Integer, primary_key = True)
  main_store = db.Column(db.String(50), nullable=False, unique = True)

  detail_store_relationship = db.relationship('Store', backref= 'main_store', lazy=True)
  post_relationship = db.relationship('Post', backref= 'main_store', lazy=True)
  def __init__(self, main_store):
    self.main_store = main_store

class Store(db.Model):
  __tablename__ = 'store'
  detail_store_id = db.Column (db.String(10), primary_key = True)
  store_id = db.Column (db.Integer, db.ForeignKey('main_store.store_id'), nullable=False, onupdate ='CASCADE')
  store = db.Column (db.String(50), nullable=False, unique = True)
  still_there = db.Column (db.Boolean, nullable=False)
  address = db.Column (db.String(200))
  discription = db.Column (db.String(500))
  open_time = db.Column (db.String(200))
  latitude = db.Column (db.Numeric(10,8), nullable=False,)
  longtitute = db.Column (db.Numeric(11,8),  nullable=False)
  map_review = db.Column (db.Text())
  region = db.Column (db.String(1))
  province = db.Column (db.String(3))
  soup = db.Column (db.String(200))
  transport =  db.Column (db.String(100))

  store_favorite_relationship = db.relationship('Favorite', backref= 'store', lazy=True)

  def __init__(self, store_id, store, still_there, address, discription,\
     open_time, latitude, longtitute, map_review, region, province, soup, transport):
    self.store_id = store_id
    self.store = store
    self.still_there = still_there
    self.address = address
    self.discription = discription
    self.open_time = open_time
    self.latitude = latitude
    self.longtitute = longtitute
    self.map_review = map_review
    self.region = region
    self.province = province
    self.soup = soup
    self.transport = transport

class Post(db.Model):
  __tablename__ = 'post'
  post_id = db.Column (db.String(10), primary_key = True)
  store_id = db.Column (db.Integer, db.ForeignKey('main_store.store_id'), nullable=False, onupdate ='CASCADE')
  stores = db.Column (db.String(30))
  create_on = db.Column (db.DateTime)
  ramen_name = db.Column (db.String(100))
  fb_review = db.Column (db.Text())

  def __init__(self, store_id, stores, create_on, ramen_name, fb_review):
    self.store_id = store_id
    self.stores = stores
    self.create_on = create_on
    self.ramen_name = ramen_name
    self.fb_review = fb_review

class Favorite(db.Model):
  __tablename__ = 'favorite'
  id = db.Column (db.Integer, primary_key = True, autoincrement=True)
  line_id = db.Column (db.String(34), nullable = False)
  detail_store_id = db.Column (db.String(10), db.ForeignKey('store.detail_store_id'), nullable = False, onupdate ='CASCADE')
  
  def __init__(self, line_id, detail_store_id):
    self.line_id = line_id
    self.detail_store_id = detail_store_id
    



## Python3 #打開cmd輸入以下code
# from app import db (app is the file name)
# db.create_all() #https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
# exit()

# query
# print(province_soup_q) #(<Main_store 0>, <Store 2223>, <Post 3331>)

   
# query
def get_data_str(lst):
  output_before_random = ''
  for r in lst:
    if r[2] is None:
      output_before_random += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},MAP_REVIEW:{r[1].map_review},LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},OPEN_TIME:{r[1].open_time},CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
    else:
        try:
          output_before_random += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},FB_R_CREATE:{r[2].create_on},FB_R_RAMEN:{r[2].ramen_name},FB_R_CONTENT:{r[2].fb_review},LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},OPEN_TIME:{r[1].open_time},CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
        except AttributeError as error:
          output_before_random += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},MAP_REVIEW:{r[1].map_review},LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},OPEN_TIME:{r[1].open_time},CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
  return output_before_random


def query_province_soup(p, s):
  province_soup_q = db.session.query(Main_store, Store, Post)\
                      .outerjoin(Post, Post.store_id == Main_store.store_id)\
                      .outerjoin(Store, Store.store_id == Main_store.store_id)\
                      .filter(Store.province == p)\
                      .filter(Store.soup.contains(s))\
                      .filter(Store.still_there == True)
  return province_soup_q
def query_province_direct(p):
  province_soup_q = db.session.query(Main_store, Store, Post)\
                      .outerjoin(Post, Post.store_id == Main_store.store_id)\
                      .outerjoin(Store, Store.store_id == Main_store.store_id)\
                      .filter(Store.province == p)\
                      .filter(Store.still_there == True)
  return province_soup_q

def query_region_by_store_table(r):
  province_soup_q = db.session.query(Main_store, Store)\
                      .outerjoin(Store, Store.store_id == Main_store.store_id)\
                      .filter(Store.region == r)\
                      .filter(Store.still_there == True)
  return province_soup_q
def query_store_by_full_name(s):
  store_direct = db.session.query(Main_store, Store, Post)\
                      .outerjoin(Post, Post.store_id == Main_store.store_id)\
                      .outerjoin(Store, Store.store_id == Main_store.store_id)\
                      .filter(Store.store == s)\
                      .filter(Store.still_there == True)
                      
  return store_direct

def query_store(store_k1,store_k2):
  store_direct = db.session.query(Main_store, Store, Post)\
                      .outerjoin(Post, Post.store_id == Main_store.store_id)\
                      .outerjoin(Store, Store.store_id == Main_store.store_id)\
                      .filter(Store.store.contains(store_k1))\
                      .filter(Store.store.contains(store_k2))\
                      .filter(Store.still_there == True)
                      
  return store_direct



def convert_string_to_lst(string,c): 
    li = list(string.split(c)) 
    return li 


#-------------------------------------------------GIS---------------------------------------------------------
def take(n, iterable):
    #"Return first n items of the iterable as a list"
    return list(islice(iterable, n))
#-------------------------------------------------format map review---------------------------------------------------------
def divide_map_review(comment_s):
    comment_clean = comment_s.replace(" - ", "-").replace("- ", "-").replace(" -", "-")
    # print(comment_clean)
    comment_lst = list(filter(None,re.split('[   ]',comment_clean)))
    comment_clean_split = re.split('[   ]',comment_clean)
    comment_lst = [i for i in comment_clean_split if i]
    # print(comment_lst)
    if len(comment_lst) > 1:
        comment_final_list = []
        for i, val in enumerate(comment_lst):
            if i != (len(comment_lst)-1) and val[-1].islower() == True and val[0].isupper() == True and comment_lst[i+1][0].isupper() == True:
                val = val + comment_lst[i+1]
                comment_lst.remove(comment_lst[i+1])
            comment_final_list.append(val)

        return comment_final_list
    else:
        return comment_lst


map_review_data = db.session.query(Store.map_review).filter(Store.still_there == True)
for r in map_review_data:
  r_str = ''.join(list(map(str,r)))
  k = divide_map_review(r_str)
  print(k)

'''
前端流程構思:
拉麵推薦>北中南東+定位(加按鈕)
定位  -叫user開定位 -推薦附近五家店或十家店(動態)
      -叫user開定位 -開台灣拉麵愛好會地圖給user, URL後面用使用者 long lat 定位(網址:https://www.google.com/maps/d/u/0/viewer?fbclid=IwAR3O8PKxMuqtqb2wMKoHKe4cCETwnT2RSCZSpsyPPkFsJ6NpstcrDcjhO2k&mid=1I8nWhKMX1j8I2bUkN4qN3-FSyFCCsCh7&ll={u_lat}%2C{u_long})

'''

city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市"\
            ,"台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]
n_city = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市"]
c_city = ["台中市","彰化縣","南投縣","雲林縣"]
s_city = ["嘉義市","台南市","高雄市","屏東縣"]
e_city = ["宜蘭縣","花蓮縣","台東縣"]
n_dict = dict.fromkeys(n_city, "北")
c_dict = dict.fromkeys(c_city, "中")
s_dict = dict.fromkeys(s_city, "南")
e_dict = dict.fromkeys(e_city, "東")
city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
user_address = 'No. 16, Nanjing West Road, Zhongshan District, Taipei City, Taiwan 10491'
u_lat = 25.05274
u_long = 121.52038
user_location = (u_lat, u_long)
u_address = user_address.replace(' ', '')
'''
做一個 縣市:區域 的字典
# print(city_name_dic) {"台北市":"北",...}
接下來抓縣市用區域來QUERY
'''

region_value = ''
for k, v in city_name_dic.items():
  if k in u_address:
    region_value = v
    all_store_province = query_region_by_store_table(region_value)
  elif k not in u_address and ("臺灣" in u_address or '台灣' in u_address or '台湾' in u_address or 'Taiwan' in u_address):
    all_store_province = province_soup_q = db.session.query(Main_store, Store)\
                      .outerjoin(Store, Store.store_id == Main_store.store_id)\
                      .filter(Store.still_there == True)
  elif k not in u_address and "臺灣" not in u_address or '台灣' not in u_address or '台湾' not in u_address or 'Taiwan' not in u_address:
    print("抱歉,請到台灣吃拉麵")
  else:
    print("出錯惹靠腰，請填寫出錯代碼「G1」")

# print(region_value)

'''
算距離
'''
# output_city_query = ''
store_distance_name = []
store_distance_list = []
for r in all_store_province:
  # print(f'long:{r[1].longtitute}')
  # print(f'lat:{r[1].latitude}')
  # print(r)
  # output_city_query += f'store = {r[1].store}, lat = {r[1].latitude}, long = {r[1].longtitute}'
  stores_loation_before_choice = (float(r[1].latitude),float(r[1].longtitute))
  distance = vincenty(user_location, stores_loation_before_choice)
  store_distance_name.append(r[1].store)
  store_distance_list.append(distance)

# print(len(store_distance_name))
# print(len(store_distance_list))
city_distance_dic = dict(zip(store_distance_name, store_distance_list))
sorted_city_distance_dic = {k: v for k, v in sorted(city_distance_dic.items(), key=lambda item: item[1])}
# print(sorted_city_distance_dic)

'''
###if the nearby stores > 10 印10家
###elif the nearby stores <= 10 and >=5 印5家
###elif the nearby stores <5 有幾家印幾家
'''
if  len(sorted_city_distance_dic) > 10:
  choice_nearby_city_tup = take(10, sorted_city_distance_dic.items())

elif (len(sorted_city_distance_dic) == 10 or len(sorted_city_distance_dic) < 10) and\
   (len(sorted_city_distance_dic) > 5 or len(sorted_city_distance_dic) == 5):
  choice_nearby_city_tup = take(5, sorted_city_distance_dic.items())
###elif the nearby stores < 5
elif len(sorted_city_distance_dic) > 0 and len(sorted_city_distance_dic) < 5: 
  choice_nearby_city_tup = take(len(sorted_city_distance_dic), sorted_city_distance_dic.items())
else:
  print('出錯惹靠腰，請填寫出錯代碼「G2」')



detail_nearby_list_table = []
final_table_nearby_shops = []
for r in choice_nearby_city_tup:
  detail_for_nearby_stores = query_store_by_full_name(r[0])
  for t in detail_for_nearby_stores:
    detail_nearby_list_table.append(t)
# print(detail_nearby_list_table)

detail_nearby_shops_group = [list(g) for b, g in groupby(detail_nearby_list_table, lambda tup: tup[1])]
# print(detail_nearby_shops_group)
for t in detail_nearby_shops_group:
  final_table_nearby_shops.append(secrets.choice(t))

nearby_store_result = get_data_str(final_table_nearby_shops)
#####get result store list
if nearby_store_result == None:
  print("No result ")
else :
  nearby_store_result = nearby_store_result.replace(u'\xa0', u' ').replace('\n','')
  nearby_store_result_final = convert_string_to_lst(nearby_store_result,'%')
  nearby_store_result_final = [i for i in nearby_store_result_final if i]
# print(f'nearby result length:{len(nearby_store_result_final)}')
# print(nearby_store_result_final)

'''
###印店家跟USER間的距離get distance between user and stores(Kilometers)###
抓法: 距離 = choice_nearby_city_dic[店家名]
'''
# choice_nearby_city_dic = dict(choice_nearby_city_tup)
# print(choice_nearby_city_dic)

'''
###get weather from the store印出店家附近的天氣###
# #!!!!shall extract APIkey  https://openweathermap.org/ 下面WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')這行要加進去
# #!!!!shall extract lon and lat from above store list 要先拿到店家的經緯度
# #!!!!實測過直接加進去flex message會跑太慢,在flex底部再多設一個按鈕(看更多推薦的附近),用點擊經緯度傳地圖的方法會比較user friendly
'''
# # WEATHER_API_KEY = ''
# lat = '22.62168700'
# lon = '120.29835700'
# # weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang=zh_tw&appid={weather_API_key}&units=metric'
# # get_weather_data = requests.get(weather_url)
# # weather_result = get_weather_data.json()
# # print(weather_result)
# # weather_discription = weather_result['weather'][0]['description']
# # main_temp = weather_result['main']['temp']
# # main_feels_like = weather_result['main']['feels_like']
# # main_temp_min = weather_result['main']['temp_min']
# # main_temp_max = weather_result['main']['temp_max']
# # print(main_temp, main_feels_like, main_temp_min, main_temp_max)

# def query_local_weather(lon,lat,APIkey):
#   weather_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&lang=zh_tw&appid={APIkey}&units=metric'
#   get_weather_data = requests.get(weather_url)
#   weather_result = get_weather_data.json()
#   return weather_result

# weather_data = query_local_weather(lon, lat, WEATHER_API_KEY)
# # print(weather_data)
# # dt_object =datetime.datetime.fromtimestamp(int(weather_data['current']['dt']))
# # print(dt_object)
# # print(weather_data['current'])

# # WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
# weather_data = query_local_weather(lon, lat, WEATHER_API_KEY)
# weather_description = weather_data['current']['weather'][0]['description']
# main_temp = weather_data['current']['temp']
# temp_feels_like = weather_data['current']['feels_like']
# humidity_procent = weather_data['current']['humidity']
# uvi_index = weather_data['current']['uvi']
# if 0 <= uvi_index <= 2:
#   uvi_index_description = '對於一般人無危險'
# elif 3 <= uvi_index <= 5:
#   uvi_index_description = '無保護暴露於陽光中有較輕傷害的風險'
# elif 6 <= uvi_index <= 7:
#   uvi_index_description = '無保護暴露於陽光中有很大傷害的風險'
# elif 8 <= uvi_index <= 10:
#   uvi_index_description = '暴露於陽光中有極高風險'
# elif 11 <= uvi_index:
#   uvi_index_description = '暴露於陽光中極其危險'
# else:
#   uvi_index_description = '目前無相關資訊'

# print(f'總結:{weather_description}  氣溫:{main_temp}℃  體感溫度:{temp_feels_like}℃\n濕度:{humidity_procent}%  紫外線指數:{uvi_index} 目前紫外線:{uvi_index_description}')


#^^^^-------------------------------------------------GIS end line---------------------------------------------------------



user_msg = 'query出來的地址'
user_select = 'Kido 拉麵'
select_first_param = ''
select_second_param = ''
result = ''
if ':' in user_select:
  select_first_param = user_select[:user_select.index(':')]
  select_second_param = user_select[user_select.index(':')+1:]
# print(select_second_param)

if select_first_param != '' and select_first_param != ''and\
  (select_first_param == '直接推薦') or (select_first_param == '看更多推薦'):
  #query withOUT soup
  result = query_province_direct(select_second_param)
  # print(type(result))
  #random here

elif select_first_param in city_name:
  #query with soup
  result = query_province_soup(select_first_param, select_second_param)
  # print(type(result))
  #random here

keyword_result = ''
if ' ' in  user_select:
  if  ' ' not in user_select[-1] and ' ' not in user_select[0]:
    input_lst = user_select.split()
    if len(input_lst) == 2 :
      count_store = query_store(input_lst[0],input_lst[1]).count()
      # print(count_store)
      if count_store != 0:
        keyword_result = query_store(input_lst[0],input_lst[1])
  #     else:
  #       keyword_result = ''
  # else:
  #   keyword_result = ''

# for r in result:
#   print(r)
#   print(r[1].store)
#   print(r[2])

#MAP_ID:{r[1].detail_store_id},FB_ID:{r[2].post_id}
# # #---------------------------------put all data in a string--------------------------

output_before_random_clear = get_data_str(result)


if output_before_random_clear == None:
  print("No result ok?")

else :
  output_before_random_clear = output_before_random_clear.replace(u'\xa0', u' ').replace('\n','')

  #---------------------------------change data to a list of datas--------------------------
  output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
  output_whole_lst = [i for i in output_whole_lst if i]
  # for data in output_whole_lst:
  #   if data == '' or data == ' ':
  #     print('false')
  #   else:
  #     print('true')
# print(f'length of whole list is {len(output_whole_lst)}')
# print(f'whole list is {output_whole_lst}')



  #---------------------------------random(everytime renew can auto random)--------------------------
if len(output_whole_lst) != 0:
  # print(len(output_whole_lst))
  try:
    output_s = secrets.choice(output_whole_lst)
    if(len(output_s) != 0):
      output_lst = convert_string_to_lst(output_s, ',')
      # print(f'result is {output_lst}')
      # print(f'result length{len(output_lst)}')
      # print(output_lst)
      # print(output_lst[-1][output_lst[-1].index(':')+1:])
    else:
      print("shithahaha")
  except IndexError as error:
    print("請輸入有效店名關鍵字(不可在前後加入空白)，例如\"鷹流 中山1\",\"一風堂\"")
else:
  print("請輸入有效店名關鍵字(不可在前後加入空白)，例如\"鷹流 中山2\",\"一風堂\"")
# print(output_lst)

'''
##---------------------------------------favorite list-------------------------------------
user_line_id = 'sgsg'
msg = '加到最愛清單:麵屋駟H.F-Ramen'
first_love_param = ''
second_love_param = ''
if ':' in msg:
  first_love_param = msg[:msg.index(':')]
  second_love_param = msg[msg.index(':')+1:]
# print( first_love_param )
# print( second_love_param )
  store_id_q = db.session.query(Store)\
        .filter(Store.store == second_love_param).count()
  # print(f'id is{store_id_q}')

def count_store_in_table(store_name):
  store_id_q = db.session.query(Store)\
      .filter(Store.store == store_name)\
      .count()
  return store_id_q
def get_store_id(store_name):
  get_id = ''
  store_id_q = db.session.query(Store)\
      .filter(Store.store == store_name)
  for data in store_id_q:
    get_id += data.detail_store_id
  return get_id
def store_exist(user_line_id, store_name):
  store_exist = db.session.query(Store, Favorite)\
        .join(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
        .filter(Favorite.line_id == user_line_id)\
        .filter(Store.store == store_name).count()
  return store_exist
def count_love_list(user_id):
  count_love_list = db.session.query(Favorite)\
        .filter(Favorite.line_id == user_id).count()
  return count_love_list
def count_total_row(database_name):
  count_total_row = db.session.query(database_name).count()
  return count_total_row


# ##---------------------------------------DELETE favorite list------------------------------------- 
# del_msg = '刪除最愛清單:一蘭拉麵-台灣台北本店別館'
# first_del_param = ''
# second_del_param = ''
# if ':' in del_msg:
#   first_del_param = del_msg[:del_msg.index(':')]
#   second_del_param = del_msg[del_msg.index(':')+1:]

# def get_store_id(store_name):
#   store_id_q = db.session.query(Store)\
#       .filter(Store.store == store_name)
#   for data in store_id_q:
#     get_id = data.detail_store_id
#   return get_id


#---------------------------------測試用---------------------------
@app.route('/')
def home():
  return 'hey'
@app.route('/submit', methods=['POST'])
def submit():
#---------------------------------測試用---------------------------
  if request.method =='POST':
    if first_love_param == '加到最愛清單':
      store_in_table = count_store_in_table(second_love_param)
      favorite_list_count = count_love_list(user_line_id) #how many items a user save
      already_add_store_count = store_exist(user_line_id, second_love_param) #check if the store user want to add already exist in the list
      # print(favorite_list_count)
      # print(type(user_line_id))
      # print(type(get_foreign_id))
      
      if store_in_table != 0:
        if favorite_list_count == 0 or\
          favorite_list_count != 0 and already_add_store_count == 0 and favorite_list_count <= 25 :
          get_foreign_id = get_store_id(second_love_param)#check the map_id(foreign key) of the store
          data = Favorite(user_line_id, get_foreign_id)
          # print(f'data is {data.id}')
          if data.id == None:
            try:
              db.session.add(data)
              db.session.commit()
            except IntegrityError as error:
              db.session.rollback()
          return f'成功加到最愛清單耶耶耶{data.id}'
        elif favorite_list_count > 25:
          return'最愛清單太長了要刪'
        else:
          return f'已經加過這間店到最愛清單{already_add_store_count}'
      else:
        return '加入最愛清單的店名不合法'

# #---------------------------------測試用---------------------------
@app.route('/remove', methods=['DELETE'])
def remove():
  text_d = msg.split(":")
  #first_del_param = text_d[0]
  second_del_param = text_d[1]
  detail_id = get_store_id(second_del_param)
  if detail_id != '' and store_exist(user_line_id, second_del_param) != 0:
    data = db.session.query(Favorite)\
            .filter(Favorite.detail_store_id == detail_id)\
            .filter(Favorite.line_id == user_line_id)\
            .first()
    db.session.delete(data)
    db.session.commit()
    return '成功刪除'
        
  elif store_exist(user_line_id, second_del_param) == 0: #check if the store user want to rermove already not exist in the list
    return '已不在最愛清單'
  
  else:
    return '發生錯誤'

##---------------------------------------Query love-list by userID-------------------------------------
# # l[0]:Store l[1]:favorite
#if message == '最愛清單'
def get_list_from_user_id(user_id):  
  love_list_q = db.session.query(Store,Favorite)\
    .outerjoin(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
    .filter(Favorite.line_id == user_id)
  return love_list_q

love_lst_q = get_list_from_user_id(user_line_id)
love_list = ''
for l in love_lst_q:
  love_list += f'STORE:{l[0].store},ADDRESS:{l[0].address},DISCRIPTION:{l[0].discription},TRANSPORT:{l[0].transport},MAP_REVIEW:{l[0].map_review},CITY:{l[0].province},CHECK_TAG:{l[0].soup}%'
love_list_clear = love_list.replace(u'\xa0', u' ').replace(' ','')
output_whole_love_list = convert_string_to_lst(love_list_clear,'%')
output_whole_love_list = [i for i in output_whole_love_list if i]
# for data in output_whole_love_list:
#   if data == '':
#     output_whole_love_list.remove(data)
# print(output_whole_love_list)
# print(len(output_whole_love_list))

'''

# #soup query
# soup_q = Store.query.all()
# print(soup_q)
# raw_soup = [{soup.province:soup.soup} for soup in soup_q]
# print(raw_soup)

# #https://www.geeksforgeeks.org/python-concatenate-values-with-same-keys-in-a-list-of-dictionaries/
# #Concatenate values with same keys in a list of dictionaries
# soup_data = dict()

# def concate_dicts(l, lst):
#   for dict in l:
#     for list in dict:
#       if list in lst:
#         lst[list] += (dict[list])
#       else:
#         lst[list] = dict[list]
#   return lst

# def remove_duplicate(l):
#   return list(dict.fromkeys(l))
# #remove tags:
# #ramentw
# #台灣拉麵愛好會
# #拉麵
# #(u'\xa0', u' ')
# concate_dicts(raw_soup, soup_data)
# # print(soup_data)
# for k, v in soup_data.items():
#   organized_v = v.replace('#ramentw','').replace('#台灣拉麵愛好會','').replace('#拉麵','')\
#             .replace(u'\xa0', u' ').replace(' ','').split('#')
#   soup_data[k] = organized_v

# for k, v in soup_data.items():
#   no_duplicate_v  = remove_duplicate(v)
#   no_duplicate_v.pop(0)
#   soup_data[k] = no_duplicate_v

# for k, v in soup_data.items():
#   v_string = ' '.join([str(elem) for elem in v])
#   soup_data[k] = v_string 
#   print(k, v_string)
# # print(soup_data)

# with open('soup.csv', 'w', encoding='UTF-8') as f:
#     for key in soup_data.keys():
#         f.write("%s,%s\n"%(key,soup_data[key]))


#---------------------------------測試用---------------------------
# if __name__ == 'main':
#   app.run(debug=True)
app.run(port=8000)
#---------------------------------測試用---------------------------
