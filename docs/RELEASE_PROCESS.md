# Release Process

This document describes the automated release process for the OpenShift AI Observability Summarizer project.

## Overview

The release process is split into two steps to ensure version correctness and provide verification checkpoints:

1. **Prepare Release**: Creates a version bump commit that triggers image builds
2. **Create Release**: Creates the GitHub release with release notes after verifying images

## Prerequisites

- Write access to the repository
- Images are published to `quay.io/ecosystem-appeng`

## Container Image Tagging Strategy

This project uses a multi-tag strategy to support both development iteration and release protection:

### During Build (Prepare Release)
When images are built, they receive two tags:
- **Version tag** (e.g., `1.1.0`) - Specific version for testing/verification
- **`latest` tag** - Always points to the most recent build

### During Release (Create Release)
When creating an official release, images receive additional tags:
- **v-prefixed tag** (e.g., `v1.1.0`) - **Protected from automated cleanup**
- **`latest` tag** - Updated to point to the official release

### Tag Lifecycle
```
Build workflow runs:
  → aiobs-metrics-ui:1.1.0
  → aiobs-metrics-ui:latest

Create release workflow runs:
  → aiobs-metrics-ui:v1.1.0 (protected, never deleted)
  → aiobs-metrics-ui:latest (updated)

After 30 days (automated cleanup):
  → aiobs-metrics-ui:1.1.0 (deleted)
  → aiobs-metrics-ui:v1.1.0 (kept - protected by v-prefix)
  → aiobs-metrics-ui:latest (kept - always protected)
```

