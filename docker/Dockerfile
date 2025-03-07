ARG SPLUNK_VERSION=9.1

#####################################################################
# CI STAGE
#####################################################################

FROM ghcr.io/zepdev/docker-splunkdev/splunk-ci:${SPLUNK_VERSION} as CI
# add needed external apps
# COPY ...
# # does not set ENV SPLUNK_APPS_URL - apps are installed optimized in github acitons workflow

#####################################################################
# DEV STAGE - used for local development
#####################################################################

FROM ghcr.io/zepdev/docker-splunkdev/splunk-dev:${SPLUNK_VERSION}
# add needed external apps
# COPY --from=ghcr.io/zepdev/splunk-splunkbase-apps/splunk_ml_toolkit:5.3.3 . /tmp/apps
# COPY --from=ghcr.io/zepdev/splunk-splunkbase-apps/visualization_toolbox:0.2.3 . /tmp/apps
# ENV SPLUNK_APPS_URL="/tmp/apps/Splunk_ML_Toolkit-5.3.3.tgz /tmp/apps/visualization_toolbox-0.2.3.tgz"