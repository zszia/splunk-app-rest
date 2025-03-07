# SplunkRest

After setting up the [development environment](#development-environment)
open the workspace as a development container in visual studio code.

Then run `make`.

## configuration and preconditions

### development environment

For development a [development container](https://code.visualstudio.com/docs/remote/containers) is used.

Following components are needed:

- Visual Studio Code with [Remote-Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
- Github credentials helper
  
  ```sh
  sudo apt install gh
  ```

  and configuration of the github helper in .gitconfig file of the user
  ```
  ...
  [credential "https://github.com"]
        helper = !/usr/bin/gh auth git-credential
  ...
  ```

- if running on windows, use a linux distribution in the WSL2 environment and checkout the code in that environment
  (otherwise docker will be slow)

  ```sh
  # get list of distributions
  wsl --list --online
  # install ubuntu
  wsl --install --distribution Ubuntu-20.04
  ```

  For troubleshooting see [Install WSL](https://docs.microsoft.com/en-us/windows/wsl/install).

- pull the splunk devcontainer 

  ```sh
  docker pull ghcr.io/zepdev/docker-splunkdev/splunk-dev:9.1
  ```

### force reset of development container 

To clear all data that is stored in the splunk etc and var volumes execute the following commands **outside the dev container**:

```sh
make clean-devcontainer
```

### update splunk in devcontainer

To update the devcontainer has to be recreated. Therefore run **outside the dev container**:

```sh
make clean-devcontainer
docker pull ghcr.io/zepdev/docker-splunkdev/splunk-dev:9.1
```

and rebuild the dev container in vscode


### github actions

- add the following github secrets (if not already present)
  - PERSONAL_ACCESS_USER (github token that has access to repository and dependent private repositories)
  - PERSONAL_ACCESS_TOKEN (github token that has access to repository and dependent private repositories)
  - SPLUNK_PASSWORD (optionally otherwise the default password "splunkdev" is used)

If the used CI target of the [Dockerfile](docker/Dockerfile) is not doing much work,
docker layer caching or image caching in github actions is counter-productive and will need more time to execute.

### build scripts

The project uses `gnu make` to build.
To enter project specific make targets, edit the [Makefile](./Makefile).

Common Makefile steps are shared between repositories and are contained in the submodule [.build](./.build).

## releasing and deployment

`make deploy` will call [slim](https://dev.splunk.com/enterprise/reference/packagingtoolkit/packagingtoolkitcli/) to create a release package in the `deploy` folder. This will also be used by github actions to create a release.

Configuration:

- [.slimignore](./SplunkRest/.slimignore): ignore files by pattern that should not be part of the release package
- [app.conf](./SplunkRest/default/app.conf): add metadata for the app

To release a new version:

1. increase version information using one of the following make targets:

   ```sh
   make version-major
   make version-minor
   make version-patch
   ```

   These targets will update the app.conf of all apps and create a commit with those changes

2. push to main
3. trigger release build on github using

   ```sh
   make release
   ```

   This target will push a new version tag to github and trigger the release build.