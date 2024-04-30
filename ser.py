import io
import re
import time
import wave

from flask import Flask
# key是更正后的词，value是要做转换的词的list
SYNONYM_TABLE_ORIGIN = {
    "杯子": ["鼻子"],
    "水壶": ["水浒"],
    "白板": ["台版"],
    "黑板刷": ["黑板选"],
    "微波炉": ["微波楼"],
    "咖啡机": ["他飞机"],
    "椅子": ["一只", "一直", "已知"],
    "瓶子": ["停止", "亭子"],
    "盆栽": ["横灾", "恒栽"],
    "箱子": ["祥子", "翔子"],
    "排插": ["排叉", "插板", "还差", "台差", "排查"],
}
app = Flask(__name__)
# 转换后得到的dict形如{"已知": "椅子", "停止": "瓶子", "亭子": "瓶子"}，目的是提高搜索效率(O(n)->O(1))
# 不直接写成这种形式是因为它不方便扩充，可读性差
SYNONYM_TABLE = {}
for key, values in SYNONYM_TABLE_ORIGIN.items():
    for val in values:
        SYNONYM_TABLE[val] = key

EN_ZH_MAPPING = {
    "person": "人",
    "bicycle": "自行车",
    "car": "汽车",
    "motorbike": "摩托车",
    "aeroplane": "飞机",
    "bus": "公交车",
    "train": "火车",
    "truck": "货车",
    "boat": "船",
    "traffic light": "红绿灯",
    "fire hydrant": "消防栓",
    "stop sign": "停车标志",
    "parking meter": "停车",
    "bench": "凳子",
    "bird": "鸟",
    "cat": "毛",
    "dog": "狗",
    "horse": "马",
    "sheep": "羊",
    "cow": "牛",
    "elephant": "象",
    "bear": "熊",
    "zebra": "斑马",
    "giraffe": "长颈鹿",
    "backpack": "背包",
    "umbrella": "雨伞",
    "handbag": "手提包",
    "tie": "领带",
    "suitcase": "手提箱",
    "frisbee": "frisbee",
    "skis": "滑雪板",
    "snowboard": "滑雪板",
    "sports ball": "球",
    "kite": "风筝",
    "baseball bat": "球棒",
    "baseball glove": "棒球手套",
    "skateboard": "滑板",
    "surfboard": "冲浪板",
    "tennis racket": "网球拍",
    "bottle": "瓶子",
    "wine glass": "酒杯",
    "cup": "杯子",
    "fork": "叉子",
    "knife": "小刀",
    "spoon": "勺子",
    "bowl": "碗",
    "banana": "香蕉",
    "apple": "苹果",
    "sandwich": "三明治",
    "orange": "橘子",
    "broccoli": "西兰花",
    "carrot": "胡萝卜",
    "hot dog": "热狗",
    "pizza": "披萨",
    "donut": "甜甜圈",
    "cake": "蛋糕",
    "chair": "椅子",
    "sofa": "沙发",
    "pottedplant": "盆栽",
    "bed": "床",
    "diningtable": "桌子",
    "toilet": "厕所",
    "tvmonitor": "显示器",
    "laptop": "笔记本电脑",
    "mouse": "鼠标",
    "remote": "遥控器",
    "keyboard": "键盘",
    "cell phone": "手机",
    "microwave": "微波炉",
    "oven": "烤箱",
    "toaster": "面包机",
    "sink": "水槽",
    "refrigerator": "冰箱",
    "book": "书",
    "clock": "钟",
    "vase": "花瓶",
    "scissors": "剪刀",
    "teddy bear": "泰迪熊",
    "hair drier": "电吹风",
    "toothbrush": "牙刷",
    "bin": "垃圾桶",
    "blackboard eraser": "黑板擦",
    "box": "箱子",
    "coffee beans": "咖啡豆",
    "coffee grinder": "磨豆机",
    "coffee machine": "咖啡机",
    "kettle": "水壶",
    "kitchen counter": "厨柜",
    "power strip": "排插",
    "projector": "投影仪",
    "tap": "水龙头",
    "whiteboard": "白板",
    "ground": "地板",
}



