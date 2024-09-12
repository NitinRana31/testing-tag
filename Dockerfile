#   Copyright IBM Corporation 2021
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

FROM registry.access.redhat.com/ubi8/ubi-minimal:latest
WORKDIR /app
RUN microdnf update && microdnf install -y java-1.8.0-openjdk-devel wget unzip && microdnf clean all

# environment variables
ENV PORT 8080

RUN wget https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/wasdev/downloads/wlp/21.0.0.12/wlp-jakartaee9-21.0.0.12.zip && \
    unzip wlp-jakartaee9-21.0.0.12.zip && \
    rm wlp-jakartaee9-21.0.0.12.zip
COPY target/java-maven.war wlp/usr/servers/defaultServer/dropins/
COPY server.xml wlp/usr/servers/defaultServer/
EXPOSE 9080
CMD ["wlp/bin/server", "run"]
