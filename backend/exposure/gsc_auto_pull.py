"""
Auto-pull GSC data when requested by frontend
"""
from datetime import date, timedelta
from typing import List, Tuple
from django.conf import settings
from .models import Keyword, ExposureSnapshot
from .gsc_client import fetch_daily_impressions


def check_data_coverage(start: date, end: date, keywords: List[str]) -> Tuple[bool, List[date]]:
    """
    Check if we have complete data for all keywords in the date range.
    Returns: (has_complete_data, list_of_missing_dates)
    """
    # Generate all dates in range
    all_dates = []
    current = start
    while current <= end:
        all_dates.append(current)
        current += timedelta(days=1)

    # Check which dates have data for all keywords
    missing_dates = []
    for check_date in all_dates:
        count = ExposureSnapshot.objects.filter(
            date=check_date,
            keyword__name__in=keywords
        ).count()

        # If we don't have data for all keywords on this date, it's missing
        if count < len(keywords):
            missing_dates.append(check_date)

    has_complete = len(missing_dates) == 0
    return has_complete, missing_dates


def pull_gsc_data_for_range(start: date, end: date, keywords: List[str] = None) -> dict:
    """
    Pull GSC data for specified date range and keywords.
    If keywords not provided, uses settings.KEYWORD_TRACK_LIST

    Returns: {
        'success': bool,
        'keywords_pulled': int,
        'snapshots_created': int,
        'date_range': str,
        'errors': []
    }
    """
    if keywords is None:
        keywords = settings.KEYWORD_TRACK_LIST

    property_uri = settings.GSC_PROPERTY_URI
    start_str = start.isoformat()
    end_str = end.isoformat()

    result = {
        'success': True,
        'keywords_pulled': 0,
        'snapshots_created': 0,
        'date_range': f'{start_str} to {end_str}',
        'errors': []
    }

    for kw_name in keywords:
        try:
            # Get or create keyword
            kw, _ = Keyword.objects.get_or_create(
                name=kw_name,
                defaults={'enabled': True}
            )

            # Fetch from GSC
            rows = fetch_daily_impressions(property_uri, kw_name, start_str, end_str)

            # Save to database
            for row in rows:
                row_date = date.fromisoformat(row['date'])

                # Only create if within requested range
                if start <= row_date <= end:
                    snapshot, created = ExposureSnapshot.objects.update_or_create(
                        date=row_date,
                        keyword=kw,
                        defaults={
                            'impressions': row['impressions'],
                            'clicks': row.get('clicks', 0),
                            'position': row.get('position', 0.0)
                        }
                    )
                    if created:
                        result['snapshots_created'] += 1

            result['keywords_pulled'] += 1

        except Exception as e:
            result['errors'].append(f"Error pulling '{kw_name}': {str(e)}")
            result['success'] = False

    return result


def auto_pull_if_needed(start: date, end: date, keywords: List[str] = None) -> dict:
    """
    Check if data exists, and pull from GSC if missing.

    Returns: {
        'had_data': bool,
        'pulled': bool,
        'pull_result': dict or None
    }
    """
    if keywords is None:
        keywords = settings.KEYWORD_TRACK_LIST

    # Ensure keywords exist in DB
    for kw_name in keywords:
        Keyword.objects.get_or_create(name=kw_name, defaults={'enabled': True})

    # Check coverage
    has_data, missing_dates = check_data_coverage(start, end, keywords)

    result = {
        'had_data': has_data,
        'pulled': False,
        'pull_result': None,
        'missing_dates_count': len(missing_dates)
    }

    # If data is missing, pull from GSC
    if not has_data:
        pull_result = pull_gsc_data_for_range(start, end, keywords)
        result['pulled'] = True
        result['pull_result'] = pull_result

    return result
