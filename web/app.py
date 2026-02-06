"""Marketing Intelligence - Flask Web Application"""
import os
import sys
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_config
from src.database.models import db, Organization, Campaign, Channel, Content, MarketingMetrics, BenchmarkResult, ChatSession, ChatMessage, UploadedFile
from src.database.repository import OrganizationRepository, CampaignRepository, ChannelRepository, ContentRepository, ChatRepository, BenchmarkResultRepository
from src.ai_core.chat_engine import ChatEngine, ConversationMode
from src.ai_core.file_analyzer import create_file_analyzer
from src.patterns.benchmark_engine import create_marketing_benchmarks, create_digital_benchmarks
from src.demo.data_generator import create_marketing_demo_generator
from src.reports.report_generator import create_report_generator
from src.alerts.alert_engine import create_alert_engine


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

    # Initialize file analyzer, report generator, and alert engine
    file_analyzer = create_file_analyzer()
    report_generator = create_report_generator()
    alert_engine = create_alert_engine()

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

    @app.route('/api/chat/sessions/<session_id>/suggestions', methods=['GET'])
    def api_chat_suggestions(session_id):
        """Get context-aware suggestions for a chat session."""
        if not chat_engine:
            return jsonify({'suggestions': [], 'error': 'Chat engine not available'}), 503

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Get conversation history
        messages = ChatRepository.get_messages(session_id)
        history = [{'role': m.role, 'content': m.content} for m in messages]

        # Build context from session
        context = session.context or {}

        # Get discussed topics and dismissed prompts
        discussed_topics = session.discussed_topics or []
        dismissed_prompts = session.dismissed_suggestions or []

        # Get dynamic suggestions
        suggestions = chat_engine.get_dynamic_suggestions(
            mode=session.mode or 'general',
            context=context,
            conversation_history=history,
            discussed_topics=discussed_topics,
            dismissed_prompts=dismissed_prompts,
            max_suggestions=4
        )

        return jsonify({
            'suggestions': suggestions,
            'context_summary': {
                'mode': session.mode,
                'discussed_topics': discussed_topics,
                'message_count': len(messages)
            }
        })

    @app.route('/api/chat/sessions/<session_id>/dismiss', methods=['POST'])
    def api_dismiss_suggestion(session_id):
        """Dismiss a suggestion so it won't appear again."""
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        prompt_text = data.get('prompt')

        if prompt_text:
            dismissed = session.dismissed_suggestions or []
            if prompt_text not in dismissed:
                dismissed.append(prompt_text)
                session.dismissed_suggestions = dismissed
                db.session.commit()

        return jsonify({'success': True})

    @app.route('/api/chat/sessions/<session_id>/topics', methods=['POST'])
    def api_track_topics(session_id):
        """Track discussed topics from a message."""
        if not chat_engine:
            return jsonify({'error': 'Chat engine not available'}), 503

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        message = data.get('message', '')

        # Extract topics from message
        new_topics = chat_engine.extract_topics(message)

        # Add to discussed topics
        discussed = session.discussed_topics or []
        for topic in new_topics:
            if topic not in discussed:
                discussed.append(topic)

        session.discussed_topics = discussed
        db.session.commit()

        return jsonify({
            'new_topics': new_topics,
            'all_topics': discussed
        })

    # ==================== FILE UPLOAD API ====================

    @app.route('/api/chat/sessions/<session_id>/upload', methods=['POST'])
    def api_upload_file(session_id):
        """Upload a file for analysis."""
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read file content
        content = file.read()
        filename = file.filename

        # Analyze file
        try:
            result = file_analyzer.analyze_file(content, filename)
        except Exception as e:
            return jsonify({'error': f'Failed to analyze file: {str(e)}'}), 400

        # Save to database
        uploaded_file = UploadedFile(
            session_id=session_id,
            filename=filename,
            file_type=result.file_type,
            file_size=len(content),
            analysis_result=result.to_dict(),
            context_summary=result.data_summary,
            row_count=result.row_count,
            column_count=result.column_count,
            detected_metrics=result.detected_metrics
        )
        db.session.add(uploaded_file)
        db.session.commit()

        return jsonify({
            'file_id': uploaded_file.id,
            'filename': filename,
            'analysis': result.to_dict()
        }), 201

    @app.route('/api/chat/sessions/<session_id>/files', methods=['GET'])
    def api_list_files(session_id):
        """List files uploaded to a session."""
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        files = UploadedFile.query.filter_by(session_id=session_id).all()
        return jsonify({
            'files': [f.to_dict() for f in files]
        })

    @app.route('/api/chat/sessions/<session_id>/files/<file_id>', methods=['GET', 'DELETE'])
    def api_file_detail(session_id, file_id):
        """Get or delete a specific file."""
        uploaded_file = UploadedFile.query.filter_by(id=file_id, session_id=session_id).first()
        if not uploaded_file:
            return jsonify({'error': 'File not found'}), 404

        if request.method == 'DELETE':
            db.session.delete(uploaded_file)
            db.session.commit()
            return jsonify({'success': True})

        return jsonify(uploaded_file.to_dict())

    # ==================== DASHBOARD API ====================

    @app.route('/api/dashboard/<org_id>')
    def api_dashboard_data(org_id):
        """Get dashboard data for an organization."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        channels = ChannelRepository.get_by_organization(org_id)
        campaigns = CampaignRepository.get_by_organization(org_id)
        benchmark = BenchmarkResultRepository.get_latest(org_id)

        # Calculate metrics
        total_revenue = sum(c.revenue or 0 for c in channels)
        total_spend = sum(c.spend or 0 for c in channels)
        total_conversions = sum(c.conversions or 0 for c in channels)
        roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0

        # Channel data for charts
        channel_data = [{
            'name': c.name,
            'spend': c.spend or 0,
            'revenue': c.revenue or 0,
            'conversions': c.conversions or 0,
            'roi': round((c.revenue - c.spend) / c.spend * 100, 1) if c.spend and c.spend > 0 else 0
        } for c in channels]

        # Campaign data for charts
        campaign_data = [{
            'name': c.name,
            'channel': c.channel,
            'status': c.status,
            'budget': c.budget or 0,
            'spent': c.spent or 0,
            'leads': c.leads or 0
        } for c in campaigns]

        # Trend data (mock for now - in production, query historical data)
        import random
        trend_data = {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
            'revenue': [int(total_revenue * (0.7 + random.random() * 0.1 * i)) for i in range(6)],
            'spend': [int(total_spend * (0.8 + random.random() * 0.05 * i)) for i in range(6)]
        }

        return jsonify({
            'organization': org.to_dict(),
            'metrics': {
                'total_revenue': total_revenue,
                'total_spend': total_spend,
                'roas': roas,
                'total_conversions': total_conversions
            },
            'channels': channel_data,
            'campaigns': campaign_data,
            'trend_data': trend_data,
            'benchmark': benchmark.to_dict() if benchmark else None
        })

    # ==================== EXPORT API ====================

    @app.route('/api/export/<org_id>/csv')
    def api_export_csv(org_id):
        """Export dashboard data as CSV."""
        # Get dashboard data
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        channels = ChannelRepository.get_by_organization(org_id)
        campaigns = CampaignRepository.get_by_organization(org_id)

        total_revenue = sum(c.revenue or 0 for c in channels)
        total_spend = sum(c.spend or 0 for c in channels)
        total_conversions = sum(c.conversions or 0 for c in channels)
        roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0

        data = {
            'metrics': {
                'total_revenue': total_revenue,
                'total_spend': total_spend,
                'roas': roas,
                'total_conversions': total_conversions
            },
            'channels': [{
                'name': c.name,
                'spend': c.spend or 0,
                'revenue': c.revenue or 0,
                'conversions': c.conversions or 0,
                'roi': round((c.revenue - c.spend) / c.spend * 100, 1) if c.spend and c.spend > 0 else 0
            } for c in channels],
            'campaigns': [{
                'name': c.name,
                'channel': c.channel,
                'status': c.status,
                'budget': c.budget or 0,
                'spent': c.spent or 0,
                'leads': c.leads or 0
            } for c in campaigns]
        }

        report_type = request.args.get('type', 'full')
        csv_content = report_generator.generate_csv(data, report_type)

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=marketing_report_{org_id}.csv'}
        )

    @app.route('/api/export/<org_id>/html')
    def api_export_html(org_id):
        """Export dashboard data as HTML report."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        channels = ChannelRepository.get_by_organization(org_id)
        campaigns = CampaignRepository.get_by_organization(org_id)

        total_revenue = sum(c.revenue or 0 for c in channels)
        total_spend = sum(c.spend or 0 for c in channels)
        total_conversions = sum(c.conversions or 0 for c in channels)
        roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0

        data = {
            'metrics': {
                'total_revenue': total_revenue,
                'total_spend': total_spend,
                'roas': roas,
                'total_conversions': total_conversions
            },
            'channels': [{
                'name': c.name,
                'spend': c.spend or 0,
                'revenue': c.revenue or 0,
                'conversions': c.conversions or 0,
                'roi': round((c.revenue - c.spend) / c.spend * 100, 1) if c.spend and c.spend > 0 else 0
            } for c in channels],
            'campaigns': [{
                'name': c.name,
                'channel': c.channel,
                'status': c.status,
                'budget': c.budget or 0,
                'spent': c.spent or 0,
                'leads': c.leads or 0
            } for c in campaigns]
        }

        html_content = report_generator.generate_html_report(data, org.name)
        return Response(html_content, mimetype='text/html')

    # ==================== ALERTS API ====================

    @app.route('/api/alerts/<org_id>')
    def api_get_alerts(org_id):
        """Get alerts for an organization based on current metrics."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        channels = ChannelRepository.get_by_organization(org_id)
        campaigns = CampaignRepository.get_by_organization(org_id)

        total_revenue = sum(c.revenue or 0 for c in channels)
        total_spend = sum(c.spend or 0 for c in channels)
        total_conversions = sum(c.conversions or 0 for c in channels)
        roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0

        data = {
            'metrics': {
                'total_revenue': total_revenue,
                'total_spend': total_spend,
                'roas': roas,
                'total_conversions': total_conversions
            },
            'channels': [{
                'name': c.name,
                'spend': c.spend or 0,
                'revenue': c.revenue or 0,
                'conversions': c.conversions or 0,
                'roi': round((c.revenue - c.spend) / c.spend * 100, 1) if c.spend and c.spend > 0 else 0
            } for c in channels],
            'campaigns': [{
                'name': c.name,
                'channel': c.channel,
                'status': c.status,
                'budget': c.budget or 0,
                'spent': c.spent or 0,
                'leads': c.leads or 0
            } for c in campaigns]
        }

        alerts = alert_engine.check_metrics(data)
        summary = alert_engine.get_alert_summary(alerts)

        return jsonify({
            'alerts': [a.to_dict() for a in alerts],
            'summary': summary
        })

    # ==================== DEMO DATA API ====================

    @app.route('/api/demo/generate', methods=['POST'])
    def api_generate_demo():
        """Generate demo marketing data."""
        data = request.json or {}
        org_name = data.get('organization_name')
        seed = data.get('seed')

        generator = create_marketing_demo_generator(seed)
        demo_data = generator.generate_full_demo(org_name)

        return jsonify(demo_data)

    @app.route('/api/demo/load', methods=['POST'])
    def api_load_demo():
        """Generate demo data and load it into the database."""
        data = request.json or {}
        org_name = data.get('organization_name', 'Demo Marketing Co')
        seed = data.get('seed')

        generator = create_marketing_demo_generator(seed)
        demo_data = generator.generate_full_demo(org_name)

        # Create organization
        org = OrganizationRepository.create(
            name=demo_data['organization']['name'],
            industry=demo_data['organization']['industry'],
            annual_marketing_budget=demo_data['organization']['monthly_budget'] * 12
        )

        # Create channels
        for channel_data in demo_data['channels']:
            ChannelRepository.create(
                organization_id=org.id,
                name=channel_data['name'],
                channel_type=channel_data['name'].lower().replace(' ', '_'),
                status=channel_data['status'],
                spend=channel_data['spend'],
                revenue=channel_data['revenue'],
                impressions=channel_data['impressions'],
                clicks=channel_data['clicks'],
                conversions=channel_data['conversions']
            )

        # Create campaigns
        for campaign_data in demo_data['campaigns']:
            CampaignRepository.create(
                organization_id=org.id,
                name=campaign_data['name'],
                channel=campaign_data['channel'],
                status=campaign_data['status'],
                budget=campaign_data['budget'],
                spent=campaign_data['spent'],
                leads=campaign_data['leads']
            )

        return jsonify({
            'success': True,
            'organization_id': org.id,
            'organization_name': org.name,
            'channels_created': len(demo_data['channels']),
            'campaigns_created': len(demo_data['campaigns']),
            'metrics_summary': demo_data['metrics_summary']
        }), 201

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
