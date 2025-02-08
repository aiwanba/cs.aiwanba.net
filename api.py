from openai import OpenAI

def create_nvidia_client():
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="$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"
    )

def get_model_response(client, prompt):
    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            stream=True
        )
        
        # Process the streaming response
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def main():
    client = create_nvidia_client()
    test_prompt = "Which number is larger, 9.11 or 9.8?"
    get_model_response(client, test_prompt)

if __name__ == "__main__":
    main() 