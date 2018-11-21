<!--
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
-->

BigchainDB 쿼리
===================

노드 operator는 MongoDB의 쿼리 엔진의 최대 성능을 사용하여 모든 트랜잭션, 자산 및 메타데이터를 포함하여 저장된 모든 데이터를 검색하고 쿼리할 수 있습니다. 노드 operator는 외부 사용자에게 얼마나 많은 쿼리 파워를 송출할지 스스로 결정할 수 있습니다.


예제 쿼리가 포함된 블로그 게시물
------------------------------


BigchainDB 블로그에 MongoDB 도구를 사용하여 BigchainDB 노드의 MongoDB 데이터베이스를 쿼리하는 방법에 대한 게시물을 올렸습니다. 데이터에 대한 일부 특정 예제 쿼리가 주요 내용입니다. [여기서 확인하세요](https://blog.bigchaindb.com/using-mongodb-to-query-bigchaindb-data-3fc651e0861b)

MongoDB에 연결하기
-------------------------


MongoDB 데이터베이스를 쿼리하려면 먼저 데이터베이스에 연결해야 합니다. 그러기 위해선 호스트 이름과 포트를 알아야 합니다.

개발 및 테스트를 위해 지역 컴퓨터에서 BigchainDB 노드를 실행 중인 경우 호스트 이름은 "로컬 호스트"여야 하며 이러한 값을 변경하지 않는 한 포트는 "27017"이어야 합니다. 원격 시스템에서 BigchainDB 노드를 실행 중이며 해당 시스템에 SSH할 수 있는 경우에도 마찬가지입니다.

원격 시스템에서 BigchainDB 노드를 실행하고 MongoDB를 auth를 사용하고 공개적으로 액세스할 수 있도록 구성한 경우(권한이 있는 사용자에게) 호스트 이름과 포트를 확인할 수 있습니다.

쿼리하기
------------

BigchainDB 노드 운영자는 로컬 MongoDB 인스턴스에 대한 전체 액세스 권한을 가지므로 실행하는데 MongoDB의 다음의 API를 사용할 수 있습니다:

- [the Mongo Shell](https://docs.mongodb.com/manual/mongo/)
- [MongoDB Compass](https://www.mongodb.com/products/compass)
- one of [the MongoDB drivers](https://docs.mongodb.com/ecosystem/drivers/), such as [PyMongo](https://api.mongodb.com/python/current/), or
- MongoDB 쿼리에 대한 서드파티툴,  RazorSQL, Studio 3T, Mongo Management Studio, NoSQLBooster for MongoDB, or Dr. Mongo.

Note

SQL을 이용해 mongoDB 데이터베이스를 쿼리할 수 있습니다. 예를 들어:

   * Studio 3T: "[How to Query MongoDB with SQL](https://studio3t.com/whats-new/how-to-query-mongodb-with-sql/)"
   * NoSQLBooster for MongoDB: "[How to Query MongoDB with SQL SELECT](https://mongobooster.com/blog/query-mongodb-with-sql/)"

예를 들어, 기본 BigchainDB 노드를 실행하는 시스템에 있는 경우  Mongo Shell (``mongo``)을 사용하여 연결하고 다음과 같이 볼 수 있습니다.

    $ mongo
    MongoDB shell version v3.6.5
    connecting to: mongodb://127.0.0.1:27017
    MongoDB server version: 3.6.4
    ...
    > show dbs
    admin     0.000GB
    bigchain  0.000GB
    config    0.000GB
    local     0.000GB
    > use bigchain
    switched to db bigchain
    > show collections
    abci_chains
    assets
    blocks
    elections
    metadata
    pre_commit
    transactions
    utxos
    validators

위 예제는 몇 가지 상황을 보여줍니다:

- 호스트 이름이나 포트를 지정하지 않으면 Mongo Shell은 각각 `localhost`와 `27017`으로 가정합니다. (`localhost`는 우분투에 IP주소를 127.0.0.1로 설정했습니다.)


* BigchainDB는 데이터를 `bigchain`이라는 데이터베이스에 저장합니다.
* `bigchain` 데이터베이스에는 여러 [collections](https://docs.mongodb.com/manual/core/databases-and-collections/)가 포함되어 있습니다.
* 어떤 컬렉션에도 투표가 저장되지 않습니다. 이런 데이터는 모두 자체(LevelDB) 데이터베이스에 의해 처리되고 저장됩니다.

컬렉션에 대한 예시 문서
---------------------------------------

``bigchain`` 데이터베이스의 가장 흥미로운 부분은 아래와 같습니다:

- transactions
- assets
- metadata
- blocks

`db.assets.findOne()` 은 MongoDB 쿼리를 사용하여 이러한 컬렉션들을 탐색할 수 있습니다. 

### 트랜잭션에 대한 예시 문서

transaction 컬렉션에서 CREATE 트랜잭션에는 추가  `"_id"` 필드(MongoDB에 추가됨)가 포함되며 `"asset"`과 `"metadata"` 필드에는 데이터가 저장되어 있지 않습니다.

    {  
        "_id":ObjectId("5b17b9fa6ce88300067b6804"),
        "inputs":[…],
        "outputs":[…],
        "operation":"CREATE",
        "version":"2.0",
        "id":"816c4dd7…851af1629"
    }

A TRANSFER transaction from the transactions collection is similar, but it keeps its `"asset"` field.

    {  
        "_id":ObjectId("5b17b9fa6ce88300067b6807"),
        "inputs":[…],
        "outputs":[…],
        "operation":"TRANSFER",
        "asset":{  
            "id":"816c4dd7ae…51af1629"
        },
        "version":"2.0",
        "id":"985ee697d…a3296b9"
    }

### assets에 대한 예시 문서

assets에 대한 기술에는 MongoDB가 추가한 `"_id"` 분야와 CREATE 거래에서 나온 `asset.data` 그리고 `"id"`  세 가지 최상위 분야로 구성되어 있습니다.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{  
    "_id":ObjectId("5b17b9fe6ce88300067b6823"),
    "data":{  
        "type":"cow",
        "name":"Mildred"
    },
    "id":"96002ef8740…45869959d8"
}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### metadata에 대한 예시 문서


metadata 컬렉션의 문서는 MongoDB가 추가한 `"_id"`필드와 거래에서 나온 `asset.data`그리고 거래에서 나온 ``"id"`` 세 가지 최상위 분야로 구성되어 있습니다.

    {  
        "_id":ObjectId("5b17ba006ce88300067b683d"),
        "metadata":{
            "transfer_time":1058568256
        },
        "id":"53cba620e…ae9fdee0"
    }

### blocks에 대한 예시 문서

    {
        "_id":ObjectId("5b212c1ceaaa420006f41c57"),
        "app_hash":"2b0b75c2c2…7fb2652ce26c6",
        "height":17,
        "transactions":[
            "5f1f2d6b…ed98c1e"
        ]
    }

## 노드 operator가 외부 유저에게 보낼 수 있는 것

각 노드 operator는 외부 사용자가 자신의 로컬 MongoDB 데이터베이스에서 정보를 얻는 방법을 결정할 수 있습니다. 그들은 다음과 같은 것들을 보낼 수 있습니다:

- 외부유저를 쿼리 처리하는 로컬 MongoDB 데이터베이스 한된 제한된 권한을 가진 역할을 가진 MongoDB 사용자 예) read-only
- 제한된 미리 정의된 쿼리 집합을 허용하는 제한된 HTTP API, [BigchainDB 서버에서 제공하는 HTTP API](http://bigchaindb.com/http-api), 혹은Django, Express, Ruby on Rails, or ASP.NET.를 이용해 구현된 커스텀 HTTP API 
- 다른 API(예: GraphQL API) 제3자의 사용자 정의 코드 또는 코드를 사용하여 수행할 수 있습니다..

각 노드 operator는 로컬 MongoDB 데이터베이스에 대한 다른 레벨 또는 유형의 액세스를 노출할 수 있습니다.
예를 들어, 한 노드 operator가 최적화된 [공간 쿼리](https://docs.mongodb.com/manual/reference/operator/query-geospatial/)를 전문으로 제공하기로 정할 수 있습니다.

보안 고려사항
-----------------------

BigchainDB 버전 1.3.0 이전 버전에서는 하나의  MongoDB 논리 데이터베이스가 있었기 때문에 외부 사용자에게 데이터베이스를 노출하는 것은 매우 위험했으며 권장되지 않습니다. "Drop database"는 공유된 MongoDB 데이터베이스를 삭제합니다.

BigchainDB 버전 2.0.0 이상에선 각 노드에 고유한 독립 로컬 MongoDB 데이터베이스가 존재합니다. 노드 간 통신은 아래 그림 1에서와 같이 MongoDB 프로토콜이 아닌 Tendermint 프로토콜을 사용하여 수행됩니다. 노드의 로컬 MongoDB 데이터베이스가 손상되어도 다른 노드는 영향을 받지 않습니다.

![image](https://user-images.githubusercontent.com/36066656/48752907-f1dcd600-ecce-11e8-95f4-3cdeaa1dc4c6.png)

Figure 1: A Four-Node BigchainDB 2.0 Network

퍼포먼스 및 요금 고려사항
-----------------------------------

쿼리 프로세싱은 상당히 많은 리소스를 소모할 수 있으므로, BigchainDB 서버 및 Tendermint Core와 별도의 컴퓨터에서 MongoDB를 실행하는 것이 좋습니다.

노드 operator 는 조회에 사용되는 리소스를 측정하여 조회를 요청한 사람은 누구든지 요금을 청구할 수 있습니다.

일부 쿼리는 너무 오래 걸리거나 리소스를 너무 많이 사용할 수 있습니다. 노드 operator는 사용할 수 있는 리소스에 상한을 두고, 초과된다면 중지(또는 차단)해야 합니다.

MongoDB 쿼리를 더욱 효율적으로 만들기 위해  [인덱스](https://docs.mongodb.com/manual/indexes/)를 만들 수 있습니다.  이러한 인덱스는 노드 operator 또는 일부 외부 사용자가 생성할 수 있습니다(노드 운영자가 허용하는 경우). 인덱스는 비어 있지 않습니다. 새 데이터를 컬렉션에 추가할 때마다 해당 인덱스를 업데이트해야 합니다. 노드 운영자는 이러한 요금을 인덱스를 생성한 사람에게 전달하고자 할 수 있습니다. mongoDB에서는 [단일 컬렉션은 64개 이하의 인덱스를 가질 수 있습니다](https://docs.mongodb.com/manual/reference/limits/#Number-of-Indexes-per-Collection).

Tendermint voting 파워가 0인 노드인 추종자 노드를 생성할 수 있다. 여전히 모든 데이터의 복사본이 있으므로 읽기 전용 노드로 사용할 수 있습니다. Follower 노드는 투표 검증자의 작업 부하에 영향을 미치지 않고 서비스로 전문화된 쿼리를 제공할 수 있습니다(쓰기도 가능). 팔로워의 팔로워들도 있을 수 있습니다.

자바스크립트 쿼리 코드 예시
------------------------------

[MongoDB node.js 드라이버](https://mongodb.github.io/node-mongodb-native/?jmp=docs)와 같은 MongoDB 드라이버를 사용하여 다음 중 하나를 사용하여 노드의 MongoDB 데이터베이스에 연결할 수 있습니다. 여기 자바스크립트 쿼리 코드에 대한 링크가 있습니다.

- [The BigchainDB JavaScript/Node.js driver source code](https://github.com/bigchaindb/js-bigchaindb-driver)
- [Example code by @manolodewiner](https://github.com/manolodewiner/query-mongodb-bigchaindb/blob/master/queryMongo.js)
- [More example code by @manolodewiner](https://github.com/bigchaindb/bigchaindb/issues/2315#issuecomment-392724279)