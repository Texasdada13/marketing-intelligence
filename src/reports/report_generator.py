"""Report generator for Marketing Intelligence dashboards."""
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional


class ReportGenerator:
    """Generate exportable reports from marketing data."""

    def __init__(self):
        self.product_name = "Marketing Intelligence"
        self.product_color = "#e83e8c"  # Pink

    def generate_csv(self, data: Dict[str, Any], report_type: str = 'full') -> str:
        """Generate CSV report from dashboard data."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([f'{self.product_name} Report'])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])

        if report_type in ['full', 'metrics']:
            # Key Metrics
            writer.writerow(['KEY METRICS'])
            writer.writerow(['Metric', 'Value'])
            metrics = data.get('metrics', {})
            writer.writerow(['Total Revenue', f"${metrics.get('total_revenue', 0):,.2f}"])
            writer.writerow(['Total Spend', f"${metrics.get('total_spend', 0):,.2f}"])
            writer.writerow(['ROAS', f"{metrics.get('roas', 0):.2f}x"])
            writer.writerow(['Total Conversions', metrics.get('total_conversions', 0)])
            writer.writerow([])

        if report_type in ['full', 'channels']:
            # Channel Performance
            writer.writerow(['CHANNEL PERFORMANCE'])
            writer.writerow(['Channel', 'Spend', 'Revenue', 'Conversions', 'ROI %'])
            for channel in data.get('channels', []):
                writer.writerow([
                    channel.get('name', ''),
                    f"${channel.get('spend', 0):,.2f}",
                    f"${channel.get('revenue', 0):,.2f}",
                    channel.get('conversions', 0),
                    f"{channel.get('roi', 0):.1f}%"
                ])
            writer.writerow([])

        if report_type in ['full', 'campaigns']:
            # Campaign Performance
            writer.writerow(['CAMPAIGN PERFORMANCE'])
            writer.writerow(['Campaign', 'Channel', 'Status', 'Budget', 'Spent', 'Leads'])
            for campaign in data.get('campaigns', []):
                writer.writerow([
                    campaign.get('name', ''),
                    campaign.get('channel', ''),
                    campaign.get('status', ''),
                    f"${campaign.get('budget', 0):,.2f}",
                    f"${campaign.get('spent', 0):,.2f}",
                    campaign.get('leads', 0)
                ])

        return output.getvalue()

    def generate_html_report(self, data: Dict[str, Any], org_name: str = '') -> str:
        """Generate HTML report for PDF conversion."""
        metrics = data.get('metrics', {})
        channels = data.get('channels', [])
        campaigns = data.get('campaigns', [])

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Marketing Intelligence Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; }}
        .header {{ background: linear-gradient(135deg, {self.product_color}, #6f42c1); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 5px 0 0; opacity: 0.9; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid {self.product_color}; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: {self.product_color}; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        th {{ background: {self.product_color}; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .section-title {{ font-size: 18px; color: #333; margin: 30px 0 15px; border-bottom: 2px solid {self.product_color}; padding-bottom: 5px; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
        .status-active {{ color: #28a745; font-weight: bold; }}
        .status-paused {{ color: #ffc107; }}
        .roi-positive {{ color: #28a745; }}
        .roi-negative {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Marketing Intelligence Report</h1>
        <p>{org_name or 'Organization'} - Generated {datetime.now().strftime("%B %d, %Y")}</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">${metrics.get('total_revenue', 0):,.0f}</div>
            <div class="metric-label">Total Revenue</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${metrics.get('total_spend', 0):,.0f}</div>
            <div class="metric-label">Total Spend</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('roas', 0):.2f}x</div>
            <div class="metric-label">ROAS</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('total_conversions', 0):,}</div>
            <div class="metric-label">Conversions</div>
        </div>
    </div>

    <h2 class="section-title">Channel Performance</h2>
    <table>
        <thead>
            <tr>
                <th>Channel</th>
                <th>Spend</th>
                <th>Revenue</th>
                <th>Conversions</th>
                <th>ROI</th>
            </tr>
        </thead>
        <tbody>'''

        for channel in channels:
            roi = channel.get('roi', 0)
            roi_class = 'roi-positive' if roi > 0 else 'roi-negative'
            html += f'''
            <tr>
                <td><strong>{channel.get('name', '')}</strong></td>
                <td>${channel.get('spend', 0):,.2f}</td>
                <td>${channel.get('revenue', 0):,.2f}</td>
                <td>{channel.get('conversions', 0):,}</td>
                <td class="{roi_class}">{roi:.1f}%</td>
            </tr>'''

        html += '''
        </tbody>
    </table>

    <h2 class="section-title">Campaign Performance</h2>
    <table>
        <thead>
            <tr>
                <th>Campaign</th>
                <th>Channel</th>
                <th>Status</th>
                <th>Budget</th>
                <th>Spent</th>
                <th>Leads</th>
            </tr>
        </thead>
        <tbody>'''

        for campaign in campaigns:
            status = campaign.get('status', 'unknown')
            status_class = 'status-active' if status == 'active' else 'status-paused'
            html += f'''
            <tr>
                <td><strong>{campaign.get('name', '')}</strong></td>
                <td>{campaign.get('channel', '')}</td>
                <td class="{status_class}">{status.title()}</td>
                <td>${campaign.get('budget', 0):,.2f}</td>
                <td>${campaign.get('spent', 0):,.2f}</td>
                <td>{campaign.get('leads', 0):,}</td>
            </tr>'''

        html += f'''
        </tbody>
    </table>

    <div class="footer">
        <p>Generated by Marketing Intelligence - Your Fractional CMO</p>
        <p>Part of the Fractional C-Suite by Patriot Tech Systems</p>
    </div>
</body>
</html>'''

        return html


def create_report_generator() -> ReportGenerator:
    """Factory function to create a report generator."""
    return ReportGenerator()
