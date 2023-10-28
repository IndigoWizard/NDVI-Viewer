# Contribution Guide

All contribution is welcome (_adding features✨, bug fix🔧, bug report🐛, design✒️, documentation📝, fixing typos ...etc_).

## To contribute to this repo, please make sure to follow the rules

### Rules

- Always check repo's open ***[issues](issues)*** to avoid duplicates, conflict and ambiguous work.
- Open a new issue stating the subject of your upcoming contribution if no already existing open issue is related to the subject.
- If it's a **one-time issue**, ask a maintainer to assign you to the issue before starting to work on it.
- Always make sure your own fork of the repo is up to date (sync) with the original repo.
- Updating the `Streamlit` package changes the class names of elements > Requires updating CSS class names.
### Issues

- Issues are labbeled to make them easier for contributors/mantainers to identify.
- Always check the existing issues to avoid conflict and duplicates.
- Request to be assigned to an issue before you start working on it.

### Branches

I'm using integrated GitFlow for this project, so the setup is:

**Branches:**
- Master = streamlit-app
- Develop = dev

**Prefixes:**
- Feature = feature/
- Release = release/
- Hotfix = hotfix/
- Version tag = 0.0.0 (using [SemVer](https://semver.org/))

Most existing branches are feature branches and named as such, e.g: "features/UI" or "features/imagery-analysis"...

### Pull Requests

- Do not push your **node modules** / **pycache** folder.
- Make sure you give your PR a clear discription and a **meaningful title** of your contribution.
- Create a new branch for you contribution and name it relatively to its theme (e.g: **UI-dark-theme** / or if using gitflow use use e.g: **feature/UI**).
- Document your code, no one has time to figure out the meaning of your ancient rituals codes ...
- Make sure your contribution don't break existing features.
- Link the issue(s) you worked on in your pull request description.
- Use visual displays (screenshots, pictures, videos) to express the new changes you added in your PR if you contributed to an issue that affects the looks, functions of the project.



## License

By contributing to this project, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.

Thank you for contributing to [NDVI Viewer]!
