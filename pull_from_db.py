import requests
import json
from  VerdictFormat.VerdictFormat import Labeled_to_Test

# http://140.120.13.242:15005/dump_labeled_data
# http://140.120.13.242:15005/dump_ori_data
if __name__ == "__main__":
    r = requests.get('http://140.120.13.242:15005/dump_labeled_data')
    data = json.loads(r.text)
    convert_to_test_format = Labeled_to_Test(data)
    with open("db_ans.json","w",encoding='utf-8') as f:
        f.write(json.dumps(convert_to_test_format,ensure_ascii=False))
