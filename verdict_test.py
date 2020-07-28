import json
import numpy
from fuzzywuzzy import fuzz

# ans_list及predict_list為整串預測出的答案list
# 計算每一篇判決書之分數
def get_judgement(id, judgement_path='test_data'):
    try:
        with open(judgement_path+'/' + id + '.txt','r',encoding='utf-8') as f:
            for doc in f.readlines():
                doc = json.loads(doc)
                return doc['judgement']
    except:
        return ''    

def exactmatch(ans_list, predict_list):
    temp_em = 0
    if ans_list == predict_list:
        temp_em += 1
    return temp_em

# def fuzzymatch(ans_list, predict_list, threshold):
#     temp_fuzzy = 0
#     if fuzz.ratio(ans_list, predict_list) > threshold:
#         temp_fuzzy += 1
#     return temp_fuzzy

def fuzzymatch(ans_list, predict_list):
    temp_fuzzy = 0
    if ans_list == predict_list:
        temp_fuzzy += 1
    else:    
        for subpredict in predict_list:
            for subans in ans_list:
                if all(pred in subpredict for pred in subans):
                    break
        try:
            temp_fuzzy = temp_fuzzy/len(ans_list)
        except:
            temp_fuzzy = 0
    return temp_fuzzy

def intersect(ans_list, predict_list):
    temp_inter = 0
    if len(ans_list) == 0:
        temp_inter = 0
    else:
        temp_inter += len(set(ans_list).intersection(set(predict_list))) / len(ans_list)
    return temp_inter

def precision(ans_list, predict_list):
    temp_precision = 0
    ans = set(ans_list)
    predict = set(predict_list)
    tp = len(ans & predict)
    fp = len(predict) - tp
    if len(ans_list) == 0:
        temp_precision = 0
    else:
        try: # tp > 0
            temp_precision = float(tp/(tp+fp))
        except:
            temp_precision = 0
    return temp_precision

def recall(ans_list, predict_list):
    temp_recall = 0
    ans = set(ans_list)
    predict = set(predict_list)
    tp = len(ans & predict)
    fn = len(ans) - tp
    if len(ans_list) == 0:
        temp_recall = 0
    else:
        try: # tp > 0
            temp_recall = float(tp/(tp+fn))
        except:
            temp_recall = 0
    return temp_recall

def f1score(ans_list, predict_list):
    temp_f1 = 0
    prec = precision(ans_list, predict_list)
    rec = recall(ans_list, predict_list)
    try:
        temp_f1 = 2 * prec * rec/ (prec + rec)
    except ZeroDivisionError:
        temp_f1 = 0
    return temp_f1 

# 統計判決書有幾篇幾個被告
def countup(ans_file = 'ans.json'):
    with open(ans_file, 'r', encoding = 'utf-8') as fp:
        ans = json.loads(fp.read())

    verdict_list = []
    verdict_name = []
    for content in ans:
        for key, value in content.items():
            if key == 'content_id':
                verdict_list.append(value)
            elif key == 'name':
                verdict_name.append(value)
    print('判決書數量 : ' + str(len(set(verdict_list))))
    print('被告數量   : ' + str(len(verdict_name)))

def score_calculate(ans_list, predict_list):

    temp_em = 0
    temp_em += exactmatch(ans_list, predict_list)

    temp_inter = 0
    temp_inter += intersect(ans_list, predict_list)

    temp_precision = 0
    temp_precision += precision(ans_list, predict_list)

    temp_recall = 0
    temp_recall += recall(ans_list, predict_list)

    temp_f1 = 0
    temp_f1 += f1score(ans_list, predict_list)

    temp_fuzzy = 0
    # temp_fuzzy += fuzzymatch(ans_list, predict_list, 50)
    temp_fuzzy += fuzzymatch(ans_list, predict_list)

    return temp_em, temp_inter, temp_precision, temp_recall, temp_f1, temp_fuzzy

