NCPDP SCRIPT FHIR Facade
===================
FHIR Facade for PDMP SCRIPT Standard Interfaces

[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/uwcirg/script-fhir-facade?label=latest%20release&sort=semver)](https://hub.docker.com/repository/docker/uwcirg/script-fhir-facade)

Development
-----------
To start the application follow the below steps in the checkout root

Copy default environment variable file and modify as necessary

    cp script.env.default script.env

Install HTTP client certificate and key

    cp pdmp.crt pdmp.key config/certs/

The certificate path is used when `SCRIPT_JWT_ASSERTION` is unset. To use the
OneHealthPort OAuth 2.0 JWT bearer grant instead, set `SCRIPT_JWT_ASSERTION` to
the pre-issued JWT, point `SCRIPT_ENDPOINT_URL` at the gateway data URL (no
port 8099), and set `SCRIPT_TOKEN_URL` if it is not the UAT token endpoint.
`SCRIPT_ORG_FACILITY_ID` is sent as `x-org-facility-id` and defaults to
`SCRIPT_FROM_QUALIFIER`. Access tokens are stored in Redis when
`REQUEST_CACHE_URL` is set, with a TTL taken from the token response
`expires_in`.

Build the docker image. Should only be necessary on first run or if dependencies change.

    docker-compose build

Start the container in detached mode

    docker-compose up --detach

Read application logs

    docker-compose logs --follow


License
-------
BSD
