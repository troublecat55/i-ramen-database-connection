#----------------定位叫使用者給位置-----------------
    elif event.message.text == "定位" :
        text_message_location = TextSendMessage(text='偷偷分享位置給我，我才能推薦附近店家給你哦！\uDBC0\uDCB9',
                                                quick_reply=QuickReply(items=[
                                                    QuickReplyButton(action=LocationAction(label="我在哪My LOC"))
                                                ]))
        line_bot_api.reply_message(event.reply_token,text_message_location) 


text_message_location = TextSendMessage(text='偷偷分享位置給我，我才能推薦附近店家給你哦！\uDBC0\uDCB9',
                                             quick_reply=QuickReply(items=[
                                                 QuickReplyButton(action=URIAction(label="看地圖",uri='https://www.google.com/maps/d/u/0/viewer?fbclid=IwAR3O8PKxMuqtqb2wMKoHKe4cCETwnT2RSCZSpsyPPkFsJ6NpstcrDcjhO2k&mid=1I8nWhKMX1j8I2bUkN4qN3-FSyFCCsCh7&ll=24.807740000000027%2C120.96740199999999&z=8'))
                                             ]))
flex_message5 = FlexSendMessage(
                    alt_text='依據你的喜好選擇吧！',
                    contents= {
                                "type": "bubble",
                                "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                    "type": "text",
                                    "text": "推薦方式 ",
                                    "weight": "bold",
                                    "size": "xl",
                                    "style": "normal",
                                    "decoration": "none",
                                    "align": "start",
                                    "gravity": "top",
                                    "color": "#876C5A",
                                    "position": "relative"
                                    },
                                    {
                                    "type": "box",
                                    "layout": "vertical",
                                    "margin": "lg",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                        "type": "text",
                                        "text": "我有口味偏好 -> 請選湯頭推薦",
                                        "size": "sm"
                                        },
                                        {
                                        "type": "text",
                                        "text": "我想來點驚喜 -> 請選直接推薦",
                                        "size": "sm"
                                        },
                                        {
                                        "type": "separator",
                                        "margin": "lg"
                                        }
                                    ]
                                    }
                                ]
                                },
                                "footer": {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                    "type": "button",
                                    "style": "primary",
                                    "height": "sm",
                                    "action": {
                                        "type": "message",
                                        "label": "湯頭推薦",
                                        "text": "湯頭推薦:"+event.message.text
                                    },
                                    "color": "#797D62",
                                    "margin": "md",
                                    "offsetTop": "none",
                                    "offsetBottom": "none",
                                    "offsetStart": "none",
                                    "offsetEnd": "none",
                                    "gravity": "center"
                                    },
                                    {
                                    "type": "button",
                                    "style": "primary",
                                    "height": "sm",
                                    "action": {
                                        "type": "message",
                                        "label": "直接推薦",
                                        "text": "直接推薦:"+event.message.text
                                    },
                                    "color": "#797D62",
                                    "margin": "md"
                                    },
                                    {
                                    "type": "spacer",
                                    "size": "sm"
                                    }
                                ]
                                }
                                
                    },
                    quick_reply= QuickReply(items=[
                            QuickReplyButton(action=LocationAction(label="我在哪My LOC"))
                    ])
                   
        )

#--------------------------------------------------------------------------------------------------------
from vincenty import vincenty
from itertools import islice

#----------------主要用在定位系統GIS的部分-----------------
def query_region_by_store_table(r):
    province_soup_q = db.session.query(Main_store, Store)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.region == r)\
                        .filter(Store.still_there == True)
    return province_soup_q
def caculate_distance(user_loc,lst):
    store_distance_name = []
    store_detail_list = []
    for r in lst:
      stores_loation_before_choice = (float(r[1].latitude),float(r[1].longtitute))
      distance = vincenty(user_loc, stores_loation_before_choice) #caculate distance
      store_distance_name.append(r[1].store)
      store_detail_list.append((distance,str(r[1].soup)))
    city_dis_dic = dict(zip(store_distance_name, store_detail_list))
    sorted_city_dis_dic = {k: v for k, v in sorted(city_dis_dic.items(), key=lambda item: item[1][0])}
    return sorted_city_dis_dic
