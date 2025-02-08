import requests
import json

API_KEY = "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"
BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def get_model_response(prompt):
    try:
        # 尝试不同的认证头格式
        headers = {
            # 移除 Bearer 前缀
            "Authorization": API_KEY,
            "Content-Type": "application/json",
            # 添加额外的 NVIDIA API 相关头部
            "Accept": "application/json",
            "User-Agent": "NVIDIA API Client/1.0"
        }
        
        data = {
            "model": "deepseek-ai/deepseek-r1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "top_p": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
        
        # 添加详细的调试信息
        print("Sending request with headers:", json.dumps(headers, indent=2))
        print("Request data:", json.dumps(data, indent=2))
        
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=data,
            # 添加超时设置
            timeout=30
        )
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                print(result['choices'][0]['message']['content'])
        else:
            print(f"Error occurred: Status code {response.status_code}")
            print(f"Response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e)}")

def main():
    test_prompt = "Which number is larger, 9.11 or 9.8?"
    get_model_response(test_prompt)

if __name__ == "__main__":
    main() 