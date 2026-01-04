#!/usr/bin/env python3
"""
Italy LiveTV Collector
Automatically collects, filters, and exports Italian IPTV channels
"""

import requests
import re
import json
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def fetch_m3u_sources():
    """Italian M3U sources"""
    source_urls = [
        "https://raw.githubusercontent.com/Free-IPTV/Countries/master/Italy/italy.m3u",
        "https://iptv-org.github.io/iptv/languages/ita.m3u",
        "https://raw.githubusercontent.com/freearhey/iptv/master/playlists/it.m3u",
    ]
    return source_urls


def parse_m3u(content, source_url=""):
    """Parse M3U content and extract channels"""
    channels = []
    lines = content.split('\n')
    current_channel = {}
    epg_url = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Parse #EXTM3U header for EPG URL
        if line.startswith('#EXTM3U'):
            epg_match = re.search(r'url-tvg="([^"]*)"', line, re.IGNORECASE)
            if not epg_match:
                epg_match = re.search(r'x-tvg-url="([^"]*)"', line, re.IGNORECASE)
            if not epg_match:
                epg_match = re.search(r'tvg-url="([^"]*)"', line, re.IGNORECASE)
            if epg_match:
                epg_url = epg_match.group(1)
            continue
        
        # Parse EXTINF line
        if line.startswith('#EXTINF:'):
            current_channel = {}
            
            # Extract tvg-id
            tvg_id_match = re.search(r'tvg-id="([^"]*)"', line, re.IGNORECASE)
            if tvg_id_match:
                current_channel['tvg_id'] = tvg_id_match.group(1)
            
            # Extract tvg-name
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', line, re.IGNORECASE)
            if tvg_name_match:
                current_channel['name'] = tvg_name_match.group(1)
            
            # Extract tvg-logo
            tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line, re.IGNORECASE)
            if tvg_logo_match:
                current_channel['logo'] = tvg_logo_match.group(1)
            else:
                current_channel['logo'] = ""
            
            # Extract group-title
            group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            if group_match:
                current_channel['group'] = group_match.group(1)
            else:
                current_channel['group'] = "General"
            
            # Extract display name (after the comma)
            comma_index = line.rfind(',')
            if comma_index != -1:
                display_name = line[comma_index + 1:].strip()
                if display_name and not current_channel.get('name'):
                    current_channel['name'] = display_name
                elif not current_channel.get('name'):
                    current_channel['name'] = "Unknown Channel"
            elif not current_channel.get('name'):
                current_channel['name'] = "Unknown Channel"
            
            continue
        
        # Skip other directives
        if line.startswith('#'):
            continue
        
        # This should be a URL - associate with previous EXTINF
        if line and current_channel and (line.startswith('http://') or line.startswith('https://')):
            current_channel['url'] = line
            current_channel['source'] = source_url
            current_channel['epg_url'] = epg_url
            channels.append(current_channel)
            current_channel = {}
    
    return channels