def take(n, iterable):
    #"Return first n items of the iterable as a list"
    return list(islice(iterable, n))
def distance_template_generator(lst):
  distance_message = {
                      "type": "carousel",
                      "contents": []
                     }
  lst_to_append_stores = distance_message["contents"]
  
  for t in lst:
    #km to m
    distance_message_content = {
                            "type": "bubble",
                            "size": "mega",
                            "header": {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": t[0],
                                    "align": "start",
                                    "size": "md",
                                    "gravity": "center",
                                    "color": "#ffffff",
                                    "wrap": True
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "width": "80px",
                                    "height": "20px"
                                }
                                ],
                                "paddingTop": "15px",
                                "paddingAll": "15px",
                                "paddingBottom": "16px",
                                "backgroundColor": "#797D62"
                            },
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    
                                    {
                                        "type": "text",
                                        "text": f"距離你：{t[1][0]}公里",
                                        "size": "md",
                                        "wrap": True,
                                        "color": "#876C5A",
                                        "margin": "md",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "separator",
                                        "margin": "lg"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"風格：{t[1][1]}",
                                        "size": "md",
                                        "wrap": True,
                                        "color": "#876C5A",
                                        "margin": "md",
                                        "weight": "bold"
                                    }
                                    ],
                                    "paddingBottom": "10px"
                                }
                                ],
                                "spacing": "sm",
                                "paddingAll": "12px"
                            },
                            "footer": {
                                "type": "box",
                                "layout": "horizontal",
                                "adjustMode": "shrink-to-fit",
                                "margin": "none",
                                "align" : "start",
                                "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "message",
                                    "label": "看店家細節",
                                    "text": f"搜尋店家細節♡{t[0]}"#後面要加看前五項/看後五項按鈕
                                    },
                                    "color": "#D08C60"
                                }
                                ]
                            },
                            "styles": {
                                "footer": {
                                "separator": False
                                }
                            }

                          }
    lst_to_append_stores.append(distance_message_content)
  return distance_message

