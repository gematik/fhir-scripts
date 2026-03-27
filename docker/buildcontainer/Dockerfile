FROM alpine

# Capture architecture platform to build for
ARG TARGETPLATFORM

RUN apk add --no-cache \
    # fhirscripts
    sudo bash git python3 \
    # To install gCloud CLI
    curl \
    # .NET SDK for Firely Terminal
    dotnet8-sdk \
    # Node.js and NPM for FSH Sushi
    nodejs npm \
    # Java (OpenJDK) and Jeykll for IG Publisher
    openjdk21 jekyll \
    # To render PlantUML images
    graphviz fontconfig

# Download and install gCloud CLI
# This tries to use the architecture specific version
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    curl -Lo google-cloud-cli-linux.tar.gz https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-arm.tar.gz; \
    elif [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
    curl -Lo google-cloud-cli-linux.tar.gz https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz; \
    else \
    curl -Lo google-cloud-cli-linux.tar.gz https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86.tar.gz; \
    fi \
    && tar -xf google-cloud-cli-linux.tar.gz \
    && ./google-cloud-sdk/install.sh --quiet \
    && rm google-cloud-cli-linux.tar.gz

# Add gcloud to path
ENV PATH="/google-cloud-sdk/bin:${PATH}"

# Install UV for Python environments
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Install fhirscripts
RUN uv tool install git+https://github.com/gematik/fhir-scripts.git

# Install base tooling for image
RUN fhirscripts install \
    --sushi \
    --firely-terminal \
    --publishtools

# Add Firely Terminal to path
ENV PATH="/root/.dotnet/tools:${PATH}"

WORKDIR /project

# Entrypoint script
COPY entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh
ENTRYPOINT [ "/scripts/entrypoint.sh" ]

###########################
# Labels
###########################

ARG COMMIT_HASH=FromEnvironment
ARG VERSION=FromEnvironment

LABEL de.gematik.commit-sha=$COMMIT_HASH \
    de.gematik.version=$VERSION \
    de.gematik.vendor="gematik GmbH" \
    maintainer="patientteam@gematik.de" \
    de.gematik.app="FHIR Scripts Build Container" \
    de.gematik.git-repo-name="https://github.com/gematik/fhir-scripts"
