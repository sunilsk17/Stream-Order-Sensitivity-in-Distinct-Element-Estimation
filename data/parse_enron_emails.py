#!/usr/bin/env python3
"""
Enron Email Dataset Parser for Order Sensitivity Testing
=========================================================

Extracts sender email addresses from Enron maildir corpus in chronological order.
This creates a stream with natural duplicates and burst patterns perfect for
validating order sensitivity in cardinality sketchers.

Key characteristics extracted:
- Sender email addresses (From field)
- Timestamps (Date field)
- Chronological ordering
- Natural duplicates and bursts
"""

import os
import re
import json
import gzip
from datetime import datetime
from collections import defaultdict
from email.utils import parsedate_to_datetime
import sys

# Configuration
MAILDIR_PATH = "/Users/sunilkumars/Desktop/distinct-order-study/maildir"
OUTPUT_FILE = "/Users/sunilkumars/Desktop/distinct-order-study/data/enron_email_stream.json.gz"
STATS_FILE = "/Users/sunilkumars/Desktop/distinct-order-study/data/enron_email_stream_stats.json"
EXECUTION_LOG = "/Users/sunilkumars/Desktop/distinct-order-study/results/ENRON_PARSER_LOG.txt"

def log_message(message):
    """Log to both stdout and file"""
    print(message)
    with open(EXECUTION_LOG, 'a') as f:
        f.write(message + '\n')

def extract_email_from_line(line):
    """Extract email address from From/To/Cc line"""
    if ':' not in line:
        return None
    
    header_value = line.split(':', 1)[1].strip()
    
    # Match email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+'
    matches = re.findall(email_pattern, header_value)
    
    return matches if matches else None

def extract_date_from_line(line):
    """Extract date from Date header"""
    if not line.startswith('Date:'):
        return None
    
    date_str = line[5:].strip()
    try:
        dt = parsedate_to_datetime(date_str)
        return dt
    except:
        return None

