import requests
import json

class AIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "http://agent-runtime-aicustomerservice-test.xyftest.hisense.com/v1/"
    
    def get_agent_info(self):
        info_url = self.url + "info"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }
        try:
            response = requests.get(info_url, headers=headers)
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(e)
            raise Exception(f"API请求失败: {str(e)}")
        
    def get_res_hotline_testenv(self, query):
        chat_url = self.url + "chat-messages"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "inputs": {"user_phone": "11111111111", "hotline_phone": "43001"},
            "query": query,
            "response_mode": "streaming",
            "conversation_id": "",
            "user": "11111111111",
        }
        try:
            response = requests.post(chat_url, data=json.dumps(payload), headers=headers)
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith('data: '):
                    json_str = line[6:].strip()  # 移除"data: "前缀
                else:
                    json_str = line
                try:
                    data = json.loads(json_str)
                    if data.get('event') == 'workflow_finished':
                        final_result = data
                        break
                except json.JSONDecodeError:
                    continue
            result = final_result['data']['outputs']['answer']
            return result
        except requests.exceptions.RequestException as e:
            print(e)
            raise Exception(f"API请求失败: {str(e)}")