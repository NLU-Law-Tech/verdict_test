import os
import re
import json
import cn2an
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
    remove_list = [' ', '　', '\\n', '\\r', '\r', '\n', '[UNK]']
    company_list = ['股份有限公司$', '有限公司$', '無限公司$', '兩合公司$', '公司$', '^中華民國']
    for rem in remove_list:
        string = string.replace(rem, '')
    for com in company_list:
        string = re.sub(com, '', string)
    return string

def exactmatch(ans_list, predict_list):
    temp_em = 0
    if ans_list == predict_list:
        temp_em += 1
    return temp_em

def fuzzymatch(ori_ans_list, ori_predict_list, ans_list, predict_list, fs, length):
    temp_fuzzy = 0
    if ans_list == predict_list:
        temp_fuzzy += 1
        for index_1, subpredict in enumerate(predict_list):
            for index_2, subans in enumerate(ans_list):
                if subpredict == subans:
                    show(ori_ans_list[index_2], ori_predict_list[index_1], 'A', fs, length)
    else:
        # predict是ans的subset
        for index_1, subpredict in enumerate(predict_list):
            for index_2, subans in enumerate(ans_list):
                start = 0
                end = 0
                flag = True
                for pred in subpredict:
                    start = subans.find(pred, end)
                    if start < end:
                        flag = False
                    end = start + 1
                if flag:
                    try:
                        if ans_list[index_2] != '' and predict_list[index_1] != '':
                            if ans_list[index_2] != 'Null' and predict_list[index_1] != 'Null':
                                temp_fuzzy += 1/len(ans_list)
                                show(ori_ans_list[index_2], ori_predict_list[index_1], 'A', fs,length)
                                predict_list[index_1] = ''
                                ans_list[index_2] = ''
                    except:
                        pass

        # ans是predict的subset
        for index_1, subans in enumerate(ans_list):
            for index_2, subpredict in enumerate(predict_list):
                start = 0
                end = 0
                flag = True
                for ans in subans:
                    start = subpredict.find(ans, end)
                    if start < end:
                        flag = False
                    end = start + 1 
                if flag:
                    try:
                        if ans_list[index_1] != '' and predict_list[index_2] != '':
                            if ans_list[index_1] != 'Null' and predict_list[index_2] != 'Null':
                                temp_fuzzy += 1/len(ans_list)
                                show(ori_ans_list[index_1], ori_predict_list[index_2], 'A_ans是predict的subset', fs,length)
                                predict_list[index_2] = ''
                                ans_list[index_1] = ''
                    except:
                        pass
                
        for index, subans in enumerate(ans_list):
            if subans != '':
                show(ori_ans_list[index], '空', 'R', fs,length)
        for index, subpredict in enumerate(predict_list):
            if subpredict != '':
                show('空', ori_predict_list[index], 'R', fs,length)
    
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
    tp = get_tp_score(ans_list, predict_list)

    if tp > len(ans_list):
        tp = len(ans_list)

    pre_len = 0
    for pre in predict_list:
        if pre != 'Null':
            pre_len += 1
    fp = pre_len - tp
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
    tp = get_tp_score(ans_list, predict_list)
    
    if tp > len(ans_list):
        tp = len(ans_list)

    ans_len = 0
    for ans in ans_list:
        if ans != 'Null':
            ans_len += 1
    fn = ans_len - tp
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

