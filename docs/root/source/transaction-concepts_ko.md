<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# 트랜잭션 개념

*트랜잭션*은 물건 (예 : 자산)을 등록, 발행, 생성 또는 전송하는 데 사용됩니다.

트랜잭션은 BigchainDB가 저장하는 가장 기본적인 종류의 레코드입니다. CREATE 트랜잭션과 TRANSFER 트랜잭션의 두 종류가 있습니다.


## 트랜잭션 생성

CREATE 트랜잭션은 BigchainDB에서 한 가지 (또는 자산)의 이력을 등록, 발행, 생성 또는 다른 방법으로 시작하는 데 사용될 수 있습니다. 예를 들어, 신원이나 창작물을 등록 할 수 있습니다. 이러한 것들을 종종 "자산"이라고 부르지만 literal 자산이 아닐 수도 있습니다.

BigchainDB는 BigchainDB Server v0.8.0부터 나눌 수있는 자산을 지원합니다. 이는 "공유"의 초기 숫자로 자산을 생성 / 등록 할 수 있음을 의미합니다. 예를 들어, CREATE 트랜잭션은 50 개의 오크 나무로 된 트럭로드를 등록 할 수 있습니다. 분할 가능한 자산의 각 주식은 서로 공유 할 수 있어야합니다. 주식은 대체 가능해야합니다.

CREATE 트랜잭션은 하나 이상의 출력을 가질 수 있습니다. 각 출력에는 관련 금액이 있습니다. 출력에 연결된 공유 수입니다. 예를 들어 자산이 50 개의 오크 나무로 구성되어있는 경우 한 출력에는 한 소유자 세트에 35 개의 오크 나무가 있고 다른 출력에는 다른 소유자 세트에는 15 개의 오크 나무가있을 수 있습니다.

또한 각 출력에는 연관된 조건이 있습니다. 출력을 전송 / 소비하기 위해 충족되어야하는 조건 (TRANSFER 트랜잭션에 의해). BigchainDB는 다양한 조건을 지원합니다. 자세한 내용은 관련 [BigchainDB 트랜잭션 Spec](https://github.com/bigchaindb/BEPs/tree/master/tx-specs/)과 관련된 **트랜잭션 구성 요소 : 조건 섹션**을 참조하십시오.

![Example BigchainDB CREATE transaction](./_static/CREATE_example.png)

위의 예제에서는 BigchainDB CREATE 트랜잭션 다이어그램을 보여줍니다. Pam은 자산 3 주를 소유 / 통제하고 다른 주식은 없습니다 (다른 산출물이 없으므로).

각 출력에는 해당 출력의 조건과 연관된 모든 공개 키 목록이 있습니다. 다시 말하면, 그 목록은 "소유자"의 목록으로 해석 될 수 있습니다.보다 정확한 단어는 이행자, 서명자, 컨트롤러 또는 이전 가능 요소 일 수 있습니다. 관련 [BigchainDB Transactions Spec](https://github.com/bigchaindb/BEPs/tree/master/tx-specs/) **소유자에 관한 참고 사항** 섹션을 참조하십시오.

CREATE 트랜잭션은 모든 소유자가 서명해야합니다. (만약 당신이 그 서명을 원한다면, 그것은 인코딩되었지만 하나의 입력의 "이행"에있다.)

## 트랜잭션 이전

트랜잭션 이전은 다른 트랜잭션 (CREATE 트랜잭션 또는 다른 TRANSFER 트랜잭션)에서 하나 이상의 출력을 전송 / 소비 할 수 있습니다. 이러한 출력물은 모두 동일한 자산과 연결되어야합니다. TRANSFER 트랜잭션은 한 번에 하나의 자산의 공유 만 전송할 수 있습니다.

트랜잭션 이전의 각 입력은 다른 트랜잭션의 한 출력에 연결됩니다. 각 입력은 전송 / 소비하려는 출력의 조건을 충족해야합니다.

트랜잭션 이전은 위에서 설명한 CREATE 트랜잭션과 마찬가지로 하나 이상의 출력을 가질 수 있습니다. 투입물에 들어오는 총 주식 수는 산출물에서 나가는 총 주식 수와 같아야합니다.

![Example BigchainDB transactions](./_static/CREATE_and_TRANSFER_example.png)

위 그림은 두 개의 BigchainDB 트랜잭션, CREATE 트랜잭션 및 TRANSFER 트랜잭션의 다이어그램을 보여줍니다. CREATE 트랜잭션은 이전 다이어그램과 동일합니다. TRANSFER 트랜잭션은 Pam의 출력을 소비하므로 TRANSFER 트랜잭션의 입력에는 Pam의 유효한 서명 (즉, 유효한 이행)이 포함되어야합니다. TRANSFER 트랜잭션에는 두 개의 출력이 있습니다. Jim은 하나의 공유를 가져오고 Pam은 나머지 두 개의 공유를 가져옵니다.

용어 : "Pam, 3"출력을 "소비 된 트랜잭션 출력"이라고하며 "Jim, 1"및 "Pam, 2"출력을 "사용되지 않은 트랜잭션 출력"(UTXO)이라고합니다.

**예제 1:** 빨간 차가 Joe가 소유하고 관리한다고 가정합니다. 자동차의 현재 전송 조건에서 Joe가 유효한 전송을 서명해야한다고 가정합니다. Joe는 Joe의 서명 (현재 출력 조건을 충족시키기 위해)과 Rae가 유효한 전송을 서명해야한다는 새로운 출력 조건을 포함하는 입력을 포함하는 TRANSFER 트랜잭션을 작성할 수 있습니다.

**예제 2:** 예를 들어 동일한 자산 유형의 이전에 전송되지 않은 4 개의 자산에 대한 출력 조건을 충족하는 TRANSFER 트랜잭션을 생성 할 수 있습니다. 종이 클립. 총 금액은 20, 10, 45 및 25 일 수 있으며, 말하자면 총 100 개의 클립입니다. 또한 TRANSFER 트랜잭션은 새로운 전송 조건을 설정합니다. 예를 들어, Gertrude가 서명하는 경우에만 60 개의 클립 클립이 전송 될 수 있으며 Jack과 Kelly가 서명하는 경우에만 40 개의 클립 클립이 전송 될 수 있습니다. 들어오는 클립 클립의 합계가 나가는 클립 클립의 합계와 같아야합니다 (100).

## 트랜잭션 유효성

언제 트랜잭션이 유효한지 유효성을 검사하는 것에 관해 해당 블로그에 게시되어있습니다. *The BigchainDB Blog*:
["What is a Valid Transaction in BigchainDB?"](https://blog.bigchaindb.com/what-is-a-valid-transaction-in-bigchaindb-9a1a075a9598) (Note: That post was about BigchainDB Server v1.0.0.)

Each [BigchainDB Transactions Spec](https://github.com/bigchaindb/BEPs/tree/master/tx-specs/) documents the conditions for a transaction (of that version) to be valid.

## 트랜잭션 예시

아래의 [HTTP API 문서](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html)와 [the Python 드라이버 문서](https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html)에는 예제 BigchainDB 트랜잭션이 있습니다.
.
