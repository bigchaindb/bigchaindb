
<!-- Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0 -->

BigchainDB가 자산 등록 및 전송에 적합한 방법
==========================================================

BigchainDB는 모든 종류의 데이터를 저장할 수 있지만 자산 등록 및 전송을 저장하는 데 특히 유용합니다.:

* BigchainDB 네트워크에 전송되어 체크되고 저장되는 (있는 경우) 트랜잭션은 기본적으로 CREATE 트랜잭션과 TRANSFER 트랜잭션의 두 가지가 있습니다.
* CREATE 트랜잭션은 임의의 메타 데이터와 함께 모든 종류의 자산 (나눌 수 없거나 분할 할 수없는)을 등록하는 데 사용할 수 있습니다.
* 저작물에는 0 명, 1 명 또는 여러 명의 소유자가있을 수 있습니다.
* 자산 소유자는 자산을 신규 소유자에게 양도하려는 사람이 만족해야하는 조건을 지정할 수 있습니다. 예를 들어 5 명의 현재 소유자 중 최소 3 명이 TRANSFER 트랜잭션에 암호를 사용해야합니다.
* BigchainDB는 TRANSFER 트랜잭션의 유효성을 검사하는 과정에서 조건이 충족되었는지 확인합니다. (또한 누구나 만족하는지 확인할 수 있습니다.)
* BigchainDB는 자산의 이중 지출을 방지합니다.
* 유효성이 검증 된 트랜잭션은 [변경불가능](https://github.com/bigchaindb/bigchaindb/blob/master/docs/root/source/korean/immutable-ko.md) 입니다.

 Note

   우리는 "소유자"라는 단어를 다소 느슨하게 사용했습니다. **보다 정확한 단어**는 이행자, 서명자, 조정자 또는 이전 가능 요소 일 수 있습니다. 관련 [BigchainDB Transaction Spec](https://github.com/bigchaindb/BEPs/tree/master/tx-specs/)의 Owners에 대한 참고 사항 절을 참조하십시오.