def get_tp_score(ans_list, predict_list):
    reg_ans_list = ans_list.copy()
    reg_predict_list = predict_list.copy()
    tp = 0
    # predict是ans的subset
    for index_1, subpredict in enumerate(reg_predict_list):
        for index_2, subans in enumerate(reg_ans_list):
            start = 0
            end = 0
            flag = True
            for pred in subpredict:
                start = subans.find(pred, end)
                if start < end:
                    flag = False
                end = start + 1
            if flag:
                try:
                    if reg_ans_list[index_2] != '' and reg_predict_list[index_1] != '':
                        if reg_ans_list[index_2] != 'Null' and reg_predict_list[index_1] != 'Null':
                            tp += 1
                            reg_predict_list[index_1] = ''
                            reg_ans_list[index_2] = ''
                except:
                    pass

    # ans是predict的subset
    for index_1, subans in enumerate(reg_ans_list):
        for index_2, subpredict in enumerate(reg_predict_list):
            start = 0
            end = 0
            flag = True
            for ans in subans:
                start = subpredict.find(ans, end)
                if start < end:
                    flag = False
                end = start + 1
            if flag:
                try:
                    if reg_ans_list[index_1] != '' and reg_predict_list[index_2] != '':
                        if reg_ans_list[index_1] != 'Null' and reg_predict_list[index_2] != 'Null':
                            tp += 1
                            reg_predict_list[index_2] = ''
                            reg_ans_list[index_1] = ''
                except:
                    pass

    return tp

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
def countup(fs, ans_file = 'db_ans_data', predict_file = 'predict.json'):
    with open(predict_file, 'r', encoding = 'utf-8') as fp:
        predict = json.loads(fp.read())
    
    verdict_name = 0
    verdict_list = []
    for pred_defendant in predict:
        with open(ans_file + '/' + pred_defendant['content_id'] + '.json', 'r', encoding = 'utf-8') as f:
            ans = json.loads(f.read())

        for key, value in pred_defendant.items():
            if key == 'content_id':
                verdict_list.append(value)

        for ans_defendant in ans:
            if ans_defendant['name'] == pred_defendant['name']:
                verdict_name += 1
    
    fs.write('篇數     : ' + str(len(set(verdict_list))) + '\n')
    fs.write('被告人數　: ' + str(verdict_name) + '\n')

def show_count(fs, reg2, count_dict):
    reg = reg2.replace(' ', '')
    if reg == '總共':
        count_dict[reg]['ans_total'] = count_dict['單位']['ans_total'] + count_dict['職稱']['ans_total'] + count_dict['法條']['ans_total']
        count_dict[reg]['predict_total'] = count_dict['單位']['predict_total'] + count_dict['職稱']['predict_total'] + count_dict['法條']['predict_total']
        count_dict[reg]['ans_empty'] = count_dict['單位']['ans_empty'] + count_dict['職稱']['ans_empty'] + count_dict['法條']['ans_empty']
        count_dict[reg]['predict_empty'] = count_dict['單位']['predict_empty'] + count_dict['職稱']['predict_empty'] + count_dict['法條']['predict_empty']
        count_dict[reg]['ans_pre_nonempty'] = count_dict['單位']['ans_pre_nonempty'] + count_dict['職稱']['ans_pre_nonempty'] + count_dict['法條']['ans_pre_nonempty']

    pre_empty = ans_empty = ans_pre_empty = 0
    pre_empty = count_dict[reg]['ans_total'] - count_dict[reg]['ans_pre_nonempty']
    ans_empty = count_dict[reg]['predict_total'] - count_dict[reg]['ans_pre_nonempty']
    ans_pre_empty = count_dict[reg]['ans_empty'] - ans_empty

    fs.write('-- ' + reg2 + ' --'+ '\n')
    fs.write('answer 非空筆數: ' + align(str(count_dict[reg]['ans_total']),5) + '       ')
    fs.write('predict 非空筆數: ' + align(str(count_dict[reg]['predict_total']), 5))
    fs.write('\t\t\t        p r e d i c t\n')

    fs.write('answer 為空筆數: ' + align(str(count_dict[reg]['ans_empty']), 5) + '       ')
    fs.write('predict 為空筆數: ' + align(str(count_dict[reg]['predict_empty']), 5))
    fs.write('          \t    |  Yes  |  No\n')

    fs.write( 'answer 空的比例: ' + str("{:.2f}".format(count_dict[reg]['ans_empty']/(count_dict[reg]['ans_total']+count_dict[reg]['ans_empty']))) + '        ')
    fs.write( 'predict 空的比例: ' + "{:.2f}".format(count_dict[reg]['predict_empty']/(count_dict[reg]['predict_total']+count_dict[reg]['predict_empty'])))
    fs.write('\t\t   a  -------------------\n')
    fs.write(' '*51 + '\t\t   n  Yes\t|  ' + str(count_dict[reg]['ans_pre_nonempty']) + '\t|  ' + str(pre_empty) + '\n')
    fs.write(' '*51 + '\t\t   s  No\t|  ' + str(ans_empty) + '\t|  ' + str(ans_pre_empty) + '\n\n')

