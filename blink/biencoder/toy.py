import os
import json
import random 

def generate_toy_data(n_samples=1000, context_length=200, dump_source=None):
    samples = []
    with open(dump_source,'r') as f:
        for line in f:
            row = json.loads(line.strip())
            row_title = row['title']
            row_text = row['text'][0:context_length]
            samples.append({
                "title": row_title,
                "text": row_text
            })
    records = []
    for i in range(n_samples):
        context_sample = random.choice(samples)
        label_sample = random.choice(samples)
        record = {
            "context_left": context_sample['text'],
            "context_right": context_sample['text'],
            "mention": context_sample['title'],
            "label": context_sample['text'],
            "label_title": context_sample['title'],
            "label_id": random.randint(0,1e+6)
        }
        records.append(record)
    return records

def save_to_jsonl(records, target):
    with open(target,'a+') as f:
        for record in records:
            print(json.dumps(record), file=f)

def main():
    os.remove('toy/train.jsonl')
    path = '/home/datasets/entity_linking/BLINK/data/wikipedia/wiki/AA/wiki_00'
    records = generate_toy_data(dump_source=path)
    save_to_jsonl(records, 'toy/train.jsonl')

if __name__ == '__main__':
    main()