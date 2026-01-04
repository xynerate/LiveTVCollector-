# LiveTVCollector - Italy Configuration

This directory contains the configuration for automatically collecting Italian IPTV channels using GitHub Actions.

## Setup

1. Fork or clone this repository
2. The GitHub Actions workflow will automatically run every 8 hours
3. Generated M3U files will be available at: `LiveTV/Italy/LiveTV.m3u`

## Manual Trigger

You can manually trigger the workflow from the GitHub Actions tab in your repository.

## Generated Files

The workflow generates the following files in `LiveTV/Italy/`:

- `LiveTV.m3u` - Standard M3U playlist format
- `LiveTV.json` - Structured JSON with channel metadata
- `LiveTV.txt` - Human-readable text format
- `LiveTV` - Custom JSON format (without extension)

## Usage in PVR App

Add the following URL as a source in your PVR application:

```
https://raw.githubusercontent.com/YOUR_USERNAME/LiveTVCollector/main/LiveTV/Italy/LiveTV.m3u
```

Replace `YOUR_USERNAME` with your GitHub username.

## Italian M3U Sources

The script collects channels from:
- https://raw.githubusercontent.com/Free-IPTV/Countries/master/Italy/italy.m3u
- https://iptv-org.github.io/iptv/languages/ita.m3u
- https://raw.githubusercontent.com/freearhey/iptv/master/playlists/it.m3u

## Features

- Automatic updates every 8 hours
- Pre-verified active links (50 concurrent workers)
- Deduplicated channels by URL
- Multiple export formats
- No CORS issues (served from GitHub raw URLs)