def score_calculate(ans_list, predict_list, em, inter, prec, rec, f1, fuzzy, reg, fs, length, count_dict):

    ori_ans_list = ans_list.copy()
    ori_predict_list = predict_list.copy()

    exist_ans_list = []
    exist_predict_list = []
    
    # 處理後綴以及中文轉阿拉伯數字
    if len(ans_list) == 0:
        count_dict[reg]['ans_empty'] += 1
    else:
        count_dict[reg]['ans_total'] += 1
    for index, ans in enumerate(ans_list):
        ans_list[index] = splitspace(ans)
        if reg == '法條':
            if ans_list[index].find('百十') != -1:
                ans_list[index] = ans_list[index].replace('百十', '百一十')
            ans_list[index] = cn2an.transform(ans_list[index], 'cn2an')
            last_index = ans_list[index].rfind('條')
            if last_index != -1:
                ans_list[index] = ans_list[index][:last_index]

        if ans_list[index] not in exist_ans_list:
            exist_ans_list.append(ans_list[index])
        else:
            ans_list[index] = 'Null'

    if len(predict_list) == 0:
        count_dict[reg]['predict_empty'] += 1
    else:
        count_dict[reg]['predict_total'] += 1
    for index, pred in enumerate(predict_list):
        predict_list[index] = splitspace(pred)
        if reg == '法條':
            if predict_list[index].find('百十') != -1:
                predict_list[index] = predict_list[index].replace('百十', '百一十')
            predict_list[index] = cn2an.transform(predict_list[index], 'cn2an')
            last_index = predict_list[index].rfind('條')
            if last_index != -1:
                predict_list[index] = predict_list[index][:last_index]

        if predict_list[index] not in exist_predict_list:
            exist_predict_list.append(predict_list[index])
        else:
            predict_list[index] = 'Null'

    # for report_full
    if len(ans_list) != 0 and len(predict_list) != 0:
        count_dict[reg]['ans_pre_nonempty'] += 1
    
    show_separate(fs, 15, '-', '\n')
    fs.write(' ＊＊　' + reg + '　＊＊　  ' + '\n')
    show_separate(fs, 70, '-', '\n')

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
    temp_fuzzy += fuzzymatch(ori_ans_list, ori_predict_list, ans_list, predict_list, fs, length)

    em.append(temp_em)
    inter.append(temp_inter)
    prec.append(temp_precision)
    rec.append(temp_recall)
    f1.append(temp_f1)
    fuzzy.append(temp_fuzzy)

    show_separate(fs, separate_length, '=', '\n')
    show_score(fs, '', temp_precision, temp_recall, temp_f1)
    fs.write('\n')

    return temp_em, temp_inter, temp_precision, temp_recall, temp_f1, temp_fuzzy

def show_score(fs, special_string, prec_list, rec_list, f1_list):
    fs.write(special_string + 'Precision: '+ "{:.2f}".format(numpy.mean(prec_list)) + '      Recall: ' + "{:.2f}".format(numpy.mean(rec_list)) + '      F1: ' + "{:.2f}".format(numpy.mean(f1_list))  + '\n')

def show_separate(fs, separate_len, separate_string, break_line):
    fs.write(''.rjust(separate_len, separate_string) + break_line)

