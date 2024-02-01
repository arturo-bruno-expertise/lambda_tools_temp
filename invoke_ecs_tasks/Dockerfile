FROM ghcr.io/lambgeo/lambda-gdal:3.6 as gdal
FROM public.ecr.aws/lambda/python:3.11

ENV PACKAGE_PREFIX=/var/task

# Bring C libs from lambgeo/lambda-gdal image
COPY --from=gdal /opt/lib/ ${PACKAGE_PREFIX}/lib/
COPY --from=gdal /opt/include/ ${PACKAGE_PREFIX}/include/
COPY --from=gdal /opt/share/ ${PACKAGE_PREFIX}/share/
COPY --from=gdal /opt/bin/ ${PACKAGE_PREFIX}/bin/

ENV \
  GDAL_DATA=${PACKAGE_PREFIX}/share/gdal \
  PROJ_LIB=${PACKAGE_PREFIX}/share/proj \
  GDAL_CONFIG=${PACKAGE_PREFIX}/bin/gdal-config \
  GEOS_CONFIG=${PACKAGE_PREFIX}/bin/geos-config \
  PATH=${PACKAGE_PREFIX}/bin:$PATH

ARG AWS_REGION=$AWS_REGION
ARG AWS_ACCOUNT=$AWS_ACCOUNT
ARG AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

RUN yum install -y gcc-c++ postgresql-devel python-psycopg2 postgresql-libs awscli

RUN aws configure set aws_access_key_id "${AWS_ACCESS_KEY_ID}" && \
    aws configure set aws_secret_access_key "${AWS_SECRET_ACCESS_KEY}" && \
    aws configure set default.region "${AWS_REGION}"

RUN aws codeartifact login \
    --tool pip \
    --repository data_warehouse \
    --domain expertise \
    --domain-owner ${AWS_ACCOUNT} \
    --region ${AWS_REGION}

COPY requirements.txt ./
RUN python3.11 -m pip install -r requirements.txt --no-cache -t .
RUN pip cache purge || echo "No cache to delete!"

COPY ./ ./

CMD ["app.lambda_handler"]