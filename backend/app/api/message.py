from flask import Blueprint, request, g, current_app
from app.services.message import MessageService
from app.utils.response import success_response, error_response
from app.utils.auth import login_required, admin_required

message_bp = Blueprint('message', __name__)

@message_bp.route('', methods=['POST'])
@admin_required
def create_message():
    """创建消息（管理员专用）"""
    try:
        data = request.get_json()
        type = data.get('type')
        title = data.get('title')
        content = data.get('content')
        priority = data.get('priority', 2)
        expire_days = data.get('expire_days', 1)
        user_ids = data.get('user_ids')
        
        # 验证必要字段
        if not all([type, title, content]):
            return error_response("请填写完整信息")
        
        # 验证类型
        if type not in [1, 2, 3, 4]:
            return error_response("无效的消息类型")
        
        success, result = MessageService.create_message(
            type=type,
            title=title,
            content=content,
            priority=priority,
            expire_days=expire_days,
            user_ids=user_ids
        )
        
        if success:
            return success_response(result.to_dict(), "消息创建成功")
        return error_response(result)
    except Exception as e:
        current_app.logger.error(f"创建消息失败: {str(e)}")
        return error_response("创建消息失败")

@message_bp.route('/broadcast', methods=['POST'])
@admin_required
def broadcast_message():
    """广播消息（管理员专用）"""
    data = request.get_json()
    type = data.get('type')
    title = data.get('title')
    content = data.get('content')
    related_id = data.get('related_id')
    priority = data.get('priority', 3)
    expire_days = data.get('expire_days', 1)
    
    # 验证必要字段
    if not all([type, title, content]):
        return error_response("请填写完整信息")
    
    # 验证类型
    if type not in [1, 2, 3, 4]:
        return error_response("无效的消息类型")
    
    success, result = MessageService.broadcast_message(
        type, title, content, related_id, priority, expire_days
    )
    
    if success:
        return success_response(result.to_dict(), "消息广播成功")
    return error_response(result)

@message_bp.route('', methods=['GET'])
@login_required
def get_message_list():
    """获取消息列表"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    type = request.args.get('type')
    is_read = request.args.get('is_read')
    
    if type:
        type = int(type)
    if is_read is not None:
        is_read = int(is_read)
    
    result = MessageService.get_user_messages(
        g.current_user.id,
        type=type,
        is_read=is_read,
        page=page,
        per_page=per_page
    )
    return success_response(result)

@message_bp.route('/<int:message_id>/read', methods=['PUT'])
@login_required
def mark_as_read(message_id):
    """标记消息为已读"""
    success, result = MessageService.mark_as_read(message_id, g.current_user.id)
    if success:
        return success_response(result.to_dict(), "已标记为已读")
    return error_response(result)

@message_bp.route('/unread/count', methods=['GET'])
@login_required
def get_unread_count():
    """获取未读消息数量"""
    count = MessageService.get_unread_count(g.current_user.id)
    return success_response({'count': count})

@message_bp.route('/clean', methods=['POST'])
@admin_required
def clean_expired_messages():
    """清理过期消息（管理员专用）"""
    success, result = MessageService.clean_expired_messages()
    if success:
        return success_response({'cleaned_count': result}, "清理完成")
    return error_response(result) 