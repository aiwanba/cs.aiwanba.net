from openai import OpenAI
import urllib3

# 禁用不安全的 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_client():
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

def get_model_response(prompt):
    try:
        client = create_client()
        
        print("\n=== Request Information ===")
        print("Prompt:", prompt)
        print("Model: deepseek-ai/deepseek-r1")
        
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            stream=True
        )
        
        print("\n=== Model Response ===")
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="")
                full_response += content
        
        return full_response
                
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        return None

def main():
    test_prompt = "Which number is larger, 9.11 or 9.8?"
    get_model_response(test_prompt)

if __name__ == "__main__":
    main() 