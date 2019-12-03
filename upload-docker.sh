#!/bin/sh

VERSION=$CI_COMMIT_REF_NAME
PROJECT_PATH=`echo "$CI_PROJECT_PATH" | tr '[:upper:]' '[:lower:]'`
echo $PROJECT_PATH $VERSION
docker build -t registry.gitlab.com/$PROJECT_PATH:$VERSION .
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY

docker push registry.gitlab.com/$PROJECT_PATH:$VERSION
if [[ "$VERSION" == "master" ]]
then
  echo "master detected"
  docker tag registry.gitlab.com/$PROJECT_PATH:$VERSION registry.gitlab.com/$PROJECT_PATH:latest
  docker push registry.gitlab.com/$PROJECT_PATH:latest
fi
