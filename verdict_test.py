import os
import re
import json
import numpy

separate_length = 70

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

def align(string, length=25):
    difference = length -  len(string)
    if difference == 0:
        return string
    elif difference < 0:
        difference = 5
    chinese_pattern = u'[?([\u4E00-\u9FA5]'
    if re.search(chinese_pattern,string) != None: 
        space = '　' 
    else:
        space = ' '
    return string + space*(difference)

def show(ans, predict, a_r, fs, length):
    fs.write(align(ans, length) + align(predict, length) + a_r + '\n')

def splitspace(string):
    remove_list = [' ', '　', '\\n', '\\r', '\r', '\n', '股份有限公司', '有限公司', '無限公司', '兩合公司', '公司']
    for rem in remove_list:
        string = string.replace(rem, '')
    return string

def exactmatch(ans_list, predict_list):
    temp_em = 0
    if ans_list == predict_list:
        temp_em += 1
    return temp_em

def fuzzymatch(ans_list, predict_list, fs, length):
    temp_fuzzy = 0
    if ans_list == predict_list:
        temp_fuzzy += 1
        for subpredict in predict_list:
            for subans in ans_list:
                if subpredict == subans:
                    show(subans, subpredict, 'A', fs, length)
    else:
        for index_1, subpredict in enumerate(predict_list):
            for index_2, subans in enumerate(ans_list):
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
                        if subans != '' and subpredict != '':
                            temp_fuzzy += 1/len(ans_list)
                            show(subans, subpredict, 'A', fs,length)
                            predict_list[index_1] = ''
                            ans_list[index_2] = ''
                    except:
                        pass
                
        for subans in ans_list:
            if subans != '':
                show(subans, '空', 'R', fs,length)
        for subpredict in predict_list:
            if subpredict != '':
                show('空', subpredict, 'R', fs,length)
    
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

    fs.write('篇數     : ' + str(len(ans_list)) + '\n')
    fs.write('被告人數　: ' + str(len(verdict_name)) + '\n')

