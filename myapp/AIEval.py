import requests
import json

class AIEval:
    def eval_ai(self, input, output, refercence):
        url = "https://inner-apisix-test.hisense.com/histaragent-test/v1/chat-messages?user_key=jdzqqy7jdzbmtaqpqvunvmnncepptwfd"
        headers = {
            "Content-Type": "application/json",
            "authorization": "Bearer app-5h2TLE52jal6806Yqxma2XXE"
        }
        payload = {
            "inputs": {"input": input, "output": output, "reference_output": refercence},
            "query": "给出得分",
            "response_mode": "streaming",
            "conversation_id": "",
            "user": "AI service",
        }
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith('data: '):
                    json_str = line[6:].strip()  # 移除"data: "前缀
                else:
                    json_str = line
                try:
                    data = json.loads(json_str)
                    # print(data)
                    if data.get('event') == 'agent_thought' and data["thought"] != "":
                        final_result = data
                        break
                except json.JSONDecodeError:
                    continue
            result = final_result['thought']
            return result
        except requests.exceptions.RequestException as e:
            print(e)
            raise Exception(f"API请求失败: {str(e)}")