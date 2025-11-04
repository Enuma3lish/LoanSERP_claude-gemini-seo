#!/usr/bin/env python
"""
Create test data for LoanSERP Analytics Dashboard
This script populates the database with sample exposure data for testing
"""
import os
import django
import random
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loanserp.base')
django.setup()

from exposure.models import Keyword, ExposureSnapshot

def create_test_data(days=30):
    """Create test data for the last N days"""

    # Sample keywords
    keywords_data = [
        "貸款",
        "房屋貸款",
        "個人信貸",
        "車貸",
        "信用貸款"
    ]

    print(f"Creating test data for {days} days...")
    print(f"Keywords: {', '.join(keywords_data)}")
    print()

    # Create keywords
    keywords = []
    for kw_name in keywords_data:
        kw, created = Keyword.objects.get_or_create(name=kw_name, defaults={'enabled': True})
        keywords.append(kw)
        if created:
            print(f"✓ Created keyword: {kw_name}")
        else:
            print(f"→ Keyword exists: {kw_name}")

    print()
    print("Generating exposure data...")

    # Generate data for the last N days
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    current_date = start_date
    created_count = 0

    while current_date <= end_date:
        for i, kw in enumerate(keywords):
            # Generate realistic-looking data with some variance
            # Each keyword has a different base level
            base_impressions = 1000 + (i * 500)

            # Add daily variation (±30%)
            daily_variance = random.uniform(0.7, 1.3)

            # Add weekly pattern (weekends lower)
            if current_date.weekday() >= 5:  # Saturday or Sunday
                weekly_factor = 0.6
            else:
                weekly_factor = 1.0

            # Add trend (slight growth over time)
            days_from_start = (current_date - start_date).days
            trend_factor = 1.0 + (days_from_start * 0.01)  # 1% growth per day

            impressions = int(base_impressions * daily_variance * weekly_factor * trend_factor)
            clicks = int(impressions * random.uniform(0.05, 0.15))  # 5-15% CTR
            position = round(random.uniform(3.0, 15.0), 1)

            # Create or update snapshot
            snapshot, created = ExposureSnapshot.objects.update_or_create(
                date=current_date,
                keyword=kw,
                defaults={
                    'impressions': impressions,
                    'clicks': clicks,
                    'position': position
                }
            )

            if created:
                created_count += 1

        current_date += timedelta(days=1)

    print(f"✓ Created {created_count} exposure snapshots")
    print()
    print("=" * 50)
    print("Test data created successfully!")
    print("=" * 50)
    print()
    print(f"Date range: {start_date} to {end_date}")
    print(f"Keywords: {len(keywords)}")
    print(f"Total snapshots: {ExposureSnapshot.objects.count()}")
    print()
    print("You can now:")
    print("1. Refresh your frontend at http://localhost:4200")
    print("2. Select a date range")
    print("3. Click '分析趨勢' to see the charts!")
    print()

if __name__ == '__main__':
    import sys

    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("Usage: python create_test_data.py [days]")
            print("Example: python create_test_data.py 60")
            sys.exit(1)

    create_test_data(days)