sym = {'人': ['人'],
 '自行车': ['自行车', '单车'],
 '汽车': ['汽车'],
 '摩托车': ['摩托车', '摩托'],
 '飞机': ['飞机', '直升机', '客机', '滑翔机', '军用飞机'],
 '公交车': ['公交车', '公交',  '公共汽车'],
 '火车': ['火车'],
 '货车': ['货车', '面包车', '货柜车', '卡车', '罐车'],
 '船': ['船', '船只', '艇', '大船', '运输船'],
 '红绿灯': ['红绿灯', '信号灯', '交通灯'],
 '消防栓': ['消防栓'],
 '停车标志': [],
 '停车': ['停车'],
 '凳子': ['凳子'],
 '鸟': ['鸟'],
 '毛': ['毛'],
 '狗': ['狗'],
 '马': ['马'],
 '羊': ['羊'],
 '牛': ['牛'],
 '象': ['象'],
 '熊': ['熊'],
 '斑马': ['斑马'],
 '长颈鹿': ['长颈鹿'],
 '背包': ['背包', '手提包', '公文包', '皮包'],
 '雨伞': ['雨伞', '伞'],
 '手提包': ['手提包', '挎包', '皮包'],
 '领带': ['领带'],
 '手提箱': ['手提箱', '箱子', '皮箱'],
 'frisbee': [],
 '滑雪板': ['滑雪板'],
 '球': ['球', '皮球'],
 '风筝': ['风筝'],
 '球棒': ['球棒'],
 '棒球手套': [],
 '滑板': ['滑板'],
 '冲浪板': ['冲浪板'],
 '网球拍': ['网球拍','拍子'],
 '瓶子': ['瓶子', '玻璃瓶'],
 '酒杯': ['酒杯'],
 '杯子': ['杯子', '玻璃杯', '水杯', '茶杯','塑料杯','纸杯'],
 '叉子': ['叉子'],
 '小刀': ['小刀','刀'],
 '勺子': ['勺子','汤勺'],
 '碗': ['碗'],
 '香蕉': ['香蕉'],
 '苹果': ['苹果'],
 '三明治': ['三明治'],
 '橘子': ['橘子', '橙子'],
 '西兰花': ['西兰花'],
 '胡萝卜': ['胡萝卜','萝卜'],
 '热狗': ['热狗', '香肠'],
 '披萨': ['披萨'],
 '甜甜圈': [],
 '蛋糕': ['蛋糕', '面包', '软糖', '松饼'],
 '椅子': ['椅子',  '凳子', '长椅'],
 '沙发': ['沙发'],
 '盆栽': ['盆栽', '盆景', '花草', '花盆'],
 '床': ['床'],
 '桌子': ['桌子', '茶桌', '茶几'],
 '厕所': ['厕所', '洗手间', '卫生间'],
 '显示器': ['显示器', '显示屏', '液晶', 'LCD', '触摸屏'],
 '笔记本电脑': ['笔记本电脑', '笔记型电脑', '笔记本', '台式机', '手提电脑'],
 '鼠标': ['鼠标', '滑鼠'],
 '遥控器': ['遥控器'],
 '键盘': ['键盘', '按键'],
 '手机': ['手机', '智能手机'],
 '微波炉': ['微波炉'],
 '烤箱': ['烤箱', '烤炉'],
 '面包机': ['面包机', '微波炉', '电磁炉'],
 '水槽': ['水槽', '水箱', '水缸'],
 '冰箱': ['冰箱', '冰柜'],
 '书': ['书',  '此书', '该书','书本'],
 '钟': ['钟','时钟'],
 '花瓶': ['花瓶', '装饰品','花盆'],
 '剪刀': ['剪刀', '小刀', '钳子', '刀片'],
 '泰迪熊': ['泰迪熊', '玩偶', '布偶'],
 '电吹风': ['电吹风'],
 '牙刷': ['牙刷', '刷子'],
 '垃圾桶': ['垃圾桶', '垃圾箱', '垃圾筒'],
 '黑板擦': [],
 '箱子': ['箱子', '袋子','手提箱', '皮箱'],
 '咖啡豆': ['咖啡豆'],
 '磨豆机': [],
 '咖啡机': ['咖啡机', '咖啡壶'],
 '水壶': ['水壶', '壶','水瓶'],
 '厨柜': ['厨柜', '柜子'],
 '排插': ['排插','插座'],
 '投影仪': ['投影仪', '投影机', '背投','外设'],
 '水龙头': ['水龙头','龙头'],
 '白板': ['白板',  '画板'],
 '地板': ['地板',  '地砖']}


