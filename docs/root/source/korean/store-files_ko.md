<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# BigchainDB에 파일을 저장하는 방법

BigchainDB 네트워크에 파일을 저장할 수는 있지만 그렇게하지 않는 것이 좋습니다. 파일이 아닌 구조화 된 데이터를 저장, 인덱싱 및 쿼리하는 데 가장 적합합니다.

분산 된 파일 저장소를 원하면 Storj, Sia, Swarm 또는 IPFS / Filecoin을 확인하십시오. 파일 URL, 해시 또는 기타 메타 데이터를 BigchainDB 네트워크에 저장할 수 있습니다.

BigchainDB 네트워크에 파일을 저장해야하는 경우,이를 수행하는 한 가지 방법은 긴 Base64 문자열로 변환 한 다음 해당 문자열을 하나 이상의 BigchainDB 트랜잭션 (CREATE 트랜잭션의 `asset.data`)에 저장하는 것입니다 , 또는 어떤 거래의 `메타데이터` 일 수도있다.
