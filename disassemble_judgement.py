# -*-coding:UTF-8 -*-
import json

# 將判決書拆成一篇篇的檔案
def disassemble_origin(judgement_path='new2000.txt'):
    with open(judgement_path,'r',encoding='utf-8') as f:
        for doc in f.readlines():
            doc = json.loads(doc)
            with open('judgement_data/' + doc['_id'] + '.txt','w',encoding='utf-8') as f2:
                f2.write(json.dumps(doc,ensure_ascii=False,indent=None))
                f2.close()

    f.close()

# 將那7篇測試判決書從原始資料中拆成一篇篇的檔案
def disassemble_test(judgement_path='new2000.txt'):
    id_list = ['5d30da9fcbd1c48dc9762383', '5d30da9fcbd1c48dc9762393', '5d30da9fcbd1c48dc97623c7', '5d30da9fcbd1c48dc97623d3', '5d30da9fcbd1c48dc9762417', '5d30da9fcbd1c48dc976244e', '5d30da9fcbd1c48dc97624de']
    with open(judgement_path,'r',encoding='utf-8') as f:
        for doc in f.readlines():
            doc = json.loads(doc)
            if doc['_id'] in id_list:
                with open('test_data/' + doc['_id'] + '.txt','w',encoding='utf-8') as f2:
                    f2.write(json.dumps(doc,ensure_ascii=False,indent=None))
                    f2.close()

    f.close()

if __name__ == "__main__":
    disassemble_origin()
    disassemble_test()