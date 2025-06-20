# Use the official Python 3.12 image from Docker Hub
FROM mcr.microsoft.com/devcontainers/python:3.12

# # Install system dependencies (if any needed, add here)
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common \
        curl \
        wget \
        gnupg2 \
        lsb-release \
        && rm -rf /var/lib/apt/lists/*


# # Install Python dependencies
COPY requirements.txt /tmp/pip-tmp/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# Install Azure CLI
RUN apt-get update \
    && apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
    && AZ_REPO=$(lsb_release -cs) \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | tee /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install -y azure-cli \
    && rm -rf /var/lib/apt/lists/*


# # Install VS Code extensions for devcontainer
RUN code --install-extension ms-semantic-kernel.semantic-kernel \
    && code --install-extension esbenp.prettier-vscode \
    && code --install-extension ms-python.python \
    && code --install-extension ms-python.vscode-pylance || true

# # [Optional] Set up a non-root user (uncomment if needed)
# # ARG USERNAME=vscode
# # ARG USER_UID=1000
# # ARG USER_GID=$USER_UID
# # RUN groupadd --gid $USER_GID $USERNAME \
# #     && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
# #     && apt-get update && apt-get install -y sudo \
# #     && echo $USERNAME ALL=\"(ALL) NOPASSWD:ALL\" >> /etc/sudoers.d/$USERNAME \
# #     && chmod 0440 /etc/sudoers.d/$USERNAME

# # Set the default shell to bash
# SHELL ["/bin/bash", "-c"]

# # Set the working directory
WORKDIR /workspace
