import json
import time

from datasets import load_dataset

# 加载数据集
dataset = load_dataset("AdaptLLM/finance-tasks", name="Headline")

# 解析每个段落的函数
def parse_questions_answers(entry):
    pairs = []
    # 分割不同的段落
    questions_answers = entry.split('\n\n')
    for qa in questions_answers:
        # 以下为四种不同的分割情况（由于原数据集的不同句型）
        try:
            if ' Now answer this question: ' in qa:
                headline_part, rest_part = qa.split(' Now answer this question: ')
                question_part, answer = rest_part.rsplit(' ', 1)
                headline = headline_part.replace('Headline:', '').strip()
                question = question_part.strip() + '?'
                pairs.append({"headline": headline, "question": question, "answer": answer})
            elif '\nQuestion:' in qa:
                headline_part, rest_part = qa.split('\nQuestion:')
                question_part, answer = rest_part.split('?')
                headline = headline_part.replace('Headline:', '').strip()
                question = 'Question:' + question_part.strip() + '?'
                answer = answer.strip()
                pairs.append({"headline": headline, "question": question, "answer": answer})
            elif 'Read this headline:' in qa:
                headline_part, rest_part = qa.split('\nNow answer this question: ')
                question_part, answer_options = rest_part.split('\nOptions:\n- ')
                answer_options_list = answer_options.split('\n- ')
                headline = headline_part.replace('Read this headline:', '').strip()
                question = question_part.strip()
                answer = answer_options_list[-1].strip()
                pairs.append({"headline": headline, "question": question, "answer": answer})
            elif 'Please answer a question about the following headline:' in qa:
                headline_part, rest_part = qa.split('\nDoes the news headline talk about ')
                headline = headline_part.replace('Please answer a question about the following headline:', '').strip()
                question_part, answer = rest_part.rsplit(' ', 1)
                question = 'Does the news headline talk about ' + question_part.strip()
                answer = answer.replace('?', '').strip()
                pairs.append({"headline": headline, "question": question, "answer": answer})
        # 若不存在以上的四种情况
        except ValueError as e:
            continue
    return pairs


# 记录开始时间
start_time = time.time()

# 解析数据集并保存为JSON
parsed_data = []
total_number = 0
for entry in dataset['test']:
    parsed_entry = parse_questions_answers(entry['input'])
    parsed_data.append({"id": entry['id'], "questions_answers": parsed_entry})
    total_number += len(parsed_entry)

# 记录结束时间
end_time = time.time()

# 保存解析后的数据为JSON文件
with open("parsed_headlines.json", "w") as json_file:
    json.dump(parsed_data, json_file, indent=4)

print(f"解析后的数据已保存为parsed_headlines.json文件")
print(f"提取的问答对总数: {total_number}")
print(f"数据集清理和转换过程所需时间: {end_time - start_time:.2f} 秒")
