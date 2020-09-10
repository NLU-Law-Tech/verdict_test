"""
將判決書全文、evaluate.json合併
"""
import json

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
    current_judgement_id = None
    for defendant_score in evaluate_data['defendant_scores']:
        judgement_id = defendant_score['_id']
        judgement = load_judgement(judgement_id)

        #
        if(current_judgement_id is None or current_judgement_id == judgement_id):
            #
            current_judgement_id = judgement_id
            
            #
            out['_id'] = judgement_id
            # out['judgement'] = judgement
            out['defendant_scores'].append(defendant_score)
         
        #   
        elif(current_judgement_id != judgement_id):
            # write json
            write_json(f_merge,data = out)
            # reset
            current_judgement_id = None
            out = renew_out()
            
    write_json(f_merge,data = out)