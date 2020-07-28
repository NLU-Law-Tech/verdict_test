# -*-coding:UTF-8 -*-
import requests
import json
from  VerdictFormat.VerdictFormat import Labeled_to_Test
from  disassemble_judgement import disassemble_origin, disassemble_ans
import os
import shutil

# http://140.120.13.242:15005/dump_labeled_data
def get_labeled_data():
    r = requests.get('http://140.120.13.242:15005/dump_labeled_data')
    data = json.loads(r.text)
    convert_to_test_format = Labeled_to_Test(data)
    with open("db_ans.json","w",encoding='utf-8') as f:
        f.write(json.dumps(convert_to_test_format,ensure_ascii=False))

# http://140.120.13.242:15005/dump_ori_data
def get_ori_data():
    r = requests.get('http://140.120.13.242:15005/dump_ori_data')
    data_list = json.loads(r.text)
    with open("db_ori.txt","w",encoding='utf-8') as f:
        for data in data_list:
            _s = data['verdict'].replace("\r\n","\\r\\n").replace("\n",'\\n')
            f.write(json.dumps(json.loads(_s),ensure_ascii=False))
            f.write('\n')

# 資料比對(同時擁有判決書和答案的編號作保留)
def check_file():
    ori_list = []
    ans_list = []
    for filename in os.listdir('db_ori_data'):
        ori_list.append(filename.replace('.txt',""))
    for filename in os.listdir('db_ans_data'):
        ans_list.append(filename.replace('.json',""))

    # 刪除兩個list重複的地方:http://wiki.alarmchang.com/index.php?title=%E6%AF%94%E8%BC%83%E5%85%A9%E5%80%8B_List_%E4%B9%8B%E9%96%93%E7%9A%84%E5%B7%AE%E7%95%B0
    s1 = set(ori_list)
    s2 = set(ans_list)
    remove1 = list(s1.difference(s2))
    remove2 = list(s2.difference(s1))
    print('db_ori_data多的檔案:')
    print(remove1)
    print('db_ans_data多的檔案:')
    print(remove2)

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
    get_labeled_data()
    get_ori_data()
    disassemble_origin(judgement_path='db_ori.txt', save_path='db_ori_data', _id = '_id')
    disassemble_ans(ans_path='db_ans.json', save_path='db_ans_data')
    check_file()
    copy_file()