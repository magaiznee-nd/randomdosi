import os
import json
import csv

def read_json_and_extract_data():
    json_files = [pos_json for pos_json in os.listdir('./json') if pos_json.endswith('.json')]
    data_to_save = []  # 추출된 데이터를 저장할 리스트

    for json_file in json_files:
        with open(f'./json/{json_file}', 'r', encoding='utf-8') as file:
            data = json.load(file)
            # JSON 구조에 따라 token_id를 추출
            token_id = data['responseData']['tokenId']
            # meta 데이터가 문자열로 저장되어 있다고 가정하고, 이를 다시 JSON 객체로 파싱
            meta = json.loads(data['responseData']['meta'])
            tier = meta['Tier']  # 이제 meta는 파싱된 JSON 객체입니다.
            # 추출된 token_id와 tier를 리스트에 추가
            data_to_save.append([token_id, tier])

    return data_to_save

def save_data_to_csv(data, file_path='output.csv'):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in data:
            writer.writerow(item)