COLOR_MAPPING = {
    "green": "绿色",
    "red": "红色",
    "purple": "紫色",
    "black": "黑色",
    "yellow": "黄色",
    "blue": "蓝色",
    "white": "白色"
}

TEST_INFO = [{"category": "kettle", "color": "black", "on": "diningtable", "near": "coffee machine", "material": ""},
             {"category": "cup", "color": "", "on": "kitchen counter", "near": "projector", "material": "塑料或金属"},
             {"category": "cup", "color": "white", "on": "diningtable", "near": "", "material": "塑料或金属"},
             {"category": "cup", "color": "white", "on": "kitchen counter", "near": "", "material": "塑料或金属"}]

def get_tp(x):
    all = []
    #print("桌子"in x)
    for i in EN_ZH_MAPPING.values():
        #print(i)
        for j in sym[i]:
          if(j in x):
            all.append(i)
            break
        if(i in x):
          all.append(i)
    all=list(set(all))
    print(all)
    if(len(all)>1):
        return -1
    if(len(all)==0):
        return None
    return all[0]

def get_color(x):
    all = []
    for i in COLOR_MAPPING.values():
        if(i in x):
            all.append(i)
    if(len(all)>1):
        return -1
    if(len(all)==0):
        return None
    return all[0]

def visual_to_sentence(query, objects):
    intent = query["intent"]["name"]
    query_category = get_tp(query["text"])
    query_color = get_color(query["text"])
    # intent, query_category, query_color = [query[i] for i in ("intent", "object", "color",)]
    if(query_category==-1 or query_color==-1):
        return "这个问题太复杂了，请简单一点提问哦！"
    if intent == "list_all":
        all_objects = {}
        for obj in objects:
            category = EN_ZH_MAPPING[obj["category"]]
            all_objects[category] = all_objects[category] + 1 if category in all_objects.keys() else 1

        return "我看到了" + "，".join([f"{n}个{o}" for o, n in all_objects.items()]) + "。"

    import jieba.posseg as pseg #词性标注
     
    sent = query["text"]
    ok = 0
    lst ="org" 
    words = pseg.cut(sent)
    for word, flag in words:
        if(flag == 'n' and word!='颜色'):
            ok = 1
            lst = word
            print(word)
            
    if ok==0:
        return "对不起，我没听清楚您的问题。"
    
    if(query_category is None or len(query_category)==0):
        query_category = lst

    if intent == "ask_object_position":
        matched_objects = {"on": {}, "near": {}}
        matched_num = 0

        # sequentially search objects that match query
        for obj in objects:
            category, on, near = [EN_ZH_MAPPING[obj[i]] if obj[i] else None for i in ("category", "on", "near")]
            if(len(obj["color"])==0 ):
              color = obj["color"]
            else:
              print(obj["color"])
              color = COLOR_MAPPING[obj["color"]]

            # query的物体出现在objects中 AND (query中未指定color OR query指定了color且与物体的color一致) 视为成功匹配
            if query_category == category and (not query_color or query_color == color):
                matched_num += 1
                if on:
                    matched_objects["on"][on] = matched_objects["on"][on] + 1 if on in matched_objects[
                        "on"].keys() else 1
                elif near:
                    matched_objects["near"][near] = matched_objects["near"][near] + 1 if near in matched_objects[
                        "near"].keys() else 1

        if matched_num == 0:
            if query_color:
                return f"抱歉，我没有看到{query_color}的{query_category}。"
            else:
                return f"抱歉，我没有看到{query_category}。"
        elif matched_num == 1:  # 匹配的物体只有一个，则不回复它的数量
            object_description = ""
            for o in matched_objects["on"].keys():
                object_description += f"在{o}上"

            for n in matched_objects["near"].keys():
                object_description += f"在{n}旁边"

            if query_color:
                return f"{query_color}的{query_category}{object_description}。"
            else:
                return f"{query_category}{object_description}。"
        else:
            object_description = ""
            on_dict = matched_objects["on"]
            near_dict = matched_objects["near"]

            if len(on_dict) + len(near_dict) == 1:  # 所有物体都出现在同一个参照物的上面或旁边，就用总结性的句子
                for o in on_dict.keys():
                    object_description += f"，它们都在{o}上面"

                for n in near_dict.keys():
                    object_description += f"，它们都在{n}旁边"
            else:  # 超过2个参照物，用排比的句子
                for o in on_dict.keys():
                    object_description += f"，在{o}上的有{matched_objects['on'][o]}个"

                for n in near_dict.keys():
                    object_description += f"，在{n}旁边的有{matched_objects['near'][n]}个"

            if query_color:
                return f"有{matched_num}个{query_color}的{query_category}{object_description}。"
            else:
                return f"有{matched_num}个{query_category}{object_description}。"

    elif intent == "ask_object_color":
        colors_of_matched = {}
        unknown_num = 0
        for obj in objects:
            category, on, near = [EN_ZH_MAPPING[obj[i]] if obj[i] else None for i in ("category", "on", "near")]
            color = obj["color"]

            if query_category == category:
                if color:
                    colors_of_matched[color] = colors_of_matched[color] + 1 if color in colors_of_matched.keys() else 1
                else:
                    unknown_num += 1

        matched_num = sum(list(colors_of_matched.values()))
        if matched_num + unknown_num == 0:
            return f"抱歉，我没有看到{query_category}。"
        elif matched_num == 0:
            return f"我看到了{matched_num + unknown_num}个{query_category}，但是我不认识它们的颜色。"
        elif matched_num == 1:
            return f"{query_category}是{list(colors_of_matched.keys())[0]}的。"
        elif len(colors_of_matched) == 1 and unknown_num == 0:
            color_description = ""
            for c in colors_of_matched.keys():
                color_description += f"它们都是{c}的"
            return f"有{matched_num}个{query_category}，{color_description}。"
        else:
            color_description = ""
            for c in colors_of_matched.keys():
                color_description += f"，{c}的有{colors_of_matched[c]}个"

            ret = f"有{matched_num + unknown_num}个{query_category}{color_description}。"
            if unknown_num > 0:
                ret += f"还有{unknown_num}个不知道是啥颜色。"

            return ret

    elif intent == "ask_object_quantity":
        counter = 0
        for obj in objects:
            category, on, near = [EN_ZH_MAPPING[obj[i]] if obj[i] else None for i in ("category", "on", "near")]
            color = obj["color"]

            if query_category == category and (not query_color or query_color == color):
                counter += 1

        if counter == 0:
            if query_color:
                return f"抱歉，我没有看到{query_color}的{query_category}。"
            else:
                return f"抱歉，我没有看到{query_category}。"
        else:
            if query_color:
                return f"{query_color}的{query_category}有{counter}个。"
            else:
                return f"{query_category}有{counter}个。"

    elif intent == "ask_object_material":
        for obj in objects:
            category, on, near = [EN_ZH_MAPPING[obj[i]] if obj[i] else None for i in ("category", "on", "near")]
            material = obj["material"]
            color = obj["color"]

            if query_category == category:
                if query_color:
                    if color and color == query_color:
                        if material:
                            return f"{query_color}的{query_category}是{material}的。"
                        else:
                            return f"抱歉，我看不出来{query_color}的{query_category}是什么材料做的噢。"
                    else:
                        break
                else:
                    if material:
                        return f"{query_category}是{material}的。"
                    else:
                        return f"抱歉，我看不出来{query_category}是什么材料做的噢。"

        if query_color:
            return f"抱歉，我没有看到{query_color}的{query_category}。"
        else:
            return f"抱歉，我没有看到{query_category}。"

    elif intent == "ask_object_function":
        for obj in objects:
            category = EN_ZH_MAPPING[obj["category"]]
            func = obj["function"]
            if category == query_category:
                return f"{query_category}可以用来{func}。"

        return f"抱歉，我没有看到{query_category}，所以我不知道它有什么用。"

    elif intent == "list_whats_on":
        on_objects = {}
        for obj in objects:
            category, on = [EN_ZH_MAPPING[obj[i]] if obj[i] else None for i in ("category", "on")]
            if on == query_category:
                on_objects[category] = on_objects[category] + 1 if category in on_objects.keys() else 1

        if len(on_objects) > 0:
            sentence = "，".join([f"{on_num}个{on}" for on, on_num in on_objects.items()])
            return f"{query_category}的上面有{sentence}。"
        else:
            return f"对不起，我不知道{query_category}上面有什么东西。"

    elif intent == "list_whats_near":
        near_objects = {}
        for obj in objects:
            category, near = [EN_ZH_MAPPING[obj[i]] if obj[i] else None for i in ("category", "near")]
            if near == query_category:
                near_objects[category] = near_objects[category] + 1 if category in near_objects.keys() else 1

        if len(near_objects) > 0:
            sentence = "，".join([f"{near_num}个{near}" for near, near_num in near_objects.items()])
            return f"{query_category}的旁边有{sentence}。"
        else:
            return f"对不起，我不知道{query_category}旁边有什么东西。"

    else:
        return "对不起，我暂时无法回答这个问题。"



