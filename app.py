from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>欢迎来到AI万吧</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f0f8ff;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .info-box {
                background: #f9f9f9;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #3498db;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>欢迎访问AI万吧管理后台</h1>
            
            <div class="info-box">
                <h3>系统信息</h3>
                <p>项目名称：cs_aiwanba_net</p>
                <p>运行端口：5010</p>
                <p>Python版本：3.11.9</p>
            </div>

            <div class="info-box">
                <h3>数据库状态</h3>
                <p>数据库版本：MySQL 5.7.40</p>
                <p>连接用户：cs_aiwanba_net</p>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 