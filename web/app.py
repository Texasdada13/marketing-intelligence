"""Marketing Intelligence - Flask Web Application"""
import os
import sys
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_config
from src.database.models import db, Organization, Campaign, Channel, Content, MarketingMetrics, BenchmarkResult, ChatSession, ChatMessage
from src.database.repository import OrganizationRepository, CampaignRepository, ChannelRepository, ContentRepository, ChatRepository, BenchmarkResultRepository
from src.ai_core.chat_engine import ChatEngine, ConversationMode
from src.patterns.benchmark_engine import create_marketing_benchmarks, create_digital_benchmarks


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='../static')

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Initialize AI engine
    try:
        chat_engine = ChatEngine()
    except Exception as e:
        print(f"Warning: Could not initialize ChatEngine: {e}")
        chat_engine = None

    # Initialize benchmark engines
    marketing_benchmark = create_marketing_benchmarks()
    digital_benchmark = create_digital_benchmarks()

    # ==================== PAGE ROUTES ====================

    @app.route('/')
    def index():
        """Landing page."""
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        """Marketing dashboard."""
        organizations = OrganizationRepository.get_all()
        return render_template('dashboard.html', organizations=organizations)

    @app.route('/organization/<org_id>')
    def organization_detail(org_id):
        """Organization detail page."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return render_template('404.html'), 404

        campaigns = CampaignRepository.get_by_organization(org_id)
        channels = ChannelRepository.get_by_organization(org_id)
        content = ContentRepository.get_by_organization(org_id)
        benchmark = BenchmarkResultRepository.get_latest(org_id)

        return render_template('organization.html',
                               organization=org,
                               campaigns=campaigns,
                               channels=channels,
                               content=content,
                               benchmark=benchmark)

    @app.route('/chat')
    def chat_page():
        """AI CMO Consultant chat interface."""
        modes = {mode.value: desc for mode, desc in [
            (ConversationMode.GENERAL, "General marketing questions"),
            (ConversationMode.CAMPAIGN_ANALYSIS, "Campaign performance analysis"),
            (ConversationMode.CHANNEL_OPTIMIZATION, "Channel mix optimization"),
            (ConversationMode.CONTENT_STRATEGY, "Content strategy"),
            (ConversationMode.FUNNEL_ANALYSIS, "Funnel optimization"),
            (ConversationMode.ROI_REVIEW, "ROI and efficiency"),
            (ConversationMode.BENCHMARK_DISCUSSION, "Industry benchmarks"),
            (ConversationMode.MARKETING_PLANNING, "Strategic planning"),
        ]}
        return render_template('chat.html', modes=modes)

    # ==================== API ROUTES ====================

    @app.route('/api/organizations', methods=['GET', 'POST'])
    def api_organizations():
        """Organization API endpoint."""
        if request.method == 'POST':
            data = request.json
            org = OrganizationRepository.create(
                name=data.get('name'),
                industry=data.get('industry'),
                size=data.get('size'),
                annual_marketing_budget=data.get('annual_marketing_budget')
            )
            return jsonify(org.to_dict()), 201

        organizations = OrganizationRepository.get_all()
        return jsonify([org.to_dict() for org in organizations])

    @app.route('/api/organizations/<org_id>', methods=['GET', 'PUT', 'DELETE'])
    def api_organization(org_id):
        """Single organization API endpoint."""
        if request.method == 'DELETE':
            success = OrganizationRepository.delete(org_id)
            return jsonify({'success': success})

        if request.method == 'PUT':
            data = request.json
            org = OrganizationRepository.update(org_id, **data)
            return jsonify(org.to_dict()) if org else ('Not found', 404)

        org = OrganizationRepository.get_by_id(org_id)
        return jsonify(org.to_dict()) if org else ('Not found', 404)

    @app.route('/api/organizations/<org_id>/campaigns', methods=['GET', 'POST'])
    def api_campaigns(org_id):
        """Campaign API endpoint."""
        if request.method == 'POST':
            data = request.json
            campaign = CampaignRepository.create(organization_id=org_id, **data)
            return jsonify(campaign.to_dict()), 201

        campaigns = CampaignRepository.get_by_organization(org_id)
        return jsonify([c.to_dict() for c in campaigns])

    @app.route('/api/organizations/<org_id>/channels', methods=['GET', 'POST'])
    def api_channels(org_id):
        """Channel API endpoint."""
        if request.method == 'POST':
            data = request.json
            channel = ChannelRepository.create(organization_id=org_id, **data)
            return jsonify(channel.to_dict()), 201

        channels = ChannelRepository.get_by_organization(org_id)
        return jsonify([c.to_dict() for c in channels])

    @app.route('/api/organizations/<org_id>/benchmark', methods=['POST'])
    def api_run_benchmark(org_id):
        """Run marketing benchmark analysis."""
        data = request.json or {}
        benchmark_type = data.get('type', 'marketing')

        # Get metrics for benchmarking
        actual_values = data.get('metrics', {})

        if benchmark_type == 'marketing':
            report = marketing_benchmark.analyze(actual_values, org_id)
        else:
            report = digital_benchmark.analyze(actual_values, org_id)

        # Save result
        result = BenchmarkResultRepository.create(
            organization_id=org_id,
            benchmark_type=benchmark_type,
            overall_score=report.overall_score,
            overall_rating=report.overall_rating,
            grade=report.grade,
            category_scores=report.category_scores,
            strengths=report.strengths,
            improvements=report.improvements,
            recommendations=report.recommendations
        )

        return jsonify(result.to_dict())

    # ==================== CHAT API ====================

    @app.route('/api/chat/sessions', methods=['GET', 'POST'])
    def api_chat_sessions():
        """Chat session management."""
        if request.method == 'POST':
            data = request.json
            session = ChatRepository.create_session(
                mode=data.get('mode', 'general'),
                organization_id=data.get('organization_id'),
                title=data.get('title'),
                context=data.get('context')
            )
            return jsonify(session.to_dict()), 201

        sessions = ChatRepository.get_sessions(limit=20)
        return jsonify([s.to_dict() for s in sessions])

    @app.route('/api/chat/sessions/<session_id>', methods=['GET', 'DELETE'])
    def api_chat_session(session_id):
        """Single chat session."""
        if request.method == 'DELETE':
            success = ChatRepository.delete_session(session_id)
            return jsonify({'success': success})

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        messages = ChatRepository.get_messages(session_id)
        return jsonify({
            'session': session.to_dict(),
            'messages': [m.to_dict() for m in messages]
        })

    @app.route('/api/chat/sessions/<session_id>/messages', methods=['POST'])
    def api_chat_message(session_id):
        """Send a chat message and get AI response."""
        if not chat_engine:
            return jsonify({'error': 'Chat engine not available'}), 503

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        user_message = data.get('message', '')

        # Save user message
        ChatRepository.add_message(session_id, 'user', user_message)

        # Get conversation history
        messages = ChatRepository.get_messages(session_id)
        history = [{'role': m.role, 'content': m.content} for m in messages[:-1]]

        # Get mode and context
        mode = ConversationMode(session.mode) if session.mode else ConversationMode.GENERAL
        context = session.context or {}

        # Get AI response
        response = chat_engine.chat(user_message, mode=mode, history=history, context=context)

        # Save AI response
        ChatRepository.add_message(session_id, 'assistant', response)

        return jsonify({'response': response})

    @app.route('/api/chat/sessions/<session_id>/stream', methods=['POST'])
    def api_chat_stream(session_id):
        """Stream a chat response."""
        if not chat_engine:
            return jsonify({'error': 'Chat engine not available'}), 503

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        user_message = data.get('message', '')

        # Save user message
        ChatRepository.add_message(session_id, 'user', user_message)

        # Get history
        messages = ChatRepository.get_messages(session_id)
        history = [{'role': m.role, 'content': m.content} for m in messages[:-1]]

        mode = ConversationMode(session.mode) if session.mode else ConversationMode.GENERAL
        context = session.context or {}

        def generate():
            full_response = []
            for chunk in chat_engine.chat_stream(user_message, mode=mode, history=history, context=context):
                full_response.append(chunk)
                yield f"data: {chunk}\n\n"

            # Save complete response
            ChatRepository.add_message(session_id, 'assistant', ''.join(full_response))
            yield "data: [DONE]\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    @app.route('/api/chat/prompts/<mode>')
    def api_suggested_prompts(mode):
        """Get suggested prompts for a mode."""
        if chat_engine:
            try:
                prompts = chat_engine.get_suggested_prompts(ConversationMode(mode))
                return jsonify({'prompts': prompts})
            except ValueError:
                pass
        return jsonify({'prompts': []})

    # ==================== HEALTH CHECK ====================

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'marketing-intelligence',
            'ai_enabled': chat_engine is not None
        })

    # ==================== ERROR HANDLERS ====================

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500

    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