**Why this matters:** The automated cleanup workflow (PR #169) deletes images older than 30 days, **except** those tagged with `v` prefix (e.g., `v1.0.0`) or `latest`. This ensures official releases are permanently available while development builds are cleaned up automatically.

**Note:** The `v` prefix follows standard GitHub release conventions (e.g., `v1.0.0`, `v2.0.0`) and clearly distinguishes official releases from CI builds.

## Dry Run Mode

Both workflows support **dry run mode** to preview changes without executing them. This is highly recommended for:
- First-time users learning the process
- Testing version calculations
- Verifying release notes before publishing
- Validating settings before making changes

To use dry run:
1. Check the **dry_run** checkbox when running either workflow
2. Review the output and summary
3. Re-run with dry_run unchecked to execute for real

## Step 1: Prepare Release

This step creates a commit with the correct version bump prefix, which triggers the image build workflow.

### Using GitHub UI

1. Go to **Actions** → **Prepare Release**
2. Click **Run workflow**
3. Select options:
   - **Version bump type**: Choose `major`, `minor`, or `patch`
   - **Custom version** (optional): Override with specific version like `1.2.3`
   - **Target branch**: Usually `dev` (or `main` for hotfixes)
   - **Dry run** (optional): Check to preview without pushing changes
4. Click **Run workflow**

**Tip**: Use dry run mode first to verify the expected version before pushing!

### What Happens

1. A commit is created with the appropriate prefix:
   - `major:` for major version bumps (e.g., 1.0.0 → 2.0.0)
   - `minor:` for minor version bumps (e.g., 1.0.0 → 1.1.0)
   - `patch:` for patch version bumps (e.g., 1.0.0 → 1.0.1)
2. The commit is pushed to the target branch
3. The **Build and push image** workflow automatically starts
4. Images are built and pushed to Quay.io with two tags:
   - Version tag (e.g., `1.1.0`)
   - `latest` tag (always points to most recent build)
5. Helm charts and Makefile are updated with the new version

### Verification

After the workflow completes:

1. Check the workflow summary for:
   - Expected version number
   - Links to verify images in Quay.io
2. Wait for the **Build and push image** workflow to complete
3. Verify all three images exist in Quay.io:
   - `aiobs-metrics-ui:<version>`
   - `aiobs-metrics-alerting:<version>`
   - `aiobs-mcp-server:<version>`

## Step 2: Create Release

After verifying the images are built correctly, create the GitHub release.

### Using GitHub UI

1. Go to **Actions** → **Create Release**
2. Click **Run workflow**
3. Fill in the details:
   - **Version**: Enter version with `v` prefix (e.g., `v1.0.0`)
   - **Target branch**: Same branch used in Step 1 (usually `dev`)
   - **Release notes** (optional): Custom notes, or leave empty for auto-generation
   - **Pre-release**: Check if this is a pre-release/beta
   - **Create PR to main**: Check to automatically create a PR from dev to main
   - **Dry run** (optional): Check to validate and preview without creating the release
4. Click **Run workflow**

**Tip**: Use dry run mode to preview release notes and validate version before creating the actual release!

### What Happens

1. Version format is validated (must be `vX.Y.Z`)
2. Version is verified against Makefile
3. Tag existence is checked (fails if tag already exists)
4. Release notes are generated (auto or custom)
5. Container images are tagged with:
   - `v` prefix (e.g., `v1.1.0`) - **protected from automated cleanup**
   - `latest` tag (updated to point to this release)
6. GitHub release is created with:
   - Tag pointing to the target branch
   - Release notes with changelog
   - Links to container images
7. (Optional) PR is created from dev to main

### Verification

After the workflow completes:

1. Check the release on GitHub: `https://github.com/<org>/<repo>/releases`
2. Verify release notes are correct
3. If PR was created, review and merge it to promote to main

## Complete Release Example

Here's a complete example of releasing version 1.1.0:

### 1. Dry Run - Prepare Release (Optional but Recommended)
```
Actions → Prepare Release → Run workflow
  - bump_type: minor
  - target_branch: dev
  - dry_run: true ✓
  → Shows: Would create commit "minor: prepare release 1.1.0"
  → Shows: Expected version would be 1.1.0
  → No changes pushed
```

### 2. Prepare Release (For Real)
```
Actions → Prepare Release → Run workflow
  - bump_type: minor
  - target_branch: dev
  - dry_run: false
  → Creates commit "minor: prepare release 1.1.0"
  → Triggers image builds
  → Outputs: Expected version 1.1.0
```

### 3. Wait and Verify
```
Wait for "Build and push image" workflow to complete
Verify images in Quay.io (both tags should exist):
  ✓ quay.io/ecosystem-appeng/aiobs-metrics-ui:1.1.0
  ✓ quay.io/ecosystem-appeng/aiobs-metrics-ui:latest
  ✓ quay.io/ecosystem-appeng/aiobs-metrics-alerting:1.1.0
  ✓ quay.io/ecosystem-appeng/aiobs-metrics-alerting:latest
  ✓ quay.io/ecosystem-appeng/aiobs-mcp-server:1.1.0
  ✓ quay.io/ecosystem-appeng/aiobs-mcp-server:latest
```

### 4. Dry Run - Create Release (Optional but Recommended)
```
Actions → Create Release → Run workflow
  - version: v1.1.0
  - target_branch: dev
  - dry_run: true ✓
  → Validates version format
  → Shows release notes preview
  → Shows what PR would be created
  → No release or tag created
```

### 5. Create Release (For Real)
```
Actions → Create Release → Run workflow
  - version: v1.1.0
  - target_branch: dev
  - release_notes: (empty for auto-generation)
  - prerelease: false
  - create_pr_to_main: true
  - dry_run: false
  → Tags images with v-prefix (official release):
    • aiobs-metrics-ui:v1.1.0
    • aiobs-metrics-alerting:v1.1.0
    • aiobs-mcp-server:v1.1.0
  → Updates latest tag to point to v1.1.0
  → Creates GitHub release v1.1.0
  → Creates PR from dev to main
```

### 6. Promote to Main
```
Review PR from dev to main
Merge PR after approval
  → main branch now has version 1.1.0
```

## Version Bump Guidelines

Choose the appropriate version bump type based on changes:

- **Major** (`major`): Breaking changes, API changes, major new features
  - Example: 1.0.0 → 2.0.0
- **Minor** (`minor`): New features, enhancements (backward compatible)
  - Example: 1.0.0 → 1.1.0
- **Patch** (`patch`): Bug fixes, minor improvements
  - Example: 1.0.0 → 1.0.1

## Troubleshooting

### Build workflow didn't start after prepare-release
- Check the Actions tab to see if the workflow was triggered
- Verify the commit was pushed successfully
- Manually trigger the "Build and push image" workflow if needed

### Images not found in Quay.io
- Check the "Build and push image" workflow logs for errors
- Verify Quay.io credentials are configured correctly
- Check for build failures

### Version mismatch error in create-release
- Ensure you ran "Prepare Release" first
- Check that the Makefile has the correct version
- Pull the latest changes from the target branch

### Tag already exists
- Check existing releases: `https://github.com/<org>/<repo>/releases`
- Either delete the existing tag or use a different version
- Never reuse version numbers

### PR creation failed
- Check repository permissions
- Verify GitHub token has `pull-requests: write` permission
- Manually create PR if needed

## Manual Fallback

If the automated workflows fail, you can create releases manually:

```bash
# 1. Update version in Makefile
sed -i 's/VERSION ?= .*/VERSION ?= 1.1.0/' Makefile

# 2. Commit and push
git add Makefile
git commit -m "minor: prepare release 1.1.0"
git push origin dev

# 3. Wait for images to build

# 4. Create tag and release
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 5. Create release on GitHub UI or using gh CLI
gh release create v1.1.0 --generate-notes
```

## Best Practices

1. **Use dry run first** - Always test with dry run mode before executing
2. **Always use dev branch** for releases, then promote to main via PR
3. **Verify images** before creating the release
4. **Use semantic versioning** consistently
5. **Review auto-generated release notes** before publishing (use dry run!)
6. **Create PR to main** for production releases
7. **Test deployments** after each release

## Support

For issues with the release process:
- Check workflow logs in the Actions tab
- Review this documentation
- Contact the maintainers
