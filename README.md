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

Build the docker image. Should only be necessary on first run or if dependencies change.

    docker-compose build

Start the container in detached mode

    docker-compose up --detach

Read application logs

    docker-compose logs --follow


License
-------
BSD
