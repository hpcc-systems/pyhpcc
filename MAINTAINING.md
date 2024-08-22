# Maintaining PyHPCC

As project maintainers, we merge PR requests, conduct code reviews, and maintain our repository overall.

## Handling Pull Requests
- Contributors are encouraged to show interest in the issue.
- Acknowledge the contributor's interest and ask to work on the issue.
- GitHub Workflow Checks are enforced to check build status and docs, run tests, check formatting and linting, and show code coverage.
- Check cover coverage to see if the test coverage is greater than 85% for every file.
- Add feedback to the contributor to make changes if necessary.
- Merge the code to the dev branch.

## Creating a new release
- Merge changes from the `dev` branch to the `main` branch.
- Create a new branch from `main` to modify the `current version` to `new version` in `pyproject.toml` file
- Merge the code to the `main` by creating a Pull Request
- After the version change is merged, Go to [releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) tab to create a new release in GitHub
- Create a new tag with the `new version` as the tag with the target branch `main`
- Generate the release notes and make changes as necessary.
- Publish the release and check GitHub actions if the release workflow ran without errors.
