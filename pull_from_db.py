# -*-coding:UTF-8 -*-
import requests
import json
from VerdictFormat.VerdictFormat import Labeled_to_Test, Multilaws_to_Normalize
from disassemble_judgement import disassemble_origin, disassemble_ans
import os
import shutil

# http://140.120.13.250:16004/dump_ori_data
def get_ori_data():
    r = requests.get('http://140.120.13.250:16004/dump_ori_data')
    data_list = json.loads(r.text)
    with open("db_ori.txt","w",encoding='utf-8') as f:
        for data in data_list:
            _s = data['verdict'].replace("\r\n","\\r\\n").replace("\n",'\\n')
            f.write(json.dumps(json.loads(_s),ensure_ascii=False))
            f.write('\n')

# http://140.120.13.250:16004/dump_labeled_data
def get_labeled_data():
    r = requests.get('http://140.120.13.250:16004/dump_labeled_data')
    data = json.loads(r.text)
    data_dict = data_to_dict(data)
    Match_laws_list = get_Match_laws_list()
    for each_verdict in data_dict:
        try:
            with open('db_ori_data' + '/' + each_verdict['doc_id'] + '.txt',"r",encoding='utf-8') as f:
                ori = json.loads(f.read())

            # print(each_verdict['doc_id'])
            # print(each_verdict['laws'])
            Normalized_laws_list = Multilaws_to_Normalize(ori['judgement'], Match_laws_list, each_verdict['laws'])
            # print(Normalized_laws_list)
            for index, context in enumerate(each_verdict['laws']):
                context['content'] = Normalized_laws_list[index]

            # print(each_verdict['laws'])
        except:
            pass

    data = dict_to_string(data_dict)
    convert_to_test_format = Labeled_to_Test(data)
    with open("db_ans.json","w",encoding='utf-8') as f:
        f.write(json.dumps(convert_to_test_format,ensure_ascii=False))

def data_to_dict(data):
    output_dict={}
    output_dict_list=[]
    for index,each_verdict in enumerate(data):
        # 讀值
        doc_id = each_verdict["doc_id"]
        identities_list = json.loads(each_verdict["identities"])
        laws_list = json.loads(each_verdict["laws"])
        name = each_verdict["name"]
        positions_list = json.loads(each_verdict["positions"])
        units_list = json.loads(each_verdict["units"])

        # 開始轉格式
        output_dict["doc_id"]=doc_id
        output_dict["id"]=each_verdict["id"]
        output_dict["identities"]=identities_list
        output_dict["laws"]=laws_list
        output_dict["name"]=name
        output_dict["positions"]=positions_list
        output_dict["units"]=units_list
        
        output_dict_list.append(output_dict.copy())
        output_dict.clear()
    return output_dict_list

def dict_to_string(data_dict):
    output={}
    output_list=[]
    for index,each_verdict in enumerate(data_dict):
        # 讀值
        doc_id = each_verdict["doc_id"]
        identities_list = json.dumps(each_verdict["identities"])
        laws_list = json.dumps(each_verdict["laws"])
        name = each_verdict["name"]
        positions_list = json.dumps(each_verdict["positions"])
        units_list = json.dumps(each_verdict["units"])

        # 開始轉格式
        output["doc_id"]=doc_id
        output["id"]=each_verdict["id"]
        output["identities"]=identities_list
        output["laws"]=laws_list
        output["name"]=name
        output["positions"]=positions_list
        output["units"]=units_list
        
        output_list.append(output.copy())
        output.clear()
    return output_list

