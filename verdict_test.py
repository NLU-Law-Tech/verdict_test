import os
import json
import numpy

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

def fuzzymatch(ans_list, predict_list, fs):
    temp_fuzzy = 0
    if ans_list == predict_list:
        temp_fuzzy += 1
        for subpredict in predict_list:
            for subans in ans_list:
                if subpredict == subans:
                    fs.write(subans + '\t' + subpredict + '\t' + 'A' + '\n')
                    # print(subans + '\t' + subpredict + '\t' + 'A')
    else:
        if len(ans_list) == 0:
            for subpredict in predict_list:
                fs.write(' ' + '\t' + subpredict + '\t' + 'R' + '\n')
                # print(' ' + '\t' + subpredict + '\t' + 'R')
        elif len(predict_list) == 0:
            for subans in ans_list:
                fs.write(subans + '\t' + ' ' + '\t' + 'R' + '\n')
                # print(subans + '\t' + ' ' + '\t' + 'R')
        else:
            for subpredict in predict_list:
                for subans in ans_list:
                    start = 0
                    end = 0
                    flag = True
                    for pred in subpredict:
                        start = subans.find(pred, start)
                        if start < end:
                            flag = False
                        end = start     
                    if flag:
                        try:
                            temp_fuzzy += 1/len(ans_list)
                            fs.write(subans + '\t' + subpredict + '\t' + 'A' + '\n')
                            # print(subans + '\t' + subpredict + '\t' + 'A')
                            break
                        except:
                            fs.write(subans + '\t' + subpredict + '\t' + 'R' + '\n')
                            # print(subans + '\t' + subpredict + '\t' + 'R')
                            pass
                    else:
                        fs.write(subans + '\t' + subpredict + '\t' + 'R' + '\n')
                        # print(subans + '\t' + subpredict + '\t' + 'R')
        
        if temp_fuzzy > 1:
            temp_fuzzy = 1

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
    # tp = len(ans & predict)
    tp = 0
    for subpredict in predict_list:
        for subans in ans_list:
            start = 0
            end = 0
            flag = True
            for pred in subpredict:
                start = subans.find(pred, start)
                if start < end:
                    flag = False
                end = start     
            if flag:
                try:
                    tp += 1
                    break
                except:
                    pass

    if tp > len(ans_list):
        tp = len(ans_list)

    fp = len(set(predict_list)) - tp
    if len(ans_list) == 0:
        if len(predict_list) == 0:
            temp_precision = 1
        else:
            temp_precision = 0
    else:
        try: # tp > 0
            temp_precision = float(tp/(tp+fp))
        except:
            temp_precision = 0
    return temp_precision

def recall(ans_list, predict_list):
    temp_recall = 0
    # tp = len(ans & predict)
    tp = 0
    for subpredict in predict_list:
        for subans in ans_list:
            start = 0
            end = 0
            flag = True
            for pred in subpredict:
                start = subans.find(pred, start)
                if start < end:
                    flag = False
                end = start     
            if flag:
                try:
                    tp += 1
                    break
                except:
                    pass
    
    if tp > len(ans_list):
        tp = len(ans_list)

    fn = len(set(ans_list)) - tp
    if len(ans_list) == 0:
        if len(predict_list) == 0:
            temp_recall = 1
        else:
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
def countup(fs, ans_file = 'db_ans_data'):
    ans_list = []
    for filename in os.listdir(ans_file):
        ans_list.append(filename.replace('.txt',""))

    verdict_name = []
    for ans in ans_list:
        with open(ans_file + '/' + ans, 'r', encoding = 'utf-8') as f:
            ans_info = json.loads(f.read())

        for info in ans_info:
            verdict_name.append(info['name'])

    fs.write('篇數     :' + str(len(ans_list)) + '\n')
    fs.write('被告人數 :' + str(len(verdict_name)) + '\n')
    # print('篇數     :' + str(len(ans_list)))
    # print('被告人數 :' + str(len(verdict_name)))

def score_calculate(ans_list, predict_list, em, inter, prec, rec, f1, fuzzy, reg, fs):
    
    if reg != '':
        fs.write('-----------------------------' + '\n')
        fs.write(reg + '\n')
        fs.write('-----------------------------' + '\n')
        # print('-----------------------------')
        # print(reg)
        # print('-----------------------------')

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
    temp_fuzzy += fuzzymatch(ans_list, predict_list, fs)

    em.append(temp_em)
    inter.append(temp_inter)
    prec.append(temp_precision)
    rec.append(temp_recall)
    f1.append(temp_f1)
    fuzzy.append(temp_fuzzy)

    if reg != '':
        fs.write('=============================' + '\n')
        fs.write('em:' + "{:.2f}".format(temp_em) + '  recall:' + "{:.2f}".format(temp_recall) + '  f1:' + "{:.2f}".format(temp_f1) + '\n' + '\n')
        # print('=============================')
        # print('em:' + "{:.2f}".format(temp_em), '  recall:' + "{:.2f}".format(temp_recall), '  f1:' + "{:.2f}".format(temp_f1) + '\n')

    return temp_em, temp_inter, temp_precision, temp_recall, temp_f1, temp_fuzzy

