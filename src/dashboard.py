from flask import Flask, render_template, jsonify, send_from_directory
import os

class Dashboard:
    def __init__(self, state):
        self.state = state
        self.app = Flask(__name__, 
                        template_folder=os.path.abspath('templates'),
                        static_folder=os.path.abspath('static'))
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/state')
        def get_state():
            return jsonify(self.state.get_state())
        
        @self.app.route('/static/images/<path:filename>')
        def serve_image(filename):
            return send_from_directory('static/images', filename)
    
    def run(self, host='0.0.0.0', port=5000):
        """Flask 서버 실행"""
        try:
            print(f"웹 서버 시작: http://{host}:{port}")
            self.app.run(host=host, port=port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"웹 서버 시작 중 오류 발생: {e}") 