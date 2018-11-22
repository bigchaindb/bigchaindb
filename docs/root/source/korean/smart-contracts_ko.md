<!--
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
-->

BigchainDB 및 스마트계약
==============================

BigchainDB에는 스마트 계약 (즉, 컴퓨터 프로그램)의 소스 코드를 저장할 수 있지만 BigchainDB는 임의의 스마트 계약을 실행하지 않습니다.

BigchainDB는 대체 가능한 자산과 대체 할 수없는 자산 모두를 전송할 수있는 권한을 가진 사람을 시행하는 데 사용할 수 있습니다. 이중 지출을 막을 것입니다. 즉, ERC-20 (대체 가능한 토큰) 또는 ERC-721 (대체 할 수없는 토큰) 스마트 계약 대신 BigchainDB 네트워크를 사용할 수 있습니다.

자산 이전 권한은 쓰기 권한으로 해석 될 수 있으므로 로그, 저널 또는 감사 내역에 기록 할 수있는 사람을 제어하는데 사용할 수 있습니다. [BigchainDB의 사용 권한](https://github.com/bigchaindb/bigchaindb/blob/master/docs/root/source/korean/permissions-ko.md)에 대한 자세한 내용은 페이지에서 확인하십시오.

BigchainDB 네트워크는 oracles 또는 체인 간 통신 프로토콜을 통해 다른 블록 체인 네트워크에 연결할 수 있습니다. 이는 BigchainDB를 다른 블록 체인을 사용하여 임의의 스마트 계약을 실행하는 솔루션의 일부로 사용할 수 있음을 의미합니다.
