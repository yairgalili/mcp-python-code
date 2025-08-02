import requests

headers = {
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
}

json_data = {
    'repo_path': './grip-repo',
    'question': 'What does the function patch do?',
}

response = requests.post('http://localhost:8000/ask', headers=headers, json=json_data)