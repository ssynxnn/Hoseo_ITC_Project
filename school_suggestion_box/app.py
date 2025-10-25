from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
DATA_FILE = 'suggestions.json'
ADMIN_CREDENTIALS = {'hoseogo': '12345'}

CATEGORY_CONFIG = {
    'facility': {'icon': '🏢', 'color': 'bg-blue-100 text-blue-800', 'name': '시설 개선'},
    'restroom': {'icon': '🚻', 'color': 'bg-cyan-100 text-cyan-800', 'name': '학교 화장실'},
    'food': {'icon': '🍽️', 'color': 'bg-green-100 text-green-800', 'name': '급식 관련'},
    'trash': {'icon': '🗑️', 'color': 'bg-orange-100 text-orange-800', 'name': '쓰레기 문제'},
    'academic': {'icon': '📚', 'color': 'bg-purple-100 text-purple-800', 'name': '수업/학사'},
    'activity': {'icon': '🎭', 'color': 'bg-yellow-100 text-yellow-800', 'name': '동아리/활동'},
    'environment': {'icon': '🌱', 'color': 'bg-emerald-100 text-emerald-800', 'name': '학교 환경'},
    'safety': {'icon': '🛡️', 'color': 'bg-red-100 text-red-800', 'name': '안전 관련'},
    'library': {'icon': '📖', 'color': 'bg-indigo-100 text-indigo-800', 'name': '도서관'},
    'sports': {'icon': '⚽', 'color': 'bg-teal-100 text-teal-800', 'name': '체육/운동'},
    'other': {'icon': '💭', 'color': 'bg-gray-100 text-gray-800', 'name': '기타'}
}

STATUS_CONFIG = {
    'pending': {'color': 'bg-yellow-100 text-yellow-800', 'name': '검토중'},
    'in-progress': {'color': 'bg-blue-100 text-blue-800', 'name': '처리중'},
    'completed': {'color': 'bg-green-100 text-green-800', 'name': '완료'}
}


def load_suggestions():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_suggestions(suggestions):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    suggestions = load_suggestions()
    return render_template(
        'index.html',
        suggestions=suggestions,
        is_admin=session.get('is_admin', False),
        admin_id=session.get('admin_id', ''),
        category_config=CATEGORY_CONFIG,
        status_config=STATUS_CONFIG
    )


@app.route('/submit_suggestion', methods=['POST'])
def submit_suggestion():
    data = request.get_json()
    is_anonymous = data.get('anonymous', False)
    student_name = '익명' if is_anonymous else (data.get('studentName') or '익명')
    student_grade = '' if is_anonymous else (data.get('studentGrade') or '')

    suggestion = {
        'id': int(datetime.now().timestamp() * 1000),
        'studentName': student_name,
        'studentGrade': student_grade,
        'category': data.get('category'),
        'title': data.get('title'),
        'content': data.get('content'),
        'status': 'pending',
        'createdAt': datetime.now().strftime('%Y. %m. %d. %H:%M:%S'),
        'adminResponse': '',
        'responseDate': ''
    }

    suggestions = load_suggestions()
    suggestions.insert(0, suggestion)
    save_suggestions(suggestions)

    return jsonify({'success': True})


@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin_id = data.get('adminId')
    password = data.get('password')

    if admin_id in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[admin_id] == password:
        session['is_admin'] = True
        session['admin_id'] = admin_id
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'})


@app.route('/admin_logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/admin_response', methods=['POST'])
def admin_response():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})

    data = request.get_json()
    suggestion_id = data.get('suggestionId')
    status = data.get('status')
    response = data.get('response')

    suggestions = load_suggestions()
    for s in suggestions:
        if s['id'] == suggestion_id:
            s['status'] = status
            s['adminResponse'] = response
            s['responseDate'] = datetime.now().strftime('%Y. %m. %d. %H:%M:%S')
            break

    save_suggestions(suggestions)
    return jsonify({'success': True})


@app.route('/delete_suggestion', methods=['POST'])
def delete_suggestion():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})

    data = request.get_json()
    suggestion_id = data.get('suggestionId')

    suggestions = load_suggestions()
    suggestion_to_delete = None
    
    for s in suggestions:
        if s['id'] == suggestion_id:
            suggestion_to_delete = s
            break
    
    if suggestion_to_delete is None:
        return jsonify({'success': False, 'message': '건의사항을 찾을 수 없습니다.'})
    

    
    suggestions = [s for s in suggestions if s['id'] != suggestion_id]
    save_suggestions(suggestions)
    
    return jsonify({'success': True})


@app.route('/get_suggestions')
def get_suggestions():
    suggestions = load_suggestions()
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')

    if category_filter:
        suggestions = [s for s in suggestions if s['category'] == category_filter]
    if status_filter:
        suggestions = [s for s in suggestions if s['status'] == status_filter]

    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)