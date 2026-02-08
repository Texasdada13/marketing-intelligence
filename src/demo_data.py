"""Demo Data Generator for Marketing Intelligence"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List


def generate_demo_data(org_name: str = "Demo Company") -> Dict[str, Any]:
    """Generate comprehensive demo data for Marketing Intelligence."""

    org_id = f"demo-{random.randint(1000, 9999)}"

    return {
        'organization': generate_organization(org_id, org_name),
        'campaigns': generate_campaigns(org_id),
        'channels': generate_channels(org_id),
        'content': generate_content(org_id),
        'metrics': generate_marketing_metrics(org_id),
        'benchmarks': generate_benchmarks(org_id),
    }


def generate_organization(org_id: str, name: str) -> Dict[str, Any]:
    """Generate demo organization."""
    industries = ['Technology', 'E-commerce', 'SaaS', 'Healthcare', 'Financial Services']
    sizes = ['SMB', 'Mid-Market', 'Enterprise']
    budgets = {'SMB': 150000, 'Mid-Market': 500000, 'Enterprise': 2000000}

    size = random.choice(sizes)
    return {
        'id': org_id,
        'name': name,
        'industry': random.choice(industries),
        'size': size,
        'annual_marketing_budget': budgets[size] * random.uniform(0.8, 1.2),
    }


def generate_campaigns(org_id: str) -> List[Dict[str, Any]]:
    """Generate demo campaigns with varied performance."""
    campaign_templates = [
        ('Q1 Product Launch', 'Product Launch', 50000, 'excellent'),
        ('Brand Awareness Push', 'Brand Awareness', 35000, 'good'),
        ('Summer Sale Campaign', 'Promotional', 25000, 'average'),
        ('Lead Gen - LinkedIn', 'Lead Generation', 20000, 'excellent'),
        ('Retargeting Campaign', 'Retargeting', 15000, 'good'),
        ('Holiday Campaign', 'Promotional', 40000, 'poor'),  # Some underperformers
        ('Email Nurture Series', 'Lead Generation', 10000, 'average'),
        ('Webinar Promotion', 'Event', 12000, 'good'),
    ]

    campaigns = []
    for name, ctype, budget, performance in campaign_templates:
        perf_multipliers = {
            'excellent': (1.2, 1.5, 85, 95),
            'good': (0.9, 1.2, 70, 84),
            'average': (0.6, 0.9, 50, 69),
            'poor': (0.3, 0.6, 30, 49),
        }
        mult = perf_multipliers[performance]

        spend = budget * random.uniform(0.7, 1.0)
        impressions = int(spend * random.uniform(80, 150))
        clicks = int(impressions * random.uniform(0.02, 0.05))
        conversions = int(clicks * random.uniform(0.03, 0.08))
        revenue = spend * random.uniform(mult[0], mult[1])

        start_date = datetime.now() - timedelta(days=random.randint(30, 120))

        campaigns.append({
            'id': f"camp-{random.randint(10000, 99999)}",
            'organization_id': org_id,
            'name': name,
            'campaign_type': ctype,
            'status': random.choice(['active', 'active', 'active', 'completed']),
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(days=random.randint(30, 90))).isoformat(),
            'budget': budget,
            'spend': round(spend, 2),
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'leads': int(conversions * random.uniform(2, 4)),
            'revenue': round(revenue, 2),
            'performance_score': random.uniform(mult[2], mult[3]),
            'roi_score': round((revenue / spend - 1) * 100, 1) if spend > 0 else 0,
            'overall_score': random.uniform(mult[2], mult[3]),
            'rating': performance.title(),
        })

    return campaigns


def generate_channels(org_id: str) -> List[Dict[str, Any]]:
    """Generate demo channel data."""
    channel_templates = [
        ('Google Ads', 'Paid Search', 30000, 320),
        ('Facebook Ads', 'Paid Social', 20000, 180),
        ('LinkedIn Ads', 'Paid Social', 15000, 420),
        ('Organic Search', 'Organic', 0, 280),
        ('Email Marketing', 'Email', 2000, 150),
        ('Direct Traffic', 'Direct', 0, 200),
        ('Referral', 'Referral', 0, 250),
        ('Display Advertising', 'Display', 8000, 90),
    ]

    channels = []
    for name, ctype, spend, base_roas in channel_templates:
        impressions = int((spend if spend > 0 else 50000) * random.uniform(50, 100))
        clicks = int(impressions * random.uniform(0.015, 0.04))
        conversions = int(clicks * random.uniform(0.02, 0.06))
        revenue = spend * (base_roas / 100) * random.uniform(0.8, 1.2) if spend > 0 else random.uniform(20000, 80000)

        channels.append({
            'id': f"chan-{random.randint(10000, 99999)}",
            'organization_id': org_id,
            'name': name,
            'channel_type': ctype,
            'status': 'active',
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'spend': round(spend, 2),
            'revenue': round(revenue, 2),
            'leads': int(conversions * random.uniform(1.5, 3)),
            'new_customers': int(conversions * random.uniform(0.3, 0.6)),
            'ctr': round(clicks / impressions * 100, 2) if impressions > 0 else 0,
            'conversion_rate': round(conversions / clicks * 100, 2) if clicks > 0 else 0,
            'cpc': round(spend / clicks, 2) if clicks > 0 else 0,
            'cpa': round(spend / conversions, 2) if conversions > 0 else 0,
            'roas': round(revenue / spend * 100, 1) if spend > 0 else 0,
            'efficiency_score': random.uniform(50, 95),
            'rating': random.choice(['Excellent', 'Good', 'Average']),
        })

    return channels


def generate_content(org_id: str) -> List[Dict[str, Any]]:
    """Generate demo content performance data."""
    content_templates = [
        ('Ultimate Guide to Growth Marketing', 'Blog', 'TOFU'),
        ('Product Demo Video', 'Video', 'MOFU'),
        ('ROI Calculator Tool', 'Interactive', 'BOFU'),
        ('Industry Trends 2024', 'Whitepaper', 'TOFU'),
        ('Customer Success Stories', 'Case Study', 'BOFU'),
        ('Getting Started Tutorial', 'Video', 'MOFU'),
        ('Pricing Comparison Guide', 'Blog', 'BOFU'),
        ('Monthly Newsletter', 'Email', 'MOFU'),
        ('Webinar Recording', 'Video', 'MOFU'),
        ('Product Features Overview', 'Landing Page', 'BOFU'),
    ]

    content_items = []
    for title, ctype, stage in content_templates:
        views = random.randint(500, 15000)

        content_items.append({
            'id': f"cont-{random.randint(10000, 99999)}",
            'organization_id': org_id,
            'title': title,
            'content_type': ctype,
            'funnel_stage': stage,
            'status': 'published',
            'publish_date': (datetime.now() - timedelta(days=random.randint(10, 180))).isoformat(),
            'views': views,
            'unique_visitors': int(views * random.uniform(0.7, 0.9)),
            'time_on_page': random.uniform(45, 300),
            'bounce_rate': random.uniform(30, 70),
            'shares': int(views * random.uniform(0.01, 0.05)),
            'comments': int(views * random.uniform(0.001, 0.01)),
            'downloads': int(views * random.uniform(0.02, 0.1)) if ctype in ['Whitepaper', 'Case Study'] else 0,
            'leads_generated': int(views * random.uniform(0.01, 0.04)),
            'conversions': int(views * random.uniform(0.005, 0.02)),
            'engagement_score': random.uniform(40, 95),
            'conversion_score': random.uniform(30, 90),
            'overall_score': random.uniform(45, 90),
            'rating': random.choice(['Excellent', 'Good', 'Average', 'Good']),
        })

    return content_items


def generate_marketing_metrics(org_id: str) -> Dict[str, Any]:
    """Generate overall marketing metrics."""
    return {
        'id': f"metr-{random.randint(10000, 99999)}",
        'organization_id': org_id,
        'period': 'monthly',
        'period_start': (datetime.now() - timedelta(days=30)).isoformat(),
        'period_end': datetime.now().isoformat(),
        'cac': round(random.uniform(80, 200), 2),
        'cpl': round(random.uniform(25, 75), 2),
        'website_traffic': random.randint(50000, 200000),
        'organic_traffic_pct': round(random.uniform(35, 55), 1),
        'conversion_rate': round(random.uniform(2, 5), 2),
        'lead_to_customer_rate': round(random.uniform(10, 25), 1),
        'cart_abandonment_rate': round(random.uniform(60, 75), 1),
        'email_open_rate': round(random.uniform(18, 35), 1),
        'email_ctr': round(random.uniform(2, 6), 2),
        'social_engagement_rate': round(random.uniform(1, 4), 2),
        'customer_retention_rate': round(random.uniform(85, 95), 1),
        'churn_rate': round(random.uniform(2, 8), 1),
        'clv': round(random.uniform(800, 3000), 2),
        'roas': round(random.uniform(150, 400), 1),
        'marketing_roi': round(random.uniform(50, 200), 1),
        'total_revenue': round(random.uniform(500000, 2000000), 2),
        'total_spend': round(random.uniform(100000, 400000), 2),
        'brand_awareness': round(random.uniform(20, 45), 1),
        'nps': round(random.uniform(30, 70), 0),
    }


def generate_benchmarks(org_id: str) -> Dict[str, Any]:
    """Generate benchmark comparison data."""
    categories = ['Brand Awareness', 'Lead Generation', 'Conversion', 'ROI', 'Content', 'Digital Presence']

    category_scores = {}
    for cat in categories:
        category_scores[cat] = {
            'score': random.uniform(50, 90),
            'benchmark': 70,
            'status': random.choice(['Above', 'At', 'Below']),
        }

    overall = sum(c['score'] for c in category_scores.values()) / len(categories)

    return {
        'id': f"bench-{random.randint(10000, 99999)}",
        'organization_id': org_id,
        'benchmark_type': 'marketing',
        'overall_score': round(overall, 1),
        'overall_rating': 'Good' if overall >= 70 else 'Average' if overall >= 50 else 'Needs Improvement',
        'grade': 'A' if overall >= 85 else 'B' if overall >= 70 else 'C' if overall >= 55 else 'D',
        'category_scores': category_scores,
        'strengths': [
            'Strong organic search presence',
            'Above-average email marketing performance',
            'Good customer retention metrics',
        ],
        'improvements': [
            'Social media engagement below industry average',
            'Paid advertising efficiency could improve',
            'Content distribution needs optimization',
        ],
        'recommendations': [
            'Increase investment in high-performing channels',
            'Implement A/B testing for underperforming campaigns',
            'Develop comprehensive content calendar',
            'Consider marketing automation tools',
        ],
    }


def load_demo_data_to_db(db, models, org_name: str = "Acme Corp"):
    """Load demo data into the database."""
    data = generate_demo_data(org_name)

    # Create organization
    org = models.Organization(
        id=data['organization']['id'],
        name=data['organization']['name'],
        industry=data['organization']['industry'],
        size=data['organization']['size'],
        annual_marketing_budget=data['organization']['annual_marketing_budget'],
    )
    db.session.add(org)

    # Create campaigns
    for c in data['campaigns']:
        from datetime import datetime
        campaign = models.Campaign(
            id=c['id'],
            organization_id=c['organization_id'],
            name=c['name'],
            campaign_type=c['campaign_type'],
            status=c['status'],
            start_date=datetime.fromisoformat(c['start_date']),
            budget=c['budget'],
            spend=c['spend'],
            impressions=c['impressions'],
            clicks=c['clicks'],
            conversions=c['conversions'],
            leads=c['leads'],
            revenue=c['revenue'],
            performance_score=c['performance_score'],
            roi_score=c['roi_score'],
            overall_score=c['overall_score'],
            rating=c['rating'],
        )
        db.session.add(campaign)

    # Create channels
    for ch in data['channels']:
        channel = models.Channel(
            id=ch['id'],
            organization_id=ch['organization_id'],
            name=ch['name'],
            channel_type=ch['channel_type'],
            status=ch['status'],
            impressions=ch['impressions'],
            clicks=ch['clicks'],
            conversions=ch['conversions'],
            spend=ch['spend'],
            revenue=ch['revenue'],
            leads=ch['leads'],
            new_customers=ch['new_customers'],
            ctr=ch['ctr'],
            conversion_rate=ch['conversion_rate'],
            cpc=ch['cpc'],
            cpa=ch['cpa'],
            roas=ch['roas'],
            efficiency_score=ch['efficiency_score'],
            rating=ch['rating'],
        )
        db.session.add(channel)

    # Create content
    for ct in data['content']:
        content = models.Content(
            id=ct['id'],
            organization_id=ct['organization_id'],
            title=ct['title'],
            content_type=ct['content_type'],
            funnel_stage=ct['funnel_stage'],
            status=ct['status'],
            views=ct['views'],
            unique_visitors=ct['unique_visitors'],
            time_on_page=ct['time_on_page'],
            bounce_rate=ct['bounce_rate'],
            shares=ct['shares'],
            downloads=ct['downloads'],
            leads_generated=ct['leads_generated'],
            conversions=ct['conversions'],
            engagement_score=ct['engagement_score'],
            conversion_score=ct['conversion_score'],
            overall_score=ct['overall_score'],
            rating=ct['rating'],
        )
        db.session.add(content)

    # Create metrics
    m = data['metrics']
    from datetime import datetime
    metrics = models.MarketingMetrics(
        id=m['id'],
        organization_id=m['organization_id'],
        period=m['period'],
        period_start=datetime.fromisoformat(m['period_start']),
        period_end=datetime.fromisoformat(m['period_end']),
        cac=m['cac'],
        cpl=m['cpl'],
        website_traffic=m['website_traffic'],
        organic_traffic_pct=m['organic_traffic_pct'],
        conversion_rate=m['conversion_rate'],
        lead_to_customer_rate=m['lead_to_customer_rate'],
        cart_abandonment_rate=m['cart_abandonment_rate'],
        email_open_rate=m['email_open_rate'],
        email_ctr=m['email_ctr'],
        social_engagement_rate=m['social_engagement_rate'],
        customer_retention_rate=m['customer_retention_rate'],
        churn_rate=m['churn_rate'],
        clv=m['clv'],
        roas=m['roas'],
        marketing_roi=m['marketing_roi'],
        total_revenue=m['total_revenue'],
        total_spend=m['total_spend'],
        brand_awareness=m['brand_awareness'],
        nps=m['nps'],
    )
    db.session.add(metrics)

    # Create benchmark
    b = data['benchmarks']
    benchmark = models.BenchmarkResult(
        id=b['id'],
        organization_id=b['organization_id'],
        benchmark_type=b['benchmark_type'],
        overall_score=b['overall_score'],
        overall_rating=b['overall_rating'],
        grade=b['grade'],
        category_scores=b['category_scores'],
        strengths=b['strengths'],
        improvements=b['improvements'],
        recommendations=b['recommendations'],
    )
    db.session.add(benchmark)

    db.session.commit()

    return data['organization']['id']