def parse_email_file(filepath):
    """Parse single email file and extract From/Date"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sender = None
            timestamp = None
            
            for line in f:
                line = line.rstrip('\n')
                
                if line.startswith('From:'):
                    emails = extract_email_from_line(line)
                    if emails:
                        sender = emails[0]  # Take first email
                elif line.startswith('Date:'):
                    timestamp = extract_date_from_line(line)
                
                # Stop after headers (blank line marks end of headers)
                if line == '' and (sender or timestamp):
                    break
            
            return {
                'sender': sender,
                'timestamp': timestamp,
                'filepath': filepath
            }
    except Exception as e:
        return None

def process_maildir():
    """Process all emails in maildir"""
    log_message("🔄 Starting Enron Email Parser...")
    log_message(f"   Maildir path: {MAILDIR_PATH}\n")
    
    emails_data = []
    email_count = 0
    user_count = 0
    parse_errors = 0
    
    # Iterate through each user directory
    for username in os.listdir(MAILDIR_PATH):
        user_path = os.path.join(MAILDIR_PATH, username)
        
        if not os.path.isdir(user_path):
            continue
        
        user_count += 1
        user_emails = 0
        
        # Find all email files recursively
        for root, dirs, files in os.walk(user_path):
            for filename in files:
                # Email files are just numbers or numbers with dots
                if filename.isdigit() or (filename[0].isdigit() and '.' in filename):
                    filepath = os.path.join(root, filename)
                    
                    email_data = parse_email_file(filepath)
                    if email_data and email_data['sender'] and email_data['timestamp']:
                        emails_data.append(email_data)
                        email_count += 1
                        user_emails += 1
                    elif email_data is None:
                        parse_errors += 1
        
        if user_count % 20 == 0:
            log_message(f"   Processed {user_count} users, {email_count} emails extracted...")
    
    log_message(f"\n✓ Parsing complete:")
    log_message(f"   Total users scanned: {user_count}")
    log_message(f"   Total emails parsed: {email_count}")
    log_message(f"   Parse errors: {parse_errors}")
    
    return emails_data

def sort_and_generate_stream(emails_data):
    """Sort emails by timestamp and generate stream"""
    log_message(f"\n🔄 Sorting {len(emails_data)} emails by timestamp...")
    
    # Sort by timestamp
    emails_data.sort(key=lambda x: x['timestamp'])
    
    log_message(f"✓ Sorted successfully")
    
    return emails_data

def analyze_statistics(sorted_emails):
    """Analyze stream statistics"""
    log_message(f"\n📊 Analyzing stream statistics...")
    
    senders = [e['sender'] for e in sorted_emails]
    unique_senders = set(senders)
    sender_counts = defaultdict(int)
    
    for sender in senders:
        sender_counts[sender] += 1
    
    # Calculate burst patterns
    burst_count = 0
    burst_lengths = []
    current_burst_sender = None
    current_burst_length = 0
    
    for sender in senders:
        if sender == current_burst_sender:
            current_burst_length += 1
        else:
            if current_burst_length > 1:
                burst_count += 1
                burst_lengths.append(current_burst_length)
            current_burst_sender = sender
            current_burst_length = 1
    
    # Finalize last burst
    if current_burst_length > 1:
        burst_count += 1
        burst_lengths.append(current_burst_length)
    
    # Calculate Zipfian-like distribution
    sorted_counts = sorted(sender_counts.values(), reverse=True)
    
    stats = {
        'total_emails': len(sorted_emails),
        'unique_senders': len(unique_senders),
        'unique_ratio': len(unique_senders) / len(sorted_emails),
        'duplicate_ratio': 1.0 - (len(unique_senders) / len(sorted_emails)),
        'total_duplicates': len(sorted_emails) - len(unique_senders),
        'burst_patterns': {
            'total_bursts': burst_count,
            'avg_burst_length': sum(burst_lengths) / len(burst_lengths) if burst_lengths else 0,
            'max_burst_length': max(burst_lengths) if burst_lengths else 0,
            'min_burst_length': min(burst_lengths) if burst_lengths else 0
        },
        'top_10_senders': [
            {'email': sender, 'count': sender_counts[sender]}
            for sender, count in sorted([(s, sender_counts[s]) for s in unique_senders],
                                       key=lambda x: x[1], reverse=True)[:10]
        ],
        'timestamp_range': {
            'earliest': sorted_emails[0]['timestamp'].isoformat(),
            'latest': sorted_emails[-1]['timestamp'].isoformat()
        },
        'characteristics': {
            'has_duplicates': True,
            'has_bursts': burst_count > 0,
            'realistic': True,
            'sorted_chronologically': True
        }
    }
    
    log_message(f"   Total emails: {stats['total_emails']:,}")
    log_message(f"   Unique senders: {stats['unique_senders']:,}")
    log_message(f"   Unique ratio: {stats['unique_ratio']:.2%}")
    log_message(f"   Duplicate ratio: {stats['duplicate_ratio']:.2%}")
    log_message(f"   Total duplicates: {stats['total_duplicates']:,}")
    log_message(f"\n   Burst patterns:")
    log_message(f"      Total bursts: {stats['burst_patterns']['total_bursts']}")
    log_message(f"      Avg burst length: {stats['burst_patterns']['avg_burst_length']:.2f}")
    log_message(f"      Max burst length: {stats['burst_patterns']['max_burst_length']}")
    log_message(f"\n   Top 10 senders:")
    for i, sender_info in enumerate(stats['top_10_senders'], 1):
        log_message(f"      {i}. {sender_info['email']}: {sender_info['count']} emails")
    
    log_message(f"\n   Time range: {stats['timestamp_range']['earliest']} to {stats['timestamp_range']['latest']}")
    
    return stats

def write_stream_to_file(sorted_emails, output_file):
    """Write email stream to compressed JSON"""
    log_message(f"\n💾 Writing stream to {output_file}...")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        for email in sorted_emails:
            record = {
                'sender': email['sender'],
                'timestamp': email['timestamp'].isoformat(),
                'source': 'enron_email_corpus'
            }
            f.write(json.dumps(record) + '\n')
    
    log_message(f"✓ Stream written successfully")
    log_message(f"   File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")

def write_stats(stats, stats_file):
    """Write statistics to JSON"""
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    log_message(f"\n✓ Statistics saved to {stats_file}")

def main():
    # Initialize log file
    os.makedirs(os.path.dirname(EXECUTION_LOG), exist_ok=True)
    with open(EXECUTION_LOG, 'w') as f:
        f.write(f"Enron Email Parser Execution Log\n")
        f.write(f"Started: {datetime.now().isoformat()}\n")
        f.write("="*60 + "\n\n")
    
    try:
        # Parse all emails
        emails_data = process_maildir()
        
        if not emails_data:
            log_message("❌ No emails found!")
            return False
        
        # Sort by timestamp
        sorted_emails = sort_and_generate_stream(emails_data)
        
        # Analyze statistics
        stats = analyze_statistics(sorted_emails)
        
        # Write outputs
        write_stream_to_file(sorted_emails, OUTPUT_FILE)
        write_stats(stats, STATS_FILE)
        
        log_message(f"\n✅ ENRON PARSING COMPLETE!")
        log_message(f"\n📁 Output files:")
        log_message(f"   Stream: {OUTPUT_FILE}")
        log_message(f"   Stats: {STATS_FILE}")
        log_message(f"   Log: {EXECUTION_LOG}")
        
        return True
        
    except Exception as e:
        log_message(f"\n❌ ERROR: {str(e)}")
        import traceback
        log_message(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
