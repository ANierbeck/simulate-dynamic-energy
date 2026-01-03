# GitHub Container Registry (GHCR) Setup Guide

This guide explains how to set up the Docker image build and push workflow to GitHub Container Registry.

## Prerequisites

1. A GitHub account with access to this repository
2. GitHub CLI installed (optional, but helpful)

## Setup Instructions

### Step 1: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name like "GHCR Push Token"
4. Select the following scopes:
   - `write:packages` (required for pushing to GHCR)
   - `read:packages` (optional, for reading packages)
   - `delete:packages` (optional, for deleting packages)
5. Click "Generate token" and copy the token value

### Step 2: Add Secrets to GitHub Repository

1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add the following secrets:
   - **Name**: `GHCR_USERNAME`
     **Value**: Your GitHub username
   - **Name**: `GHCR_TOKEN`
     **Value**: The personal access token you created in Step 1

### Step 3: Verify the Workflow

The workflow is configured to:
- Trigger automatically on pushes to the `main` branch
- Be manually triggerable via the GitHub Actions UI
- Build Docker images using the existing Dockerfile
- Push images to GHCR with two tags:
  - `latest` - for the most recent build
  - `{commit-sha}` - for traceability (e.g., `ghcr.io/your-repo/your-image:abc1234`)

### Step 4: Test the Workflow

1. Push a small change to the main branch, or
2. Go to Actions tab → Select "Docker Build and Push to GHCR" → Click "Run workflow"

### Step 5: Using the Docker Images

Once the workflow completes successfully, you can pull the images using:

```bash
# Pull the latest image
docker pull ghcr.io/your-username/your-repository:latest

# Pull a specific version by commit SHA
docker pull ghcr.io/your-username/your-repository:abc1234
```

## Troubleshooting

### Authentication Issues
- Ensure your personal access token has the correct scopes
- Verify the secrets are correctly named and contain the right values
- Check that your GitHub username is correct

### Build Failures
- Ensure your Dockerfile is syntactically correct
- Check that all required files are present in the repository
- Verify that the build context is correct

### Permission Issues
- Make sure your GitHub account has write access to the repository
- Check that the repository settings allow Actions to run

## Security Notes

- Never commit secrets directly to the repository
- Rotate your personal access token regularly
- Use the principle of least privilege when setting token scopes
- Consider using repository variables for non-sensitive configuration