def main(ans_file = 'ans.json', predict_file = 'predict.json'):

    with open(ans_file, 'r', encoding = 'utf-8') as fp:
        ans = json.loads(fp.read())
    with open(predict_file, 'r', encoding = 'utf-8') as fp:
        predict = json.loads(fp.read())

    # 總分 list
    em_total, inter_total, prec_total, rec_total, f1_total, fuzzy_total = ([] for _ in range(6))

    # 單位 職稱與法條的個別分數 list
    em_loc, em_tit, em_law = ([] for _ in range(3))
    inter_loc, inter_tit, inter_law = ([] for _ in range(3))
    prec_loc, prec_tit, prec_law = ([] for _ in range(3))
    rec_loc, rec_tit, rec_law = ([] for _ in range(3))
    f1_loc, f1_tit, f1_law = ([] for _ in range(3))
    fuzzy_loc, fuzzy_tit, fuzzy_law = ([] for _ in range(3))

    for ans_defendant in ans:
        for pred_defendant in predict:
            if ans_defendant['content_id'] == pred_defendant['content_id']:
            
                # 每篇的分數 
                em_loc_score = em_title_score = em_laws_score = 0
                inter_loc_score = inter_title_score = inter_laws_score = 0
                precision_loc_score = precision_title_score = precision_laws_score = 0
                recall_loc_score = recall_title_score = recall_laws_score = 0
                f1_loc_score = f1_title_score = f1_laws_score = 0
                fuzzy_loc_score = fuzzy_title_score = fuzzy_laws_score = 0

                if ans_defendant['name'] == pred_defendant['name']:

                    em_loc_temp, inter_loc_temp, prec_loc_temp, rec_loc_temp, f1_loc_temp, fuzzy_loc_temp = score_calculate(ans_defendant['job_location'], pred_defendant['job_location'])
                    em_tit_temp, inter_tit_temp, prec_tit_temp, rec_tit_temp, f1_tit_temp, fuzzy_tit_temp = score_calculate(ans_defendant['job_title'], pred_defendant['job_title'])
                    em_law_temp, inter_law_temp, prec_law_temp, rec_law_temp, f1_law_temp, fuzzy_law_temp = score_calculate(ans_defendant['laws'], pred_defendant['laws'])


                    em_loc_score, em_title_score, em_laws_score = em_loc_temp+em_loc_score, em_tit_temp+em_title_score, em_law_temp+em_laws_score
                    inter_loc_score, inter_title_score, inter_laws_score = inter_loc_temp+inter_loc_score, inter_tit_temp+inter_title_score, inter_law_temp+inter_laws_score
                    precision_loc_score, precision_title_score, precision_laws_score = prec_loc_temp+precision_loc_score, prec_tit_temp+precision_title_score, prec_law_temp+precision_laws_score
                    recall_loc_score, recall_title_score, recall_laws_score = rec_loc_temp+recall_loc_score, rec_tit_temp+recall_title_score, rec_law_temp+recall_laws_score
                    f1_loc_score, f1_title_score, f1_laws_score = f1_loc_temp+f1_loc_score, f1_tit_temp+f1_title_score, f1_law_temp+f1_laws_score
                    fuzzy_loc_score, fuzzy_title_score, fuzzy_laws_score = fuzzy_loc_temp+fuzzy_loc_score, fuzzy_tit_temp+fuzzy_title_score, fuzzy_law_temp+fuzzy_laws_score

                    # 印出每個被告單位 職稱及法條的分數
                    # print("id:",ans_defendant['content_id'])
                    # print(em_loc_score, em_title_score, em_laws_score)
                    # print(inter_loc_score, inter_title_score, inter_laws_score)
                    # print(precision_loc_score, precision_title_score, precision_laws_score)
                    # print(recall_loc_score, recall_title_score, recall_laws_score)
                    # print(f1_loc_score, f1_title_score, f1_laws_score)

                    em_loc.append(em_loc_score)
                    em_tit.append(em_title_score)
                    em_law.append(em_laws_score)

                    inter_loc.append(inter_loc_score)
                    inter_tit.append(inter_title_score)
                    inter_law.append(inter_laws_score)

                    prec_loc.append(precision_loc_score)
                    prec_tit.append(precision_title_score)
                    prec_law.append(precision_laws_score)

                    rec_loc.append(recall_loc_score)
                    rec_tit.append(recall_title_score)
                    rec_law.append(recall_laws_score)

                    f1_loc.append(f1_loc_score)
                    f1_tit.append(f1_title_score)
                    f1_law.append(f1_laws_score)

                    fuzzy_loc.append(fuzzy_loc_score)
                    fuzzy_tit.append(fuzzy_title_score)
                    fuzzy_law.append(fuzzy_laws_score)

                    em_total += [em_loc_score, em_title_score, em_laws_score]
                    inter_total += [inter_loc_score, inter_title_score, inter_laws_score]
                    prec_total += [precision_loc_score, precision_title_score, precision_laws_score]
                    rec_total += [recall_loc_score, recall_title_score, recall_laws_score]
                    f1_total += [f1_loc_score, f1_title_score, f1_laws_score]
                    fuzzy_total += [fuzzy_loc_score, fuzzy_title_score, fuzzy_laws_score]

    # 印出個別分數
    print('em分數: ')
    print("單位: " + "{:.2f}".format(numpy.mean(em_loc)),"職稱: " + "{:.2f}".format(numpy.mean(em_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(em_law)))
    print('fuzzymatch: ')
    print("單位: " + "{:.2f}".format(numpy.mean(fuzzy_loc)),"職稱: " + "{:.2f}".format(numpy.mean(fuzzy_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(fuzzy_law)))
    # print('交集分數: ')
    # print("單位: " + "{:.2f}".format(numpy.mean(inter_loc)),"職稱: " + "{:.2f}".format(numpy.mean(inter_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(inter_law)))
    print('precision: ')
    print("單位: " + "{:.2f}".format(numpy.mean(prec_loc)),"職稱: " + "{:.2f}".format(numpy.mean(prec_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(prec_law)))
    print('recall: ')
    print("單位: " + "{:.2f}".format(numpy.mean(rec_loc)),"職稱: " + "{:.2f}".format(numpy.mean(rec_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(rec_law)))
    print('f1score: ')
    print("單位: " + "{:.2f}".format(numpy.mean(f1_loc)),"職稱: " + "{:.2f}".format(numpy.mean(f1_tit)),"所犯法條: " + "{:.2f}".format(numpy.mean(f1_law)))
    

    # 印出總分
    print('=================')
    print('總分')
    print('Exact Match:', "{:.2f}".format(numpy.mean(em_total)))
    print('Fuzzy Match:', "{:.2f}".format(numpy.mean(fuzzy_total)))
    # print('Intersect:', "{:.2f}".format(numpy.mean(inter_total)))
    print('Precision  :', "{:.2f}".format(numpy.mean(prec_total)))
    print('Recall     :', "{:.2f}".format(numpy.mean(rec_total)))
    print('F1 Score   :', "{:.2f}".format(numpy.mean(f1_total)))
    print('=================')
    countup()

if __name__ == "__main__":
    main()