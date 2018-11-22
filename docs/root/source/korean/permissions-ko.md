<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# BigchainDB 사용 권한

BigchainDB를 사용하면 다른 사용자가 할 수 있는 것을 어느 정도 제어할 수 있습니다. 
이 능력은 \*nix환경에서의 "권한", SQL에서의 "특권", 보안 환경에서의 "액세스 제어"와 유사합니다.  

## 출력 지출/이전 권한

BigchainDB에서, 모든 출력에는 연관된 조건(crypto-condition)이 있습니다.

사용되지 않은 출력을 쓰거나 전송하려면, 사용자(또는 사용자 그룹)이 조건을 충족시켜야 합니다.
특정 사용자만이 출력을 보낼 권한이 있다는 뜻입니다. 가장 단순한 조건은, "공용 키에 해당하는 개인 키를 가진 사람만이 출력을 보낼 수 있습니다." 훨씬 더 정교한 조건들도 가능합니다, 예를 들어 “이 출력을 사용하려면,…"

- "…회계 그룹의 모든 사람이 서명 할 수 있습니다."
- "…네 명 중 세 명이 서명해야 합니다."
- "…Bob이 반드시 서명해야 하거나 Tom과 Sylvia 둘 모두가 서명해야 합니다."

자세한 내용은, [BigchainDB Transactions Spec](https://github.com/bigchaindb/BEPs/tree/master/tx-specs/)관련 **트랜잭션 구성요소:조건** 섹션을 참조하세요.

출력이 한번 소비되면 다시 사용할 수 없습니다: *아무도* 그렇게 할 권한이 없습니다. 즉, BigchainDB는 누구나 출력을 "이중 소비" 하도록 허용 하지 않습니다.

## 쓰기 권한

누군가 TRANSFER 트랜잭션을 만들면, `metadata` 필드에 임의의 JSON 객체를 넣을 수 있다. (적정 범위 내에서; 실제 BigchainDB 네트워크는 트랜잭션의 크기에 제한을 둔다.) 즉, TRANSFER 트랜잭션에서 원하는 모든 것을 쓸 수 있다.

BigchainDB에서 "쓰기 권한"이 없다는 의미인가요? 아닙니다!!

TRANSFER 트랜잭션은 입력이 이전 출력을 충족시키는 경우에만 유효(허용)합니다. 이 출력들에 대한 조건은 누가 유효한 TRANSFER 트랜잭션을 할 수 있는지 조절 할 것입니다. 즉, 출력에 대한 조건은 특정 사용자에게 관련 자산 내역에 무엇인가 쓸 수 있는 "쓰기 권한"을 부여하는 것과 같습니다.

예를 들어, 당신은 BigchainDB를 사용하여 오직 당신만이 쓰기권한이 있는 공용 저널을 작성 할 수 있습니다. 방법은 다음과 같습니다: 먼저 하나의 출력으로 `asset.data` 을 통해 `{"title": "The Journal of John Doe"}` 와 같이 되도록 CREATE 트랜잭션을 생성합니다. 이 출력에는 금액 1과 사용자(개인 키를 가진)만이 출력을 보낼 수 있는 조건이 있습니다. 저널에 무엇인가를 추가하고 싶을 때마다, `metadata` 같은 필드에 최신 항목을 넣은 TRANSFER 트랜잭션을 새로 만들어야 합니다.

```json
{"timestamp": "1508319582",
 "entry": "I visited Marmot Lake with Jane."}
```

TRANSFER 트랜잭션에는 하나의 출력이 있습니다. 이 출력에는 금액1과 사용자(개인키를 가진)만이 출력을 보낼 수 있는 조건이 있습니다. 기타 등등. 당신만이 자산 내역(당신의 저널)에 덧붙일 수 있습니다.

이와 같은 기술은 공학 노트북,공급망 기록,정부 회의록 등에도 사용 될 수 있습니다.

또한 더 정교한 것들도 할 수 있습니다. 예를 들어, 누군가가 TRANSFER 트랜잭션을 작성할 때마다, *다른 누군가*에게 사용 권한을 부여하여 일종의 작성자-전달 혹은 연쇄 편지를 설정한다.

Note

누구나 CREATE 트랜잭션의 `asset.data` 필드에 있는 JSON(조건하에)을 쓸 수 있습니다. 허가가 필요하지 않습니다.

## 읽기 권한

다음 페이지를 참고하세요, [:doc:BigchainDB, Privacy and Private Data](https://github.com/bigchaindb/bigchaindb/blob/master/docs/root/source/korean/private-data-ko.md).

## 역할 기반 액세스 제어(RBAC)

2017년 9월에, 우리는 [BigchainDB RBAC 하부 시스템을 정의 할 수 있는 방법에 대한 블로그 게시물](https://blog.bigchaindb.com/role-based-access-control-for-bigchaindb-assets-b7cada491997)을 게재 했습니다. 글을 쓴 시점(2018년 1월)에는 플러그인을 사용해야 해서, 표준 BigchainDB(다음에서 사용가능한 [BigchainDB Testnet](https://testnet.bigchaindb.com/) 를 사용 할 수 없었습니다. 이는 미래에 바뀔 수 있습니다. 만약 관심이 있다면, [BigchainDB로 연락하십시요.](https://www.bigchaindb.com/contact/)