@handler.add(MessageEvent, message=LocationMessage)#定位細節
def handle_location(event):
    #---------------縣市對應北中南東-----------------
    city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
    #---------------user info-----------------
    u_lat = event.message.latitude
    u_long = event.message.longitude   
    user_address = event.message.address
    u_address = user_address.replace(' ', '')
    user_location = (u_lat, u_long)
    all_store_province = ''
    choice_nearby_city_tup = ''
    for k, v in city_name_dic.items():
      if k in u_address:
        region_value = v[0]
        all_store_province = query_region_by_store_table(region_value)
        break
      elif k not in u_address and ("臺灣" in u_address or '台灣' in u_address or '台湾' in u_address or 'Taiwan' in u_address):
        #search all
        all_store_province = province_soup_q = db.session.query(Main_store, Store)\
                          .outerjoin(Store, Store.store_id == Main_store.store_id)\
                          .filter(Store.still_there == True)
        break
      elif k not in u_address and "臺灣" not in u_address or '台灣' not in u_address or '台湾' not in u_address or 'Taiwan' not in u_address:
        all_store_province = ''
      else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "出錯惹靠腰，麻煩幫忙在使用者回報填寫出錯代碼「G1」和您的狀況" ))
    # '''
    # 算距離
    # '''
    if all_store_province == '':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "\udbc0\udcb2目前不支援離島與國外拉麵店，請到台灣本島吃拉麵~" ),
                                                                     quick_reply= QuickReply(items=[QuickReplyButton(action=LocationAction(label="再定位一次My LOC"))
    else:
        sorted_city_distance_dic = caculate_distance(user_location,all_store_province)
        if  len(sorted_city_distance_dic) >= 10:
          choice_nearby_city_tup = take(10, sorted_city_distance_dic.items())
        else:
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "出錯惹靠腰，麻煩幫忙在使用者回報填寫出錯代碼「G2」和您的狀況" ))
    
    flex_message_location = FlexSendMessage(
                                        alt_text='快回來看看我幫你找到的店家！',
                                        contents= distance_template_generator(choice_nearby_city_tup),
                                        quick_reply= QuickReply(items=[QuickReplyButton(action=LocationAction(label="再定位一次My LOC")),
                                                                       QuickReplyButton(action=URIAction(label="拉麵地圖自己找",uri=f'https://www.google.com/maps/d/u/0/viewer?fbclid=IwAR3O8PKxMuqtqb2wMKoHKe4cCETwnT2RSCZSpsyPPkFsJ6NpstcrDcjhO2k&mid=1I8nWhKMX1j8I2bUkN4qN3-FSyFCCsCh7&ll={u_lat}%2C{u_long}'))
                                                                       ]))
    line_bot_api.reply_message(event.reply_token,flex_message_location)





    #---------------------------------------------------------------------------------------------------------
    elif "搜尋店家細節♡" in event.message.text: #定位
        text_s = event.message.text.split("♡")
        store_full_name = text_s[1] 
        store_detail = query_map_review_by_full_name(store_full_name)
        output_whole_lst = convert_string_to_lst(store_detail,',')
        output_whole_lst = [i for i in output_whole_lst if i]
        if len(output_whole_lst) == 10:
            r_store = output_whole_lst[0][output_whole_lst[0].index(':')+1:]
            ad = output_whole_lst[1][output_whole_lst[1].index(':')+1:]
            dis = output_whole_lst[2][output_whole_lst[2].index(':')+1:]
            trans = output_whole_lst[3][output_whole_lst[3].index(':')+1:]
            com = output_whole_lst[4][output_whole_lst[4].index(':')+1:]
            com_lst = divide_map_review(com)
            com_lst = [v+'\n\n' if i%2 != 0 and i != len(com_lst)-1 else v+'\n' for i,v in enumerate(com_lst)]
            com_format = ''.join(map(str, com_lst))
            city_r = output_whole_lst[5][output_whole_lst[5].index(':')+1:]
            lont = output_whole_lst[6][output_whole_lst[6].index(':')+1:]
            lati = output_whole_lst[7][output_whole_lst[7].index(':')+1:]
            opent = output_whole_lst[8][output_whole_lst[8].index(':')+1:]
            flex_message8 = FlexSendMessage(
                            alt_text='快回來看看店家細節~',
                            contents={
                                        "type": "carousel",
                                        "contents": [
                                        {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                "type": "text",
                                                "text": r_store,
                                                "align": "start",
                                                "size": "md",
                                                "gravity": "center",
                                                "color": "#ffffff",
                                                "wrap": True
                                                },
                                                {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [],
                                                "width": "80px",
                                                "height": "20px"
                                                },
                                                {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                    "type": "text",
                                                    "text": "加到最愛",
                                                    "size": "sm",
                                                    "align": "center",
                                                    "offsetTop": "3px",
                                                    "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單♡"+r_store
                                                    }
                                                    }
                                                ],
                                                "width": "60px",
                                                "height": "25px",
                                                "backgroundColor": "#FFCB69",
                                                "cornerRadius": "20px",
                                                "position": "absolute",
                                                "offsetEnd": "xxl",
                                                "offsetTop": "lg"
                                                }
                                            ],
                                            "paddingTop": "15px",
                                            "paddingAll": "15px",
                                            "paddingBottom": "16px",
                                            "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                    "type": "text",
                                                    "text": "地址：",
                                                    "color": "#797D62",
                                                    "size": "md",
                                                    "wrap": True,
                                                    "weight": "bold"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": "↓↓點擊下方地址可以直接幫你傳送地圖！",
                                                    "color": "#CA8E68",
                                                    "size": "xs",
                                                    "wrap": True,
                                                    "weight": "regular"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": ad,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": f"正在幫你找到→ \n{lont}→{lati}"
                                                    },
                                                    "margin": "md"
                                                    },
                                                    {
                                                    "type": "separator",
                                                    "margin": "lg"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": "特色：",
                                                    "size": "md",
                                                    "wrap": True,
                                                    "color": "#797D62",
                                                    "margin": "md",
                                                    "weight": "bold"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": dis,
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "margin": "md"
                                                    },
                                                    {
                                                    "type": "separator",
                                                    "margin": "lg"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": "鄰近交通資訊：",
                                                    "size": "md",
                                                    "wrap": True,
                                                    "color": "#797D62",
                                                    "margin": "md",
                                                    "weight": "bold"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": trans,
                                                    "margin": "md"
                                                    },
                                                    {
                                                    "type": "separator",
                                                    "margin": "lg"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": "營業時間：",
                                                    "size": "md",
                                                    "wrap": True,
                                                    "color": "#797D62",
                                                    "margin": "md",
                                                    "weight": "bold"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": opent,
                                                    "margin": "md"
                                                    }
                                                ],
                                                "paddingBottom": "15px"
                                                }
                                            ],
                                            "spacing": "md",
                                            "paddingAll": "12px"
                                            },
                                            "footer": {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                            {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents":[
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看網友評論",
                                                    "text": f"\udbc0\udc54有人評論→ {r_store}\n\n{com_format}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看當地天氣",
                                                    "text": f"{r_store} 附近天氣搜索中→ \n{lont}→{lati}"
                                                },
                                                "color": "#D08C60"
                                                }
                                            ]
                                            },
                                            {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents":[
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看相似店鋪",
                                                    "text": f"類別搜索中→{r_store}→{city_r}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city_r
                                                },
                                                "color": "#D08C60"
                                                }
                                            ]
                                            }
                     
                                            ]
                                            },
                                            "styles": {
                                            "footer": {
                                                "separator": False
                                            }
                                            }
                                        }
                                        ]
                            }

            )

            line_bot_api.reply_message(event.reply_token,flex_message8)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼D1」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2")
        )