def score_calculate(ans_list, predict_list, em, inter, prec, rec, f1, fuzzy, reg, fs, length):
    
    for index, ans in enumerate(ans_list):
        ans_list[index] = splitspace(ans)
    for index, pred in enumerate(predict_list):
        predict_list[index] = splitspace(pred)
        
    fs.write(''.rjust(15, '-') + '\n')
    fs.write(' ＊＊　' + reg + '　＊＊　  ' + '\n')
    fs.write(''.rjust(70, '-') + '\n')

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
    temp_fuzzy += fuzzymatch(ans_list, predict_list, fs,length)

    em.append(temp_em)
    inter.append(temp_inter)
    prec.append(temp_precision)
    rec.append(temp_recall)
    f1.append(temp_f1)
    fuzzy.append(temp_fuzzy)

    fs.write(''.rjust(separate_length, '=') + '\n')
    fs.write('EM: ' + "{:.2f}".format(temp_fuzzy) + '  F1: ' + "{:.2f}".format(temp_f1) + '\n' + '\n')

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
    each_fuzzy_verdict = []
    each_f1_verdict = []
    # 每篇(predict是以被告為單位視為一篇)的分數 
    for pred_defendant in predict:
        # 開啟對應id的ans.json
        with open(ans_file + '/' + pred_defendant['content_id'] + '.json', 'r', encoding = 'utf-8') as f:
            ans = json.loads(f.read())
        
        # 判斷是不是同篇判決書
        new_id = pred_defendant['content_id']
        if new_id != old_id:
            if old_id == '':
                fs.write('ID： ' + pred_defendant['content_id'] + '\n')
                fs.write(''.rjust(50, '-') + '\n\n')
            else:
                each_fuzzy_verdict.append(numpy.mean([fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp]))
                each_f1_verdict.append(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
                fs.write(old_id + ' AVG.' + '\n')
                fs.write(''.rjust(separate_length, '=') + '\n')
                fs.write('EM: ' + "{:.2f}".format(numpy.mean(each_fuzzy_verdict)) + '  F1: ' + "{:.2f}".format(numpy.mean(each_f1_verdict)) + '\n')
                fs.write(''.rjust(separate_length, '-') + '\n\n' + '\n')
                each_fuzzy_verdict.clear()
                each_f1_verdict.clear()
                fs.write('ID： ' + pred_defendant['content_id'] + '\n')
                fs.write(''.rjust(50, '-') + '\n\n')
        else:
            each_fuzzy_verdict.append(numpy.mean([fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp]))
            each_f1_verdict.append(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
        old_id = new_id

        for ans_defendant in ans:
            if ans_defendant['name'] == pred_defendant['name']:
                
                fs.write('被告： ' + ans_defendant['name'] + '\n')
                em_loc_temp, inter_loc_temp, prec_loc_temp, rec_loc_temp, f1_loc_temp, fuzzy_loc_temp = score_calculate(ans_defendant['job_location'], pred_defendant['job_location'], em_loc, inter_loc, prec_loc, rec_loc, f1_loc, fuzzy_loc, "單位", fs, 15)
                em_tit_temp, inter_tit_temp, prec_tit_temp, rec_tit_temp, f1_tit_temp, fuzzy_tit_temp = score_calculate(ans_defendant['job_title'], pred_defendant['job_title'], em_tit, inter_tit, prec_tit, rec_tit, f1_tit, fuzzy_tit, "職稱", fs, 15)
                em_law_temp, inter_law_temp, prec_law_temp, rec_law_temp, f1_law_temp, fuzzy_law_temp = score_calculate(ans_defendant['laws'], pred_defendant['laws'], em_law, inter_law, prec_law, rec_law, f1_law, fuzzy_law, "法條", fs, 25)
                fs.write(ans_defendant['name'] + ' AVG.' + '\n')
                fs.write(''.rjust(separate_length, '=') + '\n')

                em_total += [em_loc_temp, em_tit_temp, em_law_temp]
                inter_total += [inter_loc_temp, inter_tit_temp, inter_law_temp]
                prec_total += [prec_loc_temp, prec_tit_temp, prec_law_temp]
                rec_total += [rec_loc_temp, rec_tit_temp, rec_law_temp]
                f1_total += [f1_loc_temp, f1_tit_temp, f1_law_temp]
                fuzzy_total += [fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp]

                fs.write('EM: ' + "{:.2f}".format(numpy.mean([fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp])) + '  F1: ' + "{:.2f}".format(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp])) + '\n')
                fs.write(''.rjust(separate_length, '-') + '\n\n' + '\n')

    
    each_fuzzy_verdict.append(numpy.mean([fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp]))
    each_f1_verdict.append(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
    fs.write(old_id + ' AVG.' + '\n')
    fs.write(''.rjust(separate_length, '=') + '\n')
    fs.write('EM: ' + "{:.2f}".format(numpy.mean(each_fuzzy_verdict)) + '  F1: ' + "{:.2f}".format(numpy.mean(each_f1_verdict)) + '\n')
    fs.write(''.rjust(separate_length, '-') + '\n\n' + '\n')
    
    fs.write('TOTAL' + '\n')
    fs.write(''.rjust(separate_length, '-') + '\n')
    countup(fs, ans_file = ans_file)
    fs.write(''.rjust(separate_length, '-') + '\n')
    fs.write('AVG 單位 EM: ' + "{:.2f}".format(numpy.mean(fuzzy_loc)) + '  F1: ' + "{:.2f}".format(numpy.mean(f1_loc)) + '\n')
    fs.write('AVG 職稱 EM: ' + "{:.2f}".format(numpy.mean(fuzzy_tit)) + '  F1: ' + "{:.2f}".format(numpy.mean(f1_tit)) + '\n')
    fs.write('AVG 法條 EM: ' + "{:.2f}".format(numpy.mean(fuzzy_law)) + '  F1: ' + "{:.2f}".format(numpy.mean(f1_law)) + '\n')
    fs.write(''.rjust(separate_length, '=') + '\n')
    fs.write('AVG     EM: ' + "{:.2f}".format(numpy.mean(fuzzy_total)) + '  F1: ' + "{:.2f}".format(numpy.mean(f1_total)) + '\n')    
    fs.close()

if __name__ == "__main__":
    main()
