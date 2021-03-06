# 분산 시스템을 위한 유일 ID 생성기 설계

auto_increment 기본키를 사용하는 전략은 분산 환경에서 통하지 않는다. 

데이터베이스 서버 한 대로는 그 요구를 감당할 수 없으며, 여러 DB 를 쓴다면 지연 시간을 낮추기가 무척 어려울 것!





## 1단계 문제 이해 및 설계 범위 확정

### 설계 범위

- ID는 유일해야한다.
- ID 는 숫자로만 구성되어야 한다
- 64비트로 표현될 수 있어야 한다.
- 발급 날짜에 따라 정렬 가능해야 한다.
- 시스템은 초당 10,000 개의 ID 를 생성할 수 있어야 한다.



## 2단계 개략적 설계안 제시 및 동의 구하기

ID 를 만드는 방법은 여러가지!

- 다중 마스터 복제
- UUID
- 티켓 서버
- 트위터 스노우플레이크

하나씩 살펴보자~!



### 다중 마스터 복제

이 접근법은 DB의 auto increment 를 사용한다. 다만, 1만큼 증가가 아닌 k만큼 증가한다! (k는 사용중인 DB서버의 수)

데이터 센터를 2개로 나누어 사용하고 있다면?

- DC1 의 ID 증가 - 1, 3, 5, 7, ...
- DC2 의 ID 증가 - 2, 4, 6, 8, ...

DB의 수를 늘리면 초당 생산 가능 ID 수도 늘릴 수 있지만 단점이 있다!

- 여러 DC에 걸쳐 규모를 늘리기 어렵다
- ID의 유일성은 보장되겠지만, 그 값이 시간 흐름에 맞추어 커지도록 보장할 수 없다.
- 서버를 추가하거나 삭제할 때 잘 동작하기 어렵다



### UUID

UUID는 유일성 보장하는 또 하나의 방법! - 컴퓨터 시스템에 저장되는 정보를 유일하게 식별하기 위한 128비트 수

충돌 가능성이 지극히 낮음!

-> 각 서버별 ID 생성기를 두고 사용할 수 있다!

**장점**

- UUID 만드는 것은 단순하며, 서버 사이 조율이 필요 없으므로 동기화 이슈도 없음
- 각 서버가 자신의 ID 생성을  책임지므로 규모 확장도 쉬움

**단점**

- ID가 128비트로 길다. 요구사항 상으로는 ID는 64비트
- ID를 시간순으로 정렬 불가능
- ID에 숫자가 아닌 값이 포함된다.



### 티켓 서버

3번째로 살펴볼 방법은 티켓 서버방법!

auto_increment 기능을 갖춘 DB서버, 티켓 서버를 중앙 집중형으로 사용하는 것!

**장점**

- 유일성이 보장되는 숫자로만 구성된 ID를 만들기 쉽다
- 구현하기 쉽고, 중소 규모 애플리케이션에 적합

**단점**

- 티켓서버가 SPOF! (단일 장애 지점)
- 여러 대 준비하려면 동기화 이슈가 발생한다....



### 트위터 스노우플레이크 접근법

마지막으로 살펴볼 방법으로 트위터가 제안한 방법! 

우리가 생각했던 설계사항을 모두 만족할 수 있는데, 
ID를 바로 생성하는 대신, Divide and Conquer 를 사용해보자!
ID를 여러 절(section)으로 분할 해보는 것!

64비트의 구조를 다음과 같이 나눈다.

| 구분            | 비트 수 |                                                              |
| --------------- | ------- | ------------------------------------------------------------ |
| 사인(sign) 비트 | 1       | 현재는 사용성 X. 나중을 위해 음수, 양수 구분                 |
| 타임스탬프      | 41      | 기원 시각(epoch)이후로 몇 ms wlskTsmswl skxksosek.           |
| 데이터센터 ID   | 5       | 2^5개, 32개의 데이터 센터를 구분할 수 있다.                  |
| 서버 ID         | 5       | 2^5개, 32개의 서버를 구분할 수 있다.                         |
| 일련번호        | 12      | 각 서버에서 ID를 생성할 때마다 1만큼 증가시킨다. 이 값은 1ms 가 경과할 때마다 0으로 초기화해준다. |





## 3단계 상세 설계

트위터 스노우플레이크 방법을 사용하기로 결정, 상세하게 설계해보자!

- 데이터센터 ID 와 서버ID는 시스템의 시작과 동시에 결정되며 운영중에는 바뀌지 않을 것이다. 
- 타임스탬프와 일련번호는 동작하면서 만들어지는 값! 

타임스탬프와 일련번호 설계가 어떨지 확인해보자.



### 타임스탬프

ID 구조에서 41비트를 차지하고 있다. 

41비트로 표현할 수 있는 타임스탬프의 최댓값 = 2^41 - 1 = 약 69년

-> 69년동안만 동작하는데, 69년 이후에는 기원 시각을 바꾸거나 ID 체계를 다른 것으로 이전해야한다.

### 일련번호

일련 번호는 12비트이므로 1ms 동안 2^12 = 4096개를 만들어 낼 수 있다.



## 4단계 마무리

분산 환경에서 규모 확장이 가능한 방법은 스노우 플레이크 방법이였다. 

만일 추가로 더 논의하고자 한다면?

- 시계 동기화
  - 모든 서버가 같은 시계를 사용한다고 가정했지만, 그렇지 않은 상황이라면? (하나의 서버가 여러 코어에서 실행되는 경우 / 여러 서버가 물리적으로 독립된 여러 장비에서 실행되는 경우)
    - Network Time Protocol 이라는 것을 사용하면 된다.
- 각 절(section)길이 최적화
  - 동시성이 낮고 수명이 긴 애플리케이션이라면? 일련번호의 길이를 줄이고 타임스탬프를 늘리자!
- 고가용성
  - ID생성기는 높은 가용성을 제공해야한다!