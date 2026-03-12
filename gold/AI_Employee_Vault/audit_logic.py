"""
Advanced Audit Logic for Business Transactions and Subscriptions
This module contains the logic for identifying subscription usage, tracking business metrics,
and generating insights for the CEO Briefing.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Subscription patterns for common services
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'microsoft.com': 'Microsoft 365',
    'google.com': 'Google Workspace',
    'amazon.com': 'Amazon Prime',
    'apple.com': 'Apple Services',
    'github.com': 'GitHub Pro',
    'linkedin.com': 'LinkedIn Premium',
    'dropbox.com': 'Dropbox Business',
    'zoom.us': 'Zoom Pro',
    'trello.com': 'Trello Business',
    'asana.com': 'Asana Premium',
    'salesforce.com': 'Salesforce',
    'hubspot.com': 'HubSpot',
    'paypal.com': 'Payment Processing',
    'stripe.com': 'Payment Processing',
    'square.com': 'Payment Processing',
    'aws.amazon.com': 'AWS Services',
    'microsoftonline.com': 'Microsoft Azure',
    'googleapis.com': 'Google Cloud',
    'digitalocean.com': 'DigitalOcean',
    'heroku.com': 'Heroku',
    'vercel.com': 'Vercel',
    'cloudflare.com': 'CloudFlare',
    'datadog.com': 'Datadog Monitoring',
    'newrelic.com': 'New Relic',
    'splunk.com': 'Splunk',
    'segment.com': 'Segment Analytics',
}

# Business transaction patterns
BUSINESS_PATTERNS = {
    'payment': [
        'invoice',
        'bill',
        'payment',
        'transaction',
        'charge',
        'receipt',
        'purchase'
    ],
    'revenue': [
        'payment received',
        'deposit',
        'credit',
        'income',
        'revenue',
        'sale',
        'reimbursement'
    ],
    'expense': [
        'expense',
        'cost',
        'purchase',
        'bill',
        'payment',
        'subscription',
        'service fee'
    ]
}

class BusinessAuditor:
    """
    Advanced business auditor that analyzes transactions and generates insights
    """

    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.subscription_usage = {}

    def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single transaction and categorize it
        """
        description = transaction.get('description', '').lower()

        # Check for subscription patterns
        for pattern, name in SUBSCRIPTION_PATTERNS.items():
            if pattern in description:
                subscription_info = {
                    'type': 'subscription',
                    'name': name,
                    'amount': transaction.get('amount'),
                    'date': transaction.get('date'),
                    'description': transaction.get('description'),
                    'merchant': transaction.get('merchant', 'Unknown')
                }

                # Track usage for audit purposes
                if name not in self.subscription_usage:
                    self.subscription_usage[name] = []
                self.subscription_usage[name].append(transaction.get('date'))

                return subscription_info

        # Check for business patterns
        for category, keywords in BUSINESS_PATTERNS.items():
            for keyword in keywords:
                if keyword in description:
                    return {
                        'type': category,
                        'category': keyword,
                        'amount': transaction.get('amount'),
                        'date': transaction.get('date'),
                        'description': transaction.get('description'),
                        'merchant': transaction.get('merchant', 'Unknown')
                    }

        # Default to general transaction
        return {
            'type': 'general',
            'amount': transaction.get('amount'),
            'date': transaction.get('date'),
            'description': transaction.get('description'),
            'merchant': transaction.get('merchant', 'Unknown')
        }

    def identify_subscription_issues(self) -> List[Dict[str, Any]]:
        """
        Identify problematic subscriptions based on usage patterns and costs
        """
        issues = []

        for name, usage_dates in self.subscription_usage.items():
            # Check for no usage in 30 days
            if usage_dates:
                latest_usage = datetime.fromisoformat(usage_dates[-1].replace('Z', '+00:00'))
                days_since_usage = (datetime.now(latest_usage.tzinfo) - latest_usage).days

                if days_since_usage > 30:
                    issues.append({
                        'issue_type': 'inactive_subscription',
                        'name': name,
                        'days_since_last_use': days_since_usage,
                        'recommendation': 'Consider cancelling unused subscription'
                    })

        return issues

    def generate_weekly_summary(self, transactions: List[Dict[str, Any]], period_start: str, period_end: str) -> Dict[str, Any]:
        """
        Generate a comprehensive weekly summary for CEO Briefing
        """
        summary = {
            'period': {
                'start': period_start,
                'end': period_end
            },
            'revenue': {
                'total': 0,
                'breakdown': {},
                'trend': 'neutral'
            },
            'expenses': {
                'total': 0,
                'subscriptions': 0,
                'business': 0,
                'other': 0
            },
            'tasks': {
                'completed': 0,
                'pending': 0,
                'overdue': 0
            },
            'insights': {
                'bottlenecks': [],
                'opportunities': [],
                'risks': []
            },
            'recommendations': []
        }

        # Categorize transactions
        for transaction in transactions:
            analysis = self.analyze_transaction(transaction)

            if analysis['type'] == 'revenue':
                summary['revenue']['total'] += float(analysis['amount'])

                # Add to breakdown by merchant
                merchant = analysis['merchant']
                if merchant not in summary['revenue']['breakdown']:
                    summary['revenue']['breakdown'][merchant] = 0
                summary['revenue']['breakdown'][merchant] += float(analysis['amount'])

            elif analysis['type'] == 'subscription':
                summary['expenses']['subscriptions'] += float(analysis['amount'])
                summary['expenses']['total'] += float(analysis['amount'])

            elif analysis['type'] == 'expense':
                summary['expenses']['business'] += float(analysis['amount'])
                summary['expenses']['total'] += float(analysis['amount'])
            else:
                summary['expenses']['other'] += float(analysis['amount'])
                summary['expenses']['total'] += float(analysis['amount'])

        # Generate trend analysis
        if summary['revenue']['total'] > 0:
            summary['revenue']['trend'] = 'positive' if summary['revenue']['total'] > 0 else 'negative'

        # Add subscription audit issues
        subscription_issues = self.identify_subscription_issues()
        for issue in subscription_issues:
            summary['insights']['risks'].append(issue)
            summary['recommendations'].append({
                'type': 'cost_reduction',
                'description': f'{issue["name"]}: {issue["recommendation"]}',
                'estimated_savings': 'TBD'
            })

        # Generate other insights based on business goals
        revenue_goal = 10000  # Monthly goal
        if summary['revenue']['total'] < (revenue_goal / 4):  # Less than weekly target
            summary['insights']['bottlenecks'].append({
                'type': 'revenue_shortfall',
                'description': f'Weekly revenue ${summary["revenue"]["total"]:.2f} below target',
                'severity': 'medium'
            })

        return summary

    def generate_ceo_briefing(self, weekly_summary: Dict[str, Any]) -> str:
        """
        Generate the Monday Morning CEO Briefing based on weekly summary
        """
        briefing = f"""---
generated: {datetime.now().isoformat()}
period: {weekly_summary['period']['start']} to {weekly_summary['period']['end']}
---
# Monday Morning CEO Briefing

## Executive Summary
{self._generate_executive_summary(weekly_summary)}

## Revenue
- **This Week**: ${weekly_summary['revenue']['total']:.2f}
- **MTD**: TBD (proportional based on week)
- **Trend**: {weekly_summary['revenue']['trend'].title()}

## Expenses
- **Total Expenses**: ${weekly_summary['expenses']['total']:.2f}
- **Subscriptions**: ${weekly_summary['expenses']['subscriptions']:.2f}
- **Business**: ${weekly_summary['expenses']['business']:.2f}
- **Other**: ${weekly_summary['expenses']['other']:.2f}

## Revenue Breakdown
"""

        for merchant, amount in weekly_summary['revenue']['breakdown'].items():
            briefing += f"- {merchant}: ${amount:.2f}\n"

        # Add insights section
        briefing += "\n## Bottlenecks\n"
        for bottleneck in weekly_summary['insights']['bottlenecks']:
            briefing += f"- {bottleneck['description']}\n"

        # Add proactive suggestions
        briefing += "\n## Proactive Suggestions\n"

        if weekly_summary['insights']['risks']:
            briefing += "\n### Cost Optimization\n"
            for risk in weekly_summary['insights']['risks']:
                briefing += f"- **{risk['name']}**: {risk['recommendation']}\n"

        if weekly_summary['recommendations']:
            briefing += "\n### Recommendations\n"
            for rec in weekly_summary['recommendations']:
                if rec['type'] == 'cost_reduction':
                    briefing += f"- {rec['description']}\n"

        # Add upcoming deadlines if any
        briefing += "\n## Upcoming Deadlines\n- Check Business_Goals.md for project deadlines\n"

        briefing += "\n---\n*Generated by AI Employee v1.0*"

        return briefing

    def _generate_executive_summary(self, summary: Dict[str, Any]) -> str:
        """
        Generate a brief executive summary based on the data
        """
        if summary['revenue']['total'] > 0 and summary['revenue']['trend'] == 'positive':
            return "Strong week with revenue growth. Subscription audit identified cost reduction opportunities."
        elif summary['revenue']['total'] > 0:
            return "Steady week with consistent revenue. Subscription audit identified areas for optimization."
        else:
            return "Revenue needs attention. Multiple subscription optimization opportunities identified."


# Example usage:
if __name__ == "__main__":
    # Example transaction data
    sample_transactions = [
        {
            'description': 'Adobe Creative Cloud subscription',
            'amount': 52.99,
            'date': '2026-02-22T10:30:00Z',
            'merchant': 'Adobe'
        },
        {
            'description': 'Payment received from Client A for project work',
            'amount': 2500.00,
            'date': '2026-02-23T14:15:00Z',
            'merchant': 'Client A'
        },
        {
            'description': 'Notion productivity tool subscription',
            'amount': 8.00,
            'date': '2026-02-20T09:00:00Z',
            'merchant': 'Notion'
        }
    ]

    auditor = BusinessAuditor('.')
    summary = auditor.generate_weekly_summary(
        sample_transactions,
        '2026-02-22',
        '2026-02-28'
    )

    briefing = auditor.generate_ceo_briefing(summary)
    print(briefing)