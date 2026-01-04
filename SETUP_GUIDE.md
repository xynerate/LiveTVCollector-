# LiveTVCollector Italy - Setup Guide

## Overview

This setup automatically collects Italian IPTV channels from multiple sources, verifies active links, and generates M3U playlists via GitHub Actions.

## Prerequisites

- A GitHub account
- A forked or cloned LiveTVCollector repository

## Setup Steps

### 1. Fork/Clone the Repository

If you haven't already, fork the [LiveTVCollector](https://github.com/bugsfreeweb/LiveTVCollector) repository to your GitHub account.

Or clone it locally:
```bash
git clone https://github.com/bugsfreeweb/LiveTVCollector.git
cd LiveTVCollector
```

### 2. Verify Files Are Present

Ensure these files exist:
- `BugsfreeMain/Italy.py` - The collection script
- `.github/workflows/italy.yml` - GitHub Actions workflow
- `LiveTV/Italy/` - Output directory

### 3. Push to GitHub

If you cloned locally, add your fork as remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/LiveTVCollector.git
git add .
git commit -m "Add Italy LiveTV collector"
git push -u origin main
```

### 4. Enable GitHub Actions

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **General**
3. Ensure "Allow all actions and reusable workflows" is enabled
4. Go to **Actions** tab to see the workflow

### 5. Trigger the Workflow

The workflow runs automatically every 8 hours, but you can trigger it manually:

1. Go to **Actions** tab in your repository
2. Click on "Italy LiveTV Files" workflow
3. Click "Run workflow" button
4. Select the branch (usually `main`)
5. Click "Run workflow"

### 6. Wait for Completion

The workflow will:
- Fetch M3U sources
- Parse channels
- Remove duplicates
- Verify active links (50 concurrent workers)
- Generate output files
- Commit and push results

Check the Actions tab to see progress and logs.

### 7. Verify Generated Files

After the workflow completes, check that files exist at:
- `LiveTV/Italy/LiveTV.m3u`
- `LiveTV/Italy/LiveTV.json`
- `LiveTV/Italy/LiveTV.txt`
- `LiveTV/Italy/LiveTV`

## Using in PVR App

### Add Source URL

1. Open your PVR application
2. Go to **Manage Sources**
3. Add the following URL (replace `YOUR_USERNAME` with your GitHub username):

```
https://raw.githubusercontent.com/YOUR_USERNAME/LiveTVCollector/main/LiveTV/Italy/LiveTV.m3u
```

### Benefits

- **No CORS Issues**: GitHub raw URLs work directly in browsers
- **Auto-Updates**: Refreshes every 8 hours automatically
- **Pre-Verified**: Only active links are included
- **Deduplicated**: No duplicate channels
- **Multiple Formats**: M3U, JSON, and TXT formats available

### Example URLs

If your GitHub username is `johndoe`, your URL would be:
```
https://raw.githubusercontent.com/johndoe/LiveTVCollector/main/LiveTV/Italy/LiveTV.m3u
```

## Troubleshooting

### Workflow Not Running

- Check that GitHub Actions is enabled in repository settings
- Verify the workflow file is in `.github/workflows/italy.yml`
- Check for syntax errors in the YAML file

### No Channels Generated

- Check the Actions logs for errors
- Verify M3U source URLs are accessible
- Some sources may be temporarily unavailable

### CORS Errors in PVR App

- GitHub raw URLs should work without CORS proxy
- If issues persist, try clearing the CORS proxy field in PVR app settings
- Verify the URL is correct and the file exists

### Empty M3U File

- Check that source URLs are still valid
- Some links may have timed out during verification
- Review the workflow logs for specific errors

## Customization

### Add More Sources

Edit `BugsfreeMain/Italy.py` and add URLs to the `fetch_m3u_sources()` function:

```python
def fetch_m3u_sources():
    source_urls = [
        "https://raw.githubusercontent.com/Free-IPTV/Countries/master/Italy/italy.m3u",
        "https://iptv-org.github.io/iptv/languages/ita.m3u",
        "https://raw.githubusercontent.com/freearhey/iptv/master/playlists/it.m3u",
        "YOUR_NEW_SOURCE_URL_HERE",  # Add more sources
    ]
    return source_urls
```

### Change Update Frequency

Edit `.github/workflows/italy.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '0 */8 * * *'  # Every 8 hours
  # Change to '0 */4 * * *' for every 4 hours
  # Or '0 0 * * *' for daily at midnight UTC
```

### Adjust Link Verification

In `BugsfreeMain/Italy.py`, modify the `check_link_active()` function timeout or the ThreadPoolExecutor max_workers value.

## Support

For issues or questions:
- Check the GitHub Actions logs
- Review the script output in workflow logs
- Verify source URLs are accessible
- Check repository permissions and settings
