# GitHub Container Registry (GHCR) Setup Guide

This guide explains how to set up the Docker image build and push workflow to GitHub Container Registry.

## 🎉 Good News! No Manual Setup Required

The workflow now uses the built-in `GITHUB_TOKEN` with proper permissions, so **no manual setup is needed**! 🎉

## How It Works

The workflow automatically:

1. **Uses GitHub's built-in token**: No need to create personal access tokens
2. **Has proper permissions**: The workflow file sets the required permissions
3. **Authenticates securely**: Uses `github.actor` and `GITHUB_TOKEN`
4. **Generates attestations**: Provides supply chain security

## What You Get Automatically

✅ **No secrets to configure**
✅ **Automatic authentication**
✅ **Supply chain security** with artifact attestations
✅ **Proper permissions** already set in the workflow
✅ **Works out of the box**

## How to Use

Simply push to the `main` branch or trigger the workflow manually:

1. **Automatic triggers**: Every push to `main` branch
2. **Manual triggers**: Go to Actions tab → Select workflow → Click "Run workflow"

## Security Features

The workflow includes:

- **Artifact Attestation**: Unforgeable statements about where and how the image was built
- **Minimal Permissions**: Only the necessary permissions are granted
- **Secure Authentication**: Uses GitHub's built-in token system
- **Supply Chain Security**: Increased security for image consumers

## Troubleshooting

If you encounter any issues:

1. **Check workflow permissions**: Ensure the repository has Actions enabled
2. **Verify branch protection**: Make sure the main branch allows workflows to run
3. **Check GitHub status**: Sometimes issues are on GitHub's side
4. **Review workflow logs**: Detailed logs are available in the Actions tab

## No More Manual Setup!

The old approach required creating personal access tokens and adding secrets. The new approach is much simpler and more secure!

## Technical Details

The workflow uses:

- `permissions:` block to grant necessary access
- `GITHUB_TOKEN` for authentication (automatically available)
- `github.actor` as the username
- Built-in token with `packages: write` permission

This is the recommended approach from GitHub's official documentation.