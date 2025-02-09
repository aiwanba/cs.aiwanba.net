"""
AI服务类，处理与AI模型的交互
"""
from openai import OpenAI
import logging

class AIService:
    def __init__(self):
        try:
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key="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"
            )
            logging.info("AI service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize AI service: {str(e)}")
            raise
    
    def generate_response(self, prompt, history=None, stream=True):
        """
        生成AI响应
        """
        try:
            logging.info(f"Generating response for prompt: {prompt[:100]}...")
            
            # 构建消息历史
            messages = []
            if history:
                for msg in history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 添加当前问题
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            completion = self.client.chat.completions.create(
                model="deepseek-ai/deepseek-r1",
                messages=messages,
                temperature=1,
                top_p=1,
                max_tokens=4096,
                stream=stream
            )
            
            if stream:
                def response_generator():
                    try:
                        for chunk in completion:
                            if chunk.choices[0].delta.content is not None:
                                yield chunk.choices[0].delta.content
                    except Exception as e:
                        logging.error(f"Error in stream generation: {str(e)}")
                        yield f"Error: {str(e)}"
                return response_generator()
            else:
                return completion.choices[0].message.content
                
        except Exception as e:
            logging.error(f"Error generating AI response: {str(e)}")
            raise 