def create_dict(count_dict):
    reg_list = ['單位', '職稱', '法條', '總共']
    for reg in reg_list:
        count_dict[reg] = {}
        count_dict[reg]['ans_empty'] = 0
        count_dict[reg]['ans_total'] = 0
        count_dict[reg]['predict_empty'] = 0
        count_dict[reg]['predict_total'] = 0
        count_dict[reg]['ans_pre_nonempty'] = 0


def main(ans_file = 'db_ans_data', predict_file = 'predict.json', file_name = 'report.txt'):
    json_output = {}
    json_output['defendant_scores'] = []
    json_output['total_score'] = {}

    count_dict = {}
    create_dict(count_dict)
    fs = open(file_name, 'w')

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
    each_precision_verdict = []
    each_recall_verdict = []
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
                show_separate(fs, 50, '-', '\n\n')
            else:
                # 印出單篇最後結尾
                each_precision_verdict.append(numpy.mean([prec_loc_temp, prec_tit_temp, prec_law_temp]))
                each_recall_verdict.append(numpy.mean([rec_loc_temp, rec_tit_temp, rec_law_temp]))
                each_f1_verdict.append(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
                fs.write(old_id + ' AVG.' + '\n')
                show_separate(fs, separate_length, '=', '\n')
                show_score(fs, '', each_precision_verdict, each_recall_verdict, each_f1_verdict)
                show_separate(fs, separate_length, '-', '\n\n\n')
                # print(old_id,each_precision_verdict, each_recall_verdict, each_f1_verdict)
                
                # 印出單篇起頭
                each_precision_verdict.clear()
                each_recall_verdict.clear()
                each_f1_verdict.clear()
                fs.write('ID： ' + pred_defendant['content_id'] + '\n')
                show_separate(fs, 50, '-', '\n\n')
        else:
            each_precision_verdict.append(numpy.mean([prec_loc_temp, prec_tit_temp, prec_law_temp]))
            each_recall_verdict.append(numpy.mean([rec_loc_temp, rec_tit_temp, rec_law_temp]))
            each_f1_verdict.append(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
        old_id = new_id

        for ans_defendant in ans:
            if ans_defendant['name'] == pred_defendant['name']:
                
                fs.write('被告： ' + ans_defendant['name'] + '\n')
                em_loc_temp, inter_loc_temp, prec_loc_temp, rec_loc_temp, f1_loc_temp, fuzzy_loc_temp = score_calculate(ans_defendant['job_location'], pred_defendant['job_location'], em_loc, inter_loc, prec_loc, rec_loc, f1_loc, fuzzy_loc, "單位", fs, 15, count_dict)
                em_tit_temp, inter_tit_temp, prec_tit_temp, rec_tit_temp, f1_tit_temp, fuzzy_tit_temp = score_calculate(ans_defendant['job_title'], pred_defendant['job_title'], em_tit, inter_tit, prec_tit, rec_tit, f1_tit, fuzzy_tit, "職稱", fs, 15, count_dict)
                em_law_temp, inter_law_temp, prec_law_temp, rec_law_temp, f1_law_temp, fuzzy_law_temp = score_calculate(ans_defendant['laws'], pred_defendant['laws'], em_law, inter_law, prec_law, rec_law, f1_law, fuzzy_law, "法條", fs, 25, count_dict)
                fs.write(ans_defendant['name'] + ' AVG.' + '\n')
                show_separate(fs, separate_length, '=', '\n')

                em_total += [em_loc_temp, em_tit_temp, em_law_temp]
                inter_total += [inter_loc_temp, inter_tit_temp, inter_law_temp]
                prec_total += [prec_loc_temp, prec_tit_temp, prec_law_temp]
                rec_total += [rec_loc_temp, rec_tit_temp, rec_law_temp]
                f1_total += [f1_loc_temp, f1_tit_temp, f1_law_temp]
                fuzzy_total += [fuzzy_loc_temp, fuzzy_tit_temp, fuzzy_law_temp]

                show_score(fs, '', [prec_loc_temp, prec_tit_temp, prec_law_temp], [rec_loc_temp, rec_tit_temp, rec_law_temp], [f1_loc_temp, f1_tit_temp, f1_law_temp])
                show_separate(fs, separate_length, '-', '\n\n\n')
                
                
                _output_for_json = {
                    "_id":old_id,
                    "name":ans_defendant['name'],
                    "unit_score":{"prec":float(prec_loc_temp),"recall":float(rec_loc_temp),"f1":float(f1_loc_temp)},
                    "postion_score":{"prec":float(prec_tit_temp),"recall":float(rec_tit_temp),"f1":float(f1_tit_temp)},
                    "law_score":{"prec":float(prec_law_temp),"recall":float(rec_law_temp),"f1":float(f1_law_temp)},
                    "avg_score":{
                            "prec":float(numpy.mean([prec_loc_temp, prec_tit_temp, prec_law_temp])),
                            "recall":float(numpy.mean([rec_loc_temp, rec_tit_temp, rec_law_temp])),
                            "f1":float(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
                        }
                }
                json_output['defendant_scores'].append(_output_for_json)
                
                #     print("%(_id)s %(name)s 單位:%(unit_score)s 職稱:%(postion_score)s 法條:%(law_score)s 平均:%(avg_score)s"%(_output_for_json))
                    # exit()
    each_precision_verdict.append(numpy.mean([prec_loc_temp, prec_tit_temp, prec_law_temp]))
    each_recall_verdict.append(numpy.mean([rec_loc_temp, rec_tit_temp, rec_law_temp]))
    each_f1_verdict.append(numpy.mean([f1_loc_temp, f1_tit_temp, f1_law_temp]))
    fs.write(old_id + ' AVG.' + '\n')
    show_separate(fs, separate_length, '=', '\n')
    show_score(fs, '', each_precision_verdict, each_recall_verdict, each_f1_verdict)
    show_separate(fs, separate_length, '-', '\n\n\n')
    
    show_count(fs, '單 位', count_dict)
    show_count(fs, '職 稱', count_dict)
    show_count(fs, '法 條', count_dict)
    show_count(fs, '總 共', count_dict)


    fs.write('\n' + 'TOTAL' + '\n')
    show_separate(fs, separate_length, '-', '\n')
    countup(fs, ans_file = ans_file, predict_file = predict_file)
    show_separate(fs, separate_length, '-', '\n')
    show_score(fs, 'AVG 單位 ', prec_loc, rec_loc, f1_loc)
    show_score(fs, 'AVG 職稱 ', prec_tit, rec_tit, f1_tit)
    show_score(fs, 'AVG 法條 ', prec_law, rec_law, f1_law)
    
    show_separate(fs, separate_length, '=', '\n')
    show_score(fs, 'AVG     ', prec_total, rec_total, f1_total)

    #
    _output_for_json={
        #
        "unit_prec":float(numpy.mean(prec_loc)),
        "unit_recall":float(numpy.mean(rec_loc)),
        "unit_f1":float(numpy.mean(f1_loc)),
        #
        "position_prec":float(numpy.mean(prec_tit)),
        "position_recall":float(numpy.mean(rec_tit)),
        "position_f1":float(numpy.mean(f1_tit)),
        #
        "law_prec":float(numpy.mean(prec_law)),
        "law_recall":float(numpy.mean(rec_law)),
        "law_f1":float(numpy.mean(f1_law)),
        #
        "all_prec":float(numpy.mean(prec_total)),
        "all_recall":float(numpy.mean(rec_total)),
        "all_f1":float(numpy.mean(f1_total))
    }
    json_output['total_score'] = _output_for_json

    with open(os.path.abspath(os.path.dirname(__file__)) + "/evaluate.json","w",encoding="utf-8") as f:
        f.write(json.dumps(json_output,ensure_ascii=False))

    fs.close()

if __name__ == "__main__":
    main()