@app.route("/answer",methods=["GET"])
def answer():
  from flask import Flask, request
  import requests
  intxt =  request.args.get('text')
  headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
      
  
  data = '{"text":"'+intxt+'"}'
      #print(data)
  data= data.encode('utf-8')
  response = requests.post('http://localhost:5005/model/parse', headers=headers, data=data)

  import json
  
  test_query = json.loads(response.text)
      #print(test_query)
  if(test_query["intent"]["name"]!='chat'):
      return(visual_to_sentence(test_query, TEST_INFO))
  else:
      return(aichat(intxt))

def aichat(intxt):

  def token():
    Key = 'OCOTNtabD8TSHow0sFQm5eTZ'
    Secret = 'rgDQHx2fOc1decsSfpwIrfWLGDVZG11p'
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + Key + '&client_secret=' + Secret
    result = requests.post(url)
    result = result.json()
    access_token = result['access_token']
    return access_token
  
  # encoding:utf-8
  import requests
  import random
  access_token = token()
  print(access_token)
  url = 'https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token=' + access_token
  post_data = ("{\"version\":\"3.0\",\"service_id\":\"S92647\",\"session_id\":\"\",\"log_id\":\"7758521\",\"request\":{\"terminal_id\":\"88888\",\"query\":\"%s\"}}"%(str(intxt))).encode('utf-8')
  print(post_data)
  
  
  headers = {'content-type': 'application/x-www-form-urlencoded'}
  response = requests.post(url, data=post_data, headers=headers)
  result = response.json()
  result = result['result']['responses'][0]['actions'][0]['say']
  return result




if __name__ == "__main__":



    app.run(host="localhost", port=5002)


# import requests
#
# headers = {
#     'Content-Type': 'application/x-www-form-urlencoded',
# }
#
# data = '{"text":"hello"}'
#
# response = requests.post('http://localhost:5005/model/parse', headers=headers, data=data)
# import json
# json1 = json.loads(response.text)
# print(json1)