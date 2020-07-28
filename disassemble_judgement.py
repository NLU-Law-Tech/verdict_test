# -*-coding:UTF-8 -*-
import json
import os

# 將判決書拆成一篇篇的檔案
def disassemble_origin(judgement_path='new2000.txt', save_path='judgement_data', _id = '_id'):
    if not os.path.isdir(save_path):
        os.mkdir(save_path)

    with open(judgement_path,'r',encoding='utf-8') as f:
        for doc in f.readlines():
            doc = json.loads(doc)
            with open(save_path + '/' + doc[_id] + '.txt','w',encoding='utf-8') as f2:
                f2.write(json.dumps(doc,ensure_ascii=False,indent=None))

# 將那7篇測試判決書從原始資料中拆成一篇篇的檔案
def disassemble_test(judgement_path='new2000.txt'):
    id_list = ['5d30da9fcbd1c48dc9762383', '5d30da9fcbd1c48dc9762393', '5d30da9fcbd1c48dc97623c7', '5d30da9fcbd1c48dc97623d3', '5d30da9fcbd1c48dc9762417', '5d30da9fcbd1c48dc976244e', '5d30da9fcbd1c48dc97624de']
    with open(judgement_path,'r',encoding='utf-8') as f:
        for doc in f.readlines():
            doc = json.loads(doc)
            if doc['_id'] in id_list:
                with open('test_data/' + doc['_id'] + '.txt','w',encoding='utf-8') as f2:
                    f2.write(json.dumps(doc,ensure_ascii=False,indent=None))

# 將答案拆成一篇篇的檔案
def disassemble_ans(ans_path='ans.json', save_path='ans_data'):
    if not os.path.isdir(save_path):
        os.mkdir(save_path)

    with open(ans_path,'r',encoding='utf-8') as f:
        all_ans = json.loads(f.read())
        id_dict = {}

        for ans in all_ans:
            if ans['content_id'] not in id_dict.keys():
                id_dict[ans['content_id']] = []
            id_dict[ans['content_id']].append(ans)

    for content_id in id_dict.keys():
        with open(save_path + '/' + content_id + '.json','w',encoding='utf-8') as f2:
            f2.write(json.dumps(id_dict[content_id],ensure_ascii=False,indent=None))

if __name__ == "__main__":
    disassemble_origin()
    disassemble_test()
    disassemble_ans()