def check_link_active(url, timeout=5):
    """Check if stream link is active"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True, stream=True)
        # Accept 200-399 as valid status codes
        return response.status_code in range(200, 400)
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        # Try GET if HEAD fails
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
            return response.status_code in range(200, 400)
        except:
            return False


def fetch_source(url):
    """Fetch and parse a single M3U source"""
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, stream=True, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        content = response.text
        channels = parse_m3u(content, url)
        print(f"  Parsed {len(channels)} channels from {url}")
        return channels
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []


def export_to_m3u(channels, output_dir):
    """Export to M3U format"""
    output_path = os.path.join(output_dir, 'LiveTV.m3u')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in channels:
            # Build EXTINF line with all attributes
            extinf = '#EXTINF:-1'
            if ch.get('tvg_id'):
                extinf += f' tvg-id="{ch["tvg_id"]}"'
            if ch.get('name'):
                extinf += f' tvg-name="{ch["name"]}"'
            if ch.get('logo'):
                extinf += f' tvg-logo="{ch["logo"]}"'
            if ch.get('group'):
                extinf += f' group-title="{ch["group"]}"'
            extinf += f',{ch.get("name", "Unknown")}\n'
            f.write(extinf)
            f.write(f'{ch["url"]}\n')
    print(f"Exported {len(channels)} channels to {output_path}")


def export_to_json(channels, output_dir):
    """Export to JSON format"""
    mumbai_tz = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(mumbai_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        'date': timestamp,
        'channels': {}
    }
    
    for ch in channels:
        group = ch.get('group', 'General')
        if group not in data['channels']:
            data['channels'][group] = []
        data['channels'][group].append({
            'name': ch.get('name', 'Unknown'),
            'logo': ch.get('logo', ''),
            'group': group,
            'source': ch.get('source', ''),
            'url': ch['url'],
            'tvg_id': ch.get('tvg_id', '')
        })
    
    output_path = os.path.join(output_dir, 'LiveTV.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported JSON to {output_path}")


def export_to_txt(channels, output_dir):
    """Export to text format"""
    output_path = os.path.join(output_dir, 'LiveTV.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        for ch in channels:
            f.write(f"Group: {ch.get('group', 'General')}\n")
            f.write(f"Name: {ch.get('name', 'Unknown')}\n")
            f.write(f"URL: {ch['url']}\n")
            f.write(f"Logo: {ch.get('logo', '')}\n")
            f.write(f"Source: {ch.get('source', '')}\n")
            if ch.get('tvg_id'):
                f.write(f"TVG ID: {ch['tvg_id']}\n")
            f.write('-' * 50 + '\n\n')
    print(f"Exported text format to {output_path}")


def export_to_custom_json(channels, output_dir):
    """Export to custom JSON format (without extension)"""
    custom_data = []
    for ch in channels:
        custom_data.append({
            'name': ch.get('name', 'Unknown'),
            'type': ch.get('group', 'General'),
            'url': ch['url'],
            'img': ch.get('logo', '')
        })
    
    output_path = os.path.join(output_dir, 'LiveTV')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(custom_data, f, indent=2, ensure_ascii=False)
    print(f"Exported custom JSON to {output_path}")


def main():
    """Main function to collect and process Italian channels"""
    print("=" * 60)
    print("Italy LiveTV Collector")
    print("=" * 60)
    
    # Get output directory
    output_dir = os.path.join('LiveTV', 'Italy')
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch all sources
    source_urls = fetch_m3u_sources()
    print(f"\nFetching from {len(source_urls)} sources...\n")
    
    all_channels = []
    for url in source_urls:
        channels = fetch_source(url)
        all_channels.extend(channels)
    
    print(f"\nTotal channels collected: {len(all_channels)}")
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_channels = []
    for ch in all_channels:
        url = ch['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_channels.append(ch)
    
    print(f"Unique channels after deduplication: {len(unique_channels)}")
    
    # Check active links with concurrency
    print(f"\nVerifying active links (using 50 concurrent workers)...")
    active_channels = []
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_channel = {
            executor.submit(check_link_active, ch['url']): ch 
            for ch in unique_channels
        }
        
        completed = 0
        for future in as_completed(future_to_channel):
            ch = future_to_channel[future]
            try:
                is_active = future.result()
                if is_active:
                    active_channels.append(ch)
                completed += 1
                if completed % 50 == 0:
                    print(f"  Checked {completed}/{len(unique_channels)} links...")
            except Exception as e:
                print(f"  Error checking {ch['url']}: {e}")
    
    print(f"\nActive channels: {len(active_channels)}")
    
    # Export to all formats
    print("\nExporting files...")
    export_to_m3u(active_channels, output_dir)
    export_to_json(active_channels, output_dir)
    export_to_txt(active_channels, output_dir)
    export_to_custom_json(active_channels, output_dir)
    
    print("\n" + "=" * 60)
    print("Collection complete!")
    print(f"Exported {len(active_channels)} active Italian channels")
    print("=" * 60)


if __name__ == '__main__':
    main()
