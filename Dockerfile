FROM cumuluss/geolambda:full

WORKDIR $BUILD

COPY bin $BUILD/bin
COPY setup.py requirements*txt MANIFEST.in $BUILD/
RUN \
    cp bin/* /usr/local/bin/; \
    pip install -r requirements.txt; \
    pip install -r requirements-dev.txt;

COPY ${PROJECT} $BUILD/${PROJECT}
RUN \
	cd $BUILD; \
    pip install .; \
    rm -rf *

WORKDIR /home/cumulus

ENTRYPOINT ${CLI_NAME}