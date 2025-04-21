# GitHub Contributions Sync

This script synchronizes the GitHub contribution graph from a **work account** to your **personal account** by creating empty commits via the GitHub API. It parses the contribution calendars of both users, calculates the difference in daily contributions, and creates matching commits on a personal repository to reflect your actual work.

## Features

- Scrapes GitHub contribution calendars (public user pages)
- Detects daily contribution differences for a full calendar year
- Creates empty commits (with accurate timestamps) to match contributions
- Uses the GitHub API (no local Git required)
- Loads configuration from a `.env` file for convenience
- Only requires `--year` as a command-line argument (optional)

---

## Requirements

- Python 3.9+
- GitHub personal access token (for your **personal account**)
- A personal repository to push commits into (no file changes needed)

---

## Installation

### 1. **Clone this repository:**
```bash
   git clone https://github.com/minormending/contribution-sync.git
   cd contribution-sync
```

### 2. Install dependencies using Poetry:
```bash
poetry install
```

### 3. Create a `.env` file:
```env
WORK_USERNAME=workaccount
CURRENT_USERNAME=yourusername
GITHUB_TOKEN=ghp_your_token_here
DESTINATION_REPO=yourusername/your-repo
DESTINATION_BRANCH=main
AUTHOR_NAME=Your Name
AUTHOR_EMAIL=yourname@users.noreply.github.com
```
Alternatively, use the provided `.env.example` as a starting point.

## Generating a GitHub Token
To allow the script to create commits on your behalf via the GitHub API, you need to generate a Personal Access Token (PAT) for your personal GitHub account:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" (classic) or "Fine-grained token".
3. Name the token (e.g., `contribution-sync`).
4. Set an expiration date (or "No expiration" if you prefer to manage it manually).
5. Under "Repository Access", choose "Only select repositories" and select the commit repository.
5. Under "Permissions", check the following:
    - `Contents: Read and Write` → Full control of the contents of the selected repository.
6. Click Generate Token.
7. Copy the token and save it somewhere safe (you won’t be able to view it again).
8. Add it to your `.env` file:
```env
GITHUB_TOKEN=ghp_your_generated_token_here
```
Important: Never share your GitHub token or commit it to version control.

## Usage
Run the script with an optional `--year` argument:
```bash
poetry run python sync.py --year 2023
```
If `--year` is not provided, it will default to the current year.

The script will:
1. Fetch contribution data for both the work and current accounts.
2. Calculate which days require additional commits.
3. Create one or more empty commits per day to match the contribution count from the work account.

## Integration with GitHub Actions
You can run this script automatically every day using GitHub Actions.

See `.github/workflows/sync.yml` for a working example.

Ensure you set the appropriate secrets (WORK_GITHUB_TOKEN, WORK_REPO, and optionally PERSONAL_BRANCH) in your repository settings.

## Troubleshooting
- Ensure your GitHub token has appropriate scopes (see above).
- Verify the contribution pages exist for both accounts:
    - `https://github.com/users/<USERNAME>/contributions?from=YYYY-01-01&to=YYYY-12-31`
- Check for typos in your `.env` file or environment variables.
- Confirm that the destination repo and branch exist and are accessible.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any bug fixes or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer
This script is intended for personal use to unify or reflect actual development work across multiple accounts. Use responsibly and ethically in accordance with GitHub’s Terms of Service.