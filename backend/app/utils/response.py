from flask import jsonify

def success_response(data=None, message="Success"):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    })

def error_response(message="Error", code=400):
    return jsonify({
        "success": False,
        "message": message
    }), code 