def soup_direct_flex(whole_input):
    flex_message = FlexSendMessage(
                    alt_text='依據你的喜好選擇吧！',
                    contents= {
                                "type": "bubble",
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                        "type": "text",
                                        "text": "推薦方式 ",
                                        "weight": "bold",
                                        "size": "xl",
                                        "style": "normal",
                                        "decoration": "none",
                                        "align": "start",
                                        "gravity": "top",
                                        "color": "#876C5A",
                                        "position": "relative"
                                        },
                                        {
                                        "type": "box",
                                        "layout": "vertical",
                                        "margin": "lg",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                            "type": "text",
                                            "text": "我有口味偏好 -> 請選湯頭推薦",
                                            "size": "sm"
                                            },
                                            {
                                            "type": "text",
                                            "text": "我想來點驚喜 -> 請選直接推薦",
                                            "size": "sm"
                                            },
                                            {
                                            "type": "separator",
                                            "margin": "lg"
                                            }
                                        ]
                                        }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {"type": "box",
                                         "layout": "horizontal",
                                         "contents": [
                                            {
                                            "type": "button",
                                            "style": "primary",
                                            "height": "sm",
                                            "action": {
                                                "type": "message",
                                                "label": "湯頭推薦",
                                                "text": "湯頭推薦:"+whole_input
                                            },
                                            "color": "#797D62",
                                            "margin": "md",
                                            "offsetTop": "none",
                                            "offsetBottom": "none",
                                            "offsetStart": "none",
                                            "offsetEnd": "none",
                                            "gravity": "center"
                                            },
                                            {
                                            "type": "button",
                                            "style": "primary",
                                            "height": "sm",
                                            "action": {
                                                "type": "message",
                                                "label": "直接推薦",
                                                "text": "直接推薦:"+whole_input
                                            },
                                            "color": "#797D62",
                                            "margin": "md"
                                            },
                                            {
                                            "type": "spacer",
                                            "size": "sm"
                                            }
                                           ]
                                        },
                                        {
                                        "type": "separator",
                                        "margin": "lg"
                                        },
                                        {
                                          "type": "box",
                                          "layout": "horizontal",
                                          "contents": [
                                            {
                                              "type": "button",
                                              "action": {
                                                "type": "message",
                                                "label": "突然想開定位GPS",
                                                "text": "定位"
                                              },
                                              "style": "primary",
                                              "height": "sm",
                                              "color": "#797D62"
                                            }
                                          ]
                                        }
                                    ]
                                }
                    }
        )
    return flex_message