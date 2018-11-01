[![Codecov branch](https://img.shields.io/codecov/c/github/bigchaindb/bigchaindb/master.svg)](https://codecov.io/github/bigchaindb/bigchaindb?branch=master)
[![Latest release](https://img.shields.io/github/release/bigchaindb/bigchaindb/all.svg)](https://github.com/bigchaindb/bigchaindb/releases)
[![Status on PyPI](https://img.shields.io/pypi/status/bigchaindb.svg)](https://pypi.org/project/BigchainDB/)
[![Travis branch](https://img.shields.io/travis/bigchaindb/bigchaindb/master.svg)](https://travis-ci.org/bigchaindb/bigchaindb)
[![Documentation Status](https://readthedocs.org/projects/bigchaindb-server/badge/?version=latest)](https://docs.bigchaindb.com/projects/server/en/latest/)
[![Join the chat at https://gitter.im/bigchaindb/bigchaindb](https://badges.gitter.im/bigchaindb/bigchaindb.svg)](https://gitter.im/bigchaindb/bigchaindb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# BigchainDB 서버

BigchaingDB는 블록체인 데이터베이스입니다. 이 저장소는 _BigchaingDB 서버_를 위한 저장소입니다.

### 기본 사항

* [빠른 시작 사용해보기](https://docs.bigchaindb.com/projects/server/en/latest/quickstart.html)
* [BigchainDB 2.0 백서 읽기](https://www.bigchaindb.com/whitepaper/)
* [BigchainDB에 대한 _Hitchiker's Guide_를 확인십시오.](https://www.bigchaindb.com/developers/guide/)

### `master` Branch에서 BigchainDB 서버 실행 및 테스트

BigchaingDB 서버의 최신 버전을 실행하고 테스트하는 것은 어렵지 않습니다. [Docker Compose](https://docs.docker.com/compose/install/)의 최신 버전이 설치되어 있는지 확인하십시오. 준비가 되었다면,  터미널에서 다음을 실행하십시오.

```text
git clone https://github.com/bigchaindb/bigchaindb.git
cd bigchaindb
make run
```

이제 BigchainDB는 `http://localhost:9984/`에 연결되어야 합니다.

또한, 실행시키기 위한  다른 명령어들도 있습니다.

* `make start` : 소스로부터 BigchainDB를 실행하고 데몬화합니다. \(이는 `make stop` 을 하면 중지합니다.\)
* `make stop` : BigchainDB를 중지합니다.
* `make logs` : 로그에 첨부합니다.
* `make text` : 모든 유닛과 허가 테스트를 실행합니다.
* `make test-unit-watch` : 모든 테스트를 수행하고 기다립니다. 코드를 변경할 때마다 테스트는 다시 실행될 것입니다.
* `make cov` : 코드 커버리지를 확인하고 브라우저에서 결과를 엽니다.
* `make doc` : HTML 문서를 만들고, 브라우저에서 엽니다.
* `make clean` : 모든 빌드와 테스트, 커버리지 및 파이썬 아티팩트를 제거합니다.
* `make reset` : 모든 컨테이너들을 중지하고 제거합니다. 경고 : BigchainDB에 저장된 모든 데이터를 잃을 수 있습니다.

사용 가능한 모든 명령어를 보기 위해서는 `make` 를 실행하십시오.

### 모두를 위한 링크들

* [BigchainDB.com ](https://www.bigchaindb.com/)- 뉴스 레터 가입을 포함하는 BigchainDB 주요 웹 사이트
* [로드맵](https://github.com/bigchaindb/org/blob/master/ROADMAP.md)
* [블로그](https://medium.com/the-bigchaindb-blog)
* [트위터](https://twitter.com/BigchainDB)

### 개발자들을 위한 링크들

* [모든 BigchainDB 문서](https://docs.bigchaindb.com/en/latest/)
* [BigchainDB 서버 문서](https://docs.bigchaindb.com/projects/server/en/latest/index.html)
* [CONTRIBUTING.md](https://github.com/bigchaindb/bigchaindb/blob/master/.github/CONTRIBUTING.md) - 기여를 하는 방법
* [커뮤니티 가이드라인](https://github.com/bigchaindb/bigchaindb/blob/master/CODE_OF_CONDUCT.md)
* [이슈 작성](https://github.com/bigchaindb/bigchaindb/issues)
* [pull request 하기](https://github.com/bigchaindb/bigchaindb/pulls)
* [Gitter 채팅방](https://gitter.im/bigchaindb/bigchaindb)

### 합법

* [라이선스](https://github.com/bigchaindb/bigchaindb/blob/master/LICENSES.md) - 오픈 소스 & 오픈 콘텐츠
* [발행](https://www.bigchaindb.com/imprint/)
* [연락처](https://www.bigchaindb.com/contact/)