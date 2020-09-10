"""
將判決書全文、evaluate.json合併
"""
import json
out = {}
def load_judgement(jid):
    with open("db_ori_data/%s.txt"%jid,"r") as f:
        data = json.loads(f.read())['judgement']
    return data

def write_json(f,data=None):
    f.write(json.dumps(data,ensure_ascii=False)+"\n")

def renew_out():
    out = {}
    out['judgement'] = ''
    out['_id'] = ''
    out['defendant_scores'] = []
    return out

if __name__ == "__main__":
    with open("evaluate.json","r",encoding='utf-8') as f:
        evaluate_data = json.loads(f.read())
    
    f_merge = open('evaluate_merge.json',"w",encoding='utf-8')
        
    # print(evaluate_data)

    out = renew_out()
    current_judgement_id = evaluate_data['defendant_scores'][0]['_id']
    
    count_judgement = 0
    for i,defendant_score in enumerate(evaluate_data['defendant_scores']):
        # print(i)
        judgement_id = defendant_score['_id']
        judgement = load_judgement(judgement_id)

        #
        if(current_judgement_id == judgement_id):
            #
            out['defendant_scores'].append(defendant_score)
            # print(defendant_score)
         
        #   
        elif(current_judgement_id != judgement_id):
            # write json
            out['_id'] = judgement_id
            out['judgement'] = judgement
            write_json(f_merge,data = out)
            # reset
            current_judgement_id = judgement_id
            out = renew_out()
            out['defendant_scores'].append(defendant_score)

            #
            count_judgement +=1
            # print(count_judgement)
    
    out['_id'] = judgement_id
    out['judgement'] = judgement
    write_json(f_merge,data = out)