def get_Match_laws_list():
    Match_laws_list=['中華民國刑法', '陸海空軍刑法', '國家機密保護法', '國家情報工作法', 
                    '國家安全法', '洗錢防制法', '臺灣地區與大陸地區人民關係條例', '貿易法', 
                    '組織犯罪防制條例', '人口販運防制法', '社會秩序維護法', '戰略性高科技貨品輸出入管理辦法', 
                    '山坡地保育利用條例', '公司法', '公民投票法', '公職人員選舉罷免法', 
                    '水土保持法', '水污染防治法', '水利法', '兒童及少年性交易防制條例', 
                    '空氣污染防制法', '金融控股公司法', '律師法', '政府採購法', '毒品危害防制條例',
                    '區域計畫法', '國有財產法', '票券金融管理法', '貪污治罪條例', 
                    '都市計畫法', '期貨交易法', '森林法', '稅捐稽徵法', '農田水利會組織通則',
                    '農會法', '農業金融法', '槍砲彈藥刀械管制條例', '漁會法', '銀行法',
                    '廢棄物清理法', '總統副總統選舉罷免法', '懲治走私條例', '藥事法', '證券交易法', 
                    '資恐防制法', '畜牧法', '破產法', '商標法', '商業登記法', '光碟管理條例',
                    '個人資料保護法', '健康食品管理法', '妨害國幣懲治條例', '通訊保障及監察法',
                    '化粧品衛生管理條例', '金融資產證券化條例', '食品安全衛生管理法',
                    '動物傳染病防治條例', '多層次傳銷管理法', '商業會計法', '信託業法',
                    '電信法', '動物用藥品管理法', '消費者債務清理條例', '專利師法',
                    '傳染病防治法', '嚴重特殊傳染性肺炎防治及紓困振興特別條例',
                    '農藥管理法', '飼料管理法', '管理外匯條例', '野生動物保育法',
                    '植物防疫檢疫法', '遺產及贈與稅法', '電子支付機構管理條例', 
                    '電子票證發行管理條例', '營業秘密法', '信用合作社法', '菸酒管理法', 
                    '保險法', '證券投資信託及顧問法', '證券投資人及期貨交易人保護法', '刑法', '替代役實施條例']

    return Match_laws_list

# 資料比對(同時擁有判決書和答案的編號作保留)
def check_file():
    ori_list = []
    ans_list = []
    count = 0
    for filename in os.listdir('db_ori_data'):
        ori_list.append(filename.replace('.txt',""))
        count+=1
    for filename in os.listdir('db_ans_data'):
        ans_list.append(filename.replace('.json',""))

    # 刪除兩個list重複的地方:http://wiki.alarmchang.com/index.php?title=%E6%AF%94%E8%BC%83%E5%85%A9%E5%80%8B_List_%E4%B9%8B%E9%96%93%E7%9A%84%E5%B7%AE%E7%95%B0
    s1 = set(ori_list)
    s2 = set(ans_list)
    remove1 = list(s1.difference(s2))
    remove2 = list(s2.difference(s1))
    print('db_ori_data miss match:%s'%remove1)
    print('db_ans_data miss match:%s'%remove2)
    print("pull from database:%d"%count)

    # 刪檔案:https://www.delftstack.com/zh-tw/howto/python/how-to-delete-a-file-and-directory/
    for r1 in remove1:
        if r1 != '':
            try:
                os.remove("db_ori_data/" + r1 + '.txt')
            except OSError as e:
                print(e)

    for r2 in remove2:
        if r2 != '':
            os.remove('db_ans_data/' + r2 + '.json')

# 複製那原始的7筆檔案到要做測試的資料夾中
def copy_file():
    for filename in os.listdir('test_data'):
        name = filename.replace('.txt',"")
        if os.path.isfile('db_ori_data/' + filename):
            continue
        else:
            shutil.copy('test_data/' + filename, 'db_ori_data')
            shutil.copy('ans_data/' + name + '.json', 'db_ans_data')

if __name__ == "__main__":
    if os.path.isdir('db_ans_data'):
        shutil.rmtree('db_ans_data')
    if os.path.isdir('db_ori_data'):
        shutil.rmtree('db_ori_data')
    get_ori_data()
    disassemble_origin(judgement_path='db_ori.txt', save_path='db_ori_data', _id = '_id')
    get_labeled_data()
    disassemble_ans(ans_path='db_ans.json', save_path='db_ans_data')
    check_file()
    copy_file()