def main(ans_file = 'ans_data', predict_file = 'predict.json'):

    fs = open('report.txt', 'w')

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

    new_id = ''
    old_id = ''
    # 每篇(predict是以被告為單位視為一篇)的分數 
    for pred_defendant in predict:
        # 開啟對應id的ans.json
        with open(ans_file + '/' + pred_defendant['content_id'] + '.json', 'r', encoding = 'utf-8') as f:
            ans = json.loads(f.read())

        new_id = pred_defendant['content_id']
        if new_id != old_id:
            # print('ID： ' + pred_defendant['content_id'])
            # print('-----------------------------' + '\n')
            fs.write('ID： ' + pred_defendant['content_id'] + '\n')
            fs.write('-----------------------------' + '\n' + '\n')
        old_id = new_id
    
        for ans_defendant in ans:
            if ans_defendant['name'] == pred_defendant['name']:
                
                # print('被告： ' + ans_defendant['name'])
                fs.write('被告： ' + ans_defendant['name'] + '\n')
                em_loc_temp, inter_loc_temp, prec_loc_temp, rec_loc_temp, f1_loc_temp, fuzzy_loc_temp = score_calculate(ans_defendant['job_location'], pred_defendant['job_location'], em_loc, inter_loc, prec_loc, rec_loc, f1_loc, fuzzy_loc, "單位", fs)
                em_tit_temp, inter_tit_temp, prec_tit_temp, rec_tit_temp, f1_tit_temp, fuzzy_tit_temp = score_calculate(ans_defendant['job_title'], pred_defendant['job_title'], em_tit, inter_tit, prec_tit, rec_tit, f1_tit, fuzzy_tit, "職稱", fs)
                fs.write(ans_defendant['name'] + ' AVG.' + '\n')
                fs.write('=============================' + '\n')
                # print(ans_defendant['name'] + ' AVG.')
                # print('=============================')
                em_law_temp, inter_law_temp, prec_law_temp, rec_law_temp, f1_law_temp, fuzzy_law_temp = score_calculate(ans_defendant['laws'], pred_defendant['laws'], em_law, inter_law, prec_law, rec_law, f1_law, fuzzy_law, '', fs)

                em_total += [em_loc_temp, em_tit_temp, em_law_temp]
                inter_total += [inter_loc_temp, inter_tit_temp, inter_law_temp]
                prec_total += [prec_loc_temp, prec_tit_temp, prec_law_temp]
                rec_total += [rec_loc_temp, rec_tit_temp, rec_law_temp]
                f1_total += [f1_loc_temp, f1_tit_temp, f1_law_temp]
                fuzzy_total += [fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp]

                fs.write('em:' + "{:.2f}".format(numpy.mean([em_loc_temp, em_tit_temp, em_law_temp])) + '  recall:' + "{:.2f}".format(numpy.mean([rec_loc_temp, rec_tit_temp, rec_law_temp])) + '  f1:' + "{:.2f}".format(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp])) + '\n')
                fs.write('-----------------------------\n\n' + '\n')
                # print('em:' + "{:.2f}".format(numpy.mean([em_loc_temp, em_tit_temp, em_law_temp])), '  recall:' + "{:.2f}".format(numpy.mean([rec_loc_temp, rec_tit_temp, rec_law_temp])), '  f1:' + "{:.2f}".format(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp])))
                # print('-----------------------------\n\n')

    fs.write('TOTAL' + '\n')
    fs.write('-----------------------------' + '\n')
    countup(fs, ans_file = ans_file)
    fs.write('-----------------------------' + '\n')
    fs.write('AVG職稱 em:' + "{:.2f}".format(numpy.mean(em_tit)) + '  recall:' + "{:.2f}".format(numpy.mean(rec_tit)) + '  f1:' + "{:.2f}".format(numpy.mean(f1_tit)) + '\n')
    fs.write('AVG單位 em:' + "{:.2f}".format(numpy.mean(em_loc)) + '  recall:' + "{:.2f}".format(numpy.mean(rec_loc)) + '  f1:' + "{:.2f}".format(numpy.mean(f1_loc)) + '\n')
    fs.write('=============================' + '\n')
    fs.write('AVG     em:' + "{:.2f}".format(numpy.mean(em_total)) + '  recall:' + "{:.2f}".format(numpy.mean(rec_total)) + '  f1:' + "{:.2f}".format(numpy.mean(f1_total)) + '\n')
    # print('TOTAL')
    # print('-----------------------------')
    # countup(ans_file = ans_file, f)
    # print('-----------------------------')
    # print('AVG職稱 em:' + "{:.2f}".format(numpy.mean(em_tit)), '  recall:' + "{:.2f}".format(numpy.mean(rec_tit)), '  f1:' + "{:.2f}".format(numpy.mean(f1_tit)))
    # print('AVG單位 em:' + "{:.2f}".format(numpy.mean(em_loc)), '  recall:' + "{:.2f}".format(numpy.mean(rec_loc)), '  f1:' + "{:.2f}".format(numpy.mean(f1_loc)))
    # print('=============================')
    # print('AVG     em:' + "{:.2f}".format(numpy.mean(em_total)), '  recall:' + "{:.2f}".format(numpy.mean(rec_total)), '  f1:' + "{:.2f}".format(numpy.mean(f1_total)))
    fs.close()

if __name__ == "__main__":
    main()
