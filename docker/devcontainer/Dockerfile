FROM mcr.microsoft.com/devcontainers/base:alpine-3.20

# Setzen der Umgebungsvariablen
ENV CLOUD_SDK_VERSION=464.0.0
ENV FIRELY_TERMINAL_VERSION=3.3.2
ENV JAVA_VALIDATOR_VERSION=6.3.25

# Google Cloud SDK herunterladen und installieren
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    tar -xf google-cloud-cli-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet && \
    rm google-cloud-cli-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz

RUN apk add --no-cache \
    # .NET SDK for Firely Terminal
    dotnet8-sdk \
    # icu-libs \
    # Node.js and NPM for FSH Sushi
    nodejs npm \
    # Java (OpenJDK) and Jeykll for IG Publisher
    openjdk17 jekyll \
    # Additional dependencies
    # jq findutils curl ca-certificates \
    # PlantUML
    graphviz fontconfig

# Switch to the vscode user
USER vscode

# Setup for FHIR Validator
RUN mkdir -p /home/vscode/.fhir/validators/
RUN wget -q https://github.com/hapifhir/org.hl7.fhir.core/releases/download/$JAVA_VALIDATOR_VERSION/validator_cli.jar -O /home/vscode/.fhir/validators/validator_cli.jar

# Add gcloud to user path
ENV PATH="/google-cloud-sdk/bin:${PATH}"

# Install UV for Python environments
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

RUN uv tool install git+https://github.com/gematik/fhir-scripts.git

RUN fhirscripts install \
    --sushi \
    --firely-terminal

# Add Firely Terminal to user path
ENV PATH="/home/vscode/.dotnet/tools:${PATH}"
