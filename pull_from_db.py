import requests
import json
from  VerdictFormat.VerdictFormat import Labeled_to_Test

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
            f.write(json.dumps(data,ensure_ascii=False))

if __name__ == "__main__":
    get_labeled_data()
    get_ori_data()

    
