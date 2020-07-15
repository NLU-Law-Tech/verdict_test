import json
import numpy

# ans_list及predict_list為整串預測出的答案list
# 計算每一篇判決書之分數
def get_judgement(id, judgement_path='new2000.txt'):
    with open(judgement_path,'r',encoding='utf-8') as f:
        for doc in f.readlines():
            doc = json.loads(doc)
            if id == doc['_id']:
                return doc['judgement']
    return ''

def Score_calculate(ans_list,predict_list):
    temp_em = 0
    temp_inter = 0
    if ans_list == predict_list:
        temp_em += 1
    # set(ans_list).intersection(set(predict_list)) # 交集個數
    if len(ans_list) == 0:
        temp_inter  = 1
    else:
        temp_inter += len(set(ans_list).intersection(set(predict_list))) / len(ans_list)
    return temp_em,temp_inter

def main(ans_file='ans.json',predict_file='predict.json'):
    with open(ans_file, 'r', encoding='utf-8') as fp:
        ans = json.loads(fp.read())
    with open(predict_file, 'r', encoding='utf-8') as fp:
        predict = json.loads(fp.read())
    # 總分 list
    em_total = []
    inter_total = []
    # 單位 職稱與法條的個別分數 list
    em_loc = []
    em_tit = []
    em_law = []
    inter_loc = []
    inter_tit = []
    inter_law = []
    for ans_defendant in ans:
        for pred_defendant in predict:
            if ans_defendant['content_id'] == pred_defendant['content_id']:  
                # 每篇的分數 
                em_loc_score = 0
                em_title_score = 0
                em_laws_score = 0
                inter_loc_score = 0
                inter_title_score = 0
                inter_laws_score = 0
                if ans_defendant['name'] == pred_defendant['name']:
                    em_loc_temp, inter_loc_temp = Score_calculate(ans_defendant['job_location'],pred_defendant['job_location'])
                    em_tit_temp, inter_tit_temp = Score_calculate(ans_defendant['job_title'],pred_defendant['job_title'])
                    em_law_temp, inter_law_temp = Score_calculate(ans_defendant['laws'],pred_defendant['laws'])
                    
                    em_loc_score += em_loc_temp
                    em_title_score += em_tit_temp
                    em_laws_score += em_law_temp
                    inter_loc_score += inter_loc_temp
                    inter_title_score += inter_tit_temp
                    inter_laws_score += inter_law_temp
                    # 印出每個被告單位 職稱及法條的分數
                    # print("id:",ans_defendant['content_id'])
                    # print(em_loc_score, em_title_score, em_laws_score)
                    # print(inter_loc_score, inter_title_score, inter_laws_score)
                    
                    em_loc.append(em_loc_score)
                    em_tit.append(em_title_score)
                    em_law.append(em_laws_score)
                    inter_loc.append(inter_loc_score)
                    inter_tit.append(inter_title_score)
                    inter_law.append(inter_laws_score)
                    
                    em_total += [em_loc_score,em_title_score,em_laws_score]
                    inter_total += [inter_loc_score,inter_title_score,inter_laws_score]
    # 印出個別分數
    print('em分數: ')
    print("單位: " + "{:.2f}".format(numpy.mean(em_loc)),"職稱: " + "{:.2f}".format(numpy.mean(em_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(em_law)))
    print('交集分數: ')
    print("單位: " + "{:.2f}".format(numpy.mean(inter_loc)),"職稱: " + "{:.2f}".format(numpy.mean(inter_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(inter_law)))
    # 印出總分
    print('===============')
    print('總分')
    print("{:.2f}".format((numpy.mean(em_total))))
    print("{:.2f}".format(numpy.mean(inter_total)))

if __name__ == "__main__":
    main()