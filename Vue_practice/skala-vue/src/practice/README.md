# Vue Syntax 실습 — Weather Mockup ver1 (2026.08.25)

Vue 3 Composition API(`<script setup>`)의 기본 템플릿 문법을 익히기 위한 날씨 카드 Mockup 구현

첫 Vue 사용이기 때문에 최대한 다양한 방법론을 적용하기보다 과제 요구사항을 우선적으로 수행하고, 각 요구사항에서 구현 가능한 방법을 비교하며 적절한 방식을 선택

## 1. 배열 렌더링 — v-for, :key

Action:
여러 도시의 날씨 정보를 배열로 관리하고 v-for를 사용해 카드 반복 출력
key에는 배열의 인덱스 대신 각 도시가 가지고 있는 고유한 id 사용

Why:
:key에 index를 사용해도 단순한 화면 출력에는 문제가 없지만 배열의 중간에 데이터가 추가되거나 삭제되면 인덱스가 변경될 수 있음
데이터의 위치가 아닌 데이터 자체를 구분할 수 있도록 고유한 id를 사용하는 것이 더 적절하다고 판단

## 2. 조건부 렌더링 — v-if, v-else

Action:
도시의 기온을 기준으로 25도 이상이면 더움, 25도 미만이면 선선함이라는 라벨 표시
v-if를 2번 사용하는 방법과 v-if, v-else를 사용하는 방법을 비교한 후 v-if와 v-else 사용

Why:
v-if를 각각 사용해도 두 조건을 명시적으로 작성할 수 있어 동일한 결과 출력 가능
하지만 해당 case는 25도 이상과 25도 미만으로 반드시 하나의 조건에만 해당하고 다른 경우가 존재하지 않기 때문에 v-if와 v-else를 사용하는 것이 조건 관계를 더 명확하게 표현할 수 있다고 판단

## 3. 양방향 바인딩 및 한글 처리 — :value, @input

Action:
도시 이름을 입력할 수 있는 input을 구성하고 :value와 @input을 사용해 입력값 관리
입력한 도시명을 화면에 출력
한글 입력 시 발생하는 조합 과정을 처리하기 위해 compositionstart와 compositionend 사용

Why:
v-model을 사용하면 입력값과 상태를 간단하게 연결할 수 있지만, 이번 과제에서는 :value와 @input을 직접 사용해 입력 이벤트와 상태값 변경 과정을 확인
한글은 하나의 글자가 완성되기 전에 자음과 모음이 조합되는 과정이 있기 때문에 compositionstart와 compositionend를 사용해 조합 중인 입력과 최종 입력을 구분

## 4. 이벤트 및 수식어 — @click, @click.stop

Action:
날씨 카드 전체 클릭 시 선택한 도시를 상태바에 표시
카드 내부 상세보기 버튼 클릭 시 해당 도시의 날씨 내용을 window.alert로 표시
카드에는 @click을 사용하고 상세보기 버튼에는 @click.stop 사용

Why:
상세보기 버튼은 카드 내부에 있기 때문에 버튼 클릭 시 버튼의 이벤트와 함께 부모 요소인 카드의 클릭 이벤트까지 전달될 수 있음
상세보기 버튼 클릭 시 카드 선택 동작까지 실행될 필요가 없기 때문에 @click.stop을 사용해 이벤트 전파 차단
@click.stop과 event.stopPropagation()을 비교했을 때 두 방법 모두 이벤트 전파를 막을 수 있지만, 현재 구현에서는 템플릿에서 이벤트 전파 차단 의도를 바로 표현할 수 있는 @click.stop을 사용

## 5. 본인만의 데이터 추가 및 Mockup 구성

Action:
기존 날씨 데이터에 구미, 대구, 서울, 제주 데이터를 추가하고 부산을 포함해 총 5개의 도시 데이터 구성
추가한 데이터를 기존 날씨 카드와 동일한 구조로 렌더링하고 날씨 상태, 기온, 상세보기 기능이 동일하게 적용되도록 구성

Why:
기존 데이터만으로도 날씨 카드 반복 출력은 가능하지만 조건부 렌더링의 두 가지 경우를 모두 확인하기 위해 서로 다른 기온의 데이터 추가
추가 데이터 역시 기존 데이터와 동일한 구조로 구성해 별도의 렌더링 로직 없이 기존 v-for와 조건부 렌더링을 그대로 활용

## 정리 (ver1)

이번 실습에서는 v-for, v-if, v-else, ref, 이벤트 처리와 같은 Vue의 기본 문법을 사용
단순히 요구사항을 구현하는 것에서 끝내지 않고 같은 기능을 구현할 수 있는 여러 방법을 비교하면서 각각의 차이를 확인
특히 v-if와 v-else, v-model과 :value + @input, @click.stop과 stopPropagation()을 비교하면서 문법 자체보다 어떤 상황에서 어떤 방식을 사용하는지가 중요하다는 점을 확인

<br>

# Vue Composition API 실습 — Weather Composition ver2 (2026.08.25)

ver1에서 구현한 날씨 Mockup을 기반으로 Composition API의 상태 관리와 반응형 감시 기능을 추가한 구현

ver1의 화면 구조와 이벤트 처리 방식은 그대로 유지하고, 데이터를 어떻게 정의하고 파생시키며 변화를 감지하는지에 집중
computed와 함수 호출, watch와 watchEffect처럼 같은 목적을 다르게 구현할 수 있는 경우를 비교하며 상황에 맞는 방식을 선택

## 1. 반응형 상태 관리 — ref

Action:
검색어 searchQuery, 선택된 도시 selectedCityInfo, 지역별 날씨 데이터 weatherList를 ref로 정의
ver1에서 사용하던 searchText를 과제 명세에 맞춰 searchQuery로 변경
selectedCityInfo에는 상태바에 표시할 문구가 아닌 선택된 도시 객체 자체를 저장하고, 문구는 별도의 computed로 파생

Why:
ver1에서는 카드를 클릭할 때 상태바 문구 문자열을 그대로 상태에 저장했지만, 이 방식은 감시 대상이 데이터가 아닌 화면에 표시할 텍스트가 됨
요구사항 3에서 selectedCityInfo를 watch로 감시해야 하기 때문에 상태에는 도시 객체를 저장하고 표시용 문구는 파생시키는 방식으로 변경
이렇게 구성하면 문구 형식이 바뀌어도 상태 구조와 감시 로직은 수정할 필요가 없다고 판단

## 2. 검색 도시 필터링 — computed

Action:
전체 날씨 리스트에서 사용자가 입력한 검색어가 도시 이름에 포함된 항목만 필터링하여 filteredWeatherList에 저장
검색어가 비어 있는 경우에는 필터링하지 않고 원본 데이터를 그대로 반환
원본 weatherList는 수정하지 않고 파생된 결과만 화면에 출력

Why:
템플릿에서 필터링 함수를 직접 호출하는 방법과 computed를 사용하는 방법을 비교
함수를 호출하면 화면이 다시 그려질 때마다 매번 다시 실행되지만 computed는 의존하는 값이 변경될 때만 재계산되고 그 외에는 이전 결과를 재사용하기 때문에 불필요한 연산 방지 가능
검색 결과를 원본 배열에 직접 반영하면 검색어를 지웠을 때 원래 데이터를 복원할 수 없기 때문에 원본은 유지하고 결과만 파생시키는 방식으로 구현

## 3. 반응형 변수 변화 감시 — watch, watchEffect

Action:
selectedCityInfo는 watch를 사용해 감시하고 이전에 선택된 도시와 새로 선택된 도시, 그리고 변경된 상태바 문구를 콘솔로그로 출력
searchQuery는 watchEffect를 사용해 감시하고 도시 검색어를 타이핑할 때마다 현재 검색어를 콘솔로그로 출력

Why:
watch는 감시할 대상을 직접 지정하고 변경 전 값과 변경 후 값을 함께 전달받을 수 있으며 최초 렌더 시에는 실행되지 않음
watchEffect는 감시 대상을 지정하지 않아도 콜백 내부에서 사용한 반응형 값을 자동으로 추적하고 최초에 한 번 즉시 실행됨
상태바 문구가 어떤 도시에서 어떤 도시로 바뀌었는지 확인해야 하는 selectedCityInfo에는 이전 값을 받을 수 있는 watch가 적절하다고 판단
검색어의 현재 상태만 계속 추적하면 되는 searchQuery에는 대상을 따로 지정하지 않아도 되는 watchEffect가 적절하다고 판단

## 4. 검색 결과 표시 — Template 영역

Action:
검색어가 비어 있을 때는 filteredWeatherList가 원본 데이터를 반환하므로 전체 도시 카드 출력
검색어와 일치하는 데이터가 있을 때는 해당 데이터만 카드로 출력
검색어와 일치하는 데이터가 없을 때는 v-else를 사용해 일치하는 도시가 없다는 안내 문구 출력
v-for 카드 묶음 전체를 template 태그로 감싸고 해당 template에 v-if 적용

Why:
검색어가 비어 있는 경우를 템플릿에서 별도로 분기하는 방법과 computed에서 원본을 반환하도록 처리하는 방법을 비교
computed 단계에서 빈 검색어를 처리하면 템플릿은 결과가 있는지 없는지 두 가지 경우만 판단하면 되기 때문에 조건 분기가 단순해진다고 판단
카드 묶음을 감싸기 위해 div를 추가하면 실제 화면에 불필요한 요소가 생기기 때문에, 렌더링 결과에 남지 않는 template 태그를 사용해 v-for 전체를 조건부로 처리

## 5. 본인만의 반응형 상태 변수, Computed, Watcher 추가

Action:
반응형 상태 변수로 25도 이상인 도시만 표시하는 hotOnly를 추가하고 체크박스와 연결
Computed로 현재 화면에 표시되는 도시들의 평균 기온을 계산하는 averageTemp를 추가하고 검색 결과 건수와 함께 출력
Watcher로 검색 결과 건수의 변화를 감지하는 watch를 추가하고 이전 건수와 새 건수를 콘솔로그로 출력

Why:
hotOnly를 별도의 필터로 분리하지 않고 filteredWeatherList 내부의 조건으로 추가해 검색어 조건과 함께 동작하도록 구성했고, 조건이 늘어나도 computed 하나만 수정하면 되는 구조인지 확인
averageTemp는 filteredWeatherList에 의존하기 때문에 검색어나 필터가 바뀌면 자동으로 다시 계산되며, computed가 다른 computed를 의존할 수 있다는 점 확인
검색 결과 건수를 감시할 때 filteredWeatherList를 그대로 감시하면 필터가 재계산될 때마다 새로운 배열이 생성되어 건수가 같아도 콜백이 실행됨
따라서 감시 대상을 배열이 아닌 length를 반환하는 함수로 지정해 건수가 실제로 변경될 때만 콜백이 실행되도록 구현

## 정리 (ver2)

이번 실습에서는 ref, computed, watch, watchEffect와 같은 Composition API의 상태 관리와 반응형 감시 기능을 사용
ver1이 화면을 어떻게 그리는지에 대한 실습이었다면 ver2는 데이터를 어떻게 정의하고 파생시키며 변화를 감지하는지에 대한 실습
같은 결과를 만들 수 있는 방법이 여러 가지 있을 때 어떤 값을 상태로 저장하고 어떤 값을 파생시킬지 구분하는 것이 구조를 단순하게 만든다는 점을 확인
특히 selectedCityInfo에 문구가 아닌 도시 객체를 저장한 것과, 검색 결과 건수를 감시할 때 배열이 아닌 length를 감시하도록 지정한 부분에서 감시 대상을 무엇으로 잡느냐에 따라 동작이 달라진다는 점을 확인

<br>

# Vue Component 실습 — Weather Component ver3 (2026.08.26)

ver2에서 하나의 파일로 작성한 날씨 Mockup을 기능 변경 없이 Component 파일로 분리한 구현

화면에 보이는 결과와 동작은 ver2와 완전히 동일하게 유지하고, 하나의 파일에 모여 있던 상태와 화면을 어떤 기준으로 나눌지에 집중
props와 emits, slot을 사용해 분리된 Component가 서로 어떻게 데이터를 주고받는지를 확인

파일 구성: WeatherParent.vue, BaseDashboardCard.vue, SearchBar.vue, WeatherCard.vue, StatusBar.vue

## 1. 부모 Component의 반응형 데이터 유지 — WeatherParent.vue

Action:
ver2에서 작성한 반응형 상태(weatherList, searchQuery, selectedCityInfo, hotOnly)와 Computed, Watcher를 모두 WeatherParent.vue에 그대로 유지
자식 Component가 발생시킨 이벤트를 받아 상태를 변경하는 핸들러(handleUpdateQuery, handleSelectCard, handleClickDetail)를 부모에 작성
한글 조합 여부를 판단하는 isComposing만 예외적으로 SearchBar.vue로 이동

Why:
검색어를 SearchBar가 직접 상태로 가지는 방법과 부모가 상태를 가지고 자식은 전달만 받는 방법을 비교
검색어는 SearchBar에서 입력되지만 실제로 사용되는 곳은 목록을 필터링하는 filteredWeatherList이기 때문에, 상태를 자식이 소유하면 부모가 그 값을 다시 받아와야 하는 구조가 됨
상태를 한 곳에서만 변경하도록 부모가 소유하고 자식은 이벤트로 알리기만 하는 단방향 흐름이 데이터의 출처를 추적하기 쉽다고 판단
isComposing은 한글 입력이라는 입력 방식 자체의 문제이고 부모의 화면 로직과 관련이 없기 때문에 입력을 담당하는 SearchBar가 가지는 것이 적절하다고 판단

## 2. 디자인 공통화와 내용 주입 — BaseDashboardCard.vue

Action:
도시 검색 박스와 지역별 날씨 현황 박스가 공유하는 패널 디자인(테두리, 배경, 제목 스타일)을 BaseDashboardCard.vue로 공통화
패널 제목과 우측 부가 정보는 props(title, meta)로 전달받고, 박스 내부의 실제 내용은 slot으로 부모가 주입
검색 결과 건수와 평균 기온은 부모에서 listMeta라는 Computed로 조합해 meta props로 전달

Why:
박스 내부 내용까지 props로 전달받는 방법과 slot으로 주입받는 방법을 비교
도시 검색 박스는 입력창과 체크박스, 날씨 현황 박스는 카드 목록으로 내용의 구조가 완전히 다르기 때문에, props로 받으려면 BaseDashboardCard가 두 가지 경우를 모두 알고 분기해야 함
slot을 사용하면 BaseDashboardCard는 내용을 전혀 모른 채 패널 디자인만 담당하게 되므로, 나중에 다른 종류의 박스가 추가되어도 수정할 필요가 없다고 판단
meta는 화면에 표시할 문자열이므로 BaseDashboardCard가 계산하지 않고 데이터를 가진 부모가 Computed로 만들어 전달하는 방식으로 구현

## 3. 검색어 전달과 이벤트 발생 — SearchBar.vue

Action:
부모로부터 검색어를 query props로 전달받아 input의 :value에 바인딩하고 검색 중인 도시 문구에 표시
입력이 발생하면 상태를 직접 변경하지 않고 update-query 이벤트를 발생시키면서 입력값을 부모에게 전달
한글 조합 처리는 SearchBar 내부에서 수행하고, 조합이 끝난 시점의 값만 부모에게 전달

Why:
props로 받은 값은 자식이 직접 수정할 수 없기 때문에 값 변경은 반드시 이벤트로 부모에게 요청해야 함
v-model을 사용해 양방향으로 연결하는 방법과 update-query 이벤트를 명시적으로 발생시키는 방법을 비교
v-model을 쓰면 코드는 짧아지지만 값이 언제 누구에 의해 바뀌는지가 드러나지 않기 때문에, 이벤트 이름을 직접 지정하는 방식이 데이터 흐름을 명확하게 표현할 수 있다고 판단
한글 조합 중인 값까지 부모로 전달하면 부모의 검색어 상태가 조합 중인 글자로 계속 갱신되므로, 조합 처리를 마친 최종 값만 전달하도록 SearchBar 내부에서 걸러내도록 구현

## 4. 도시 객체 전달과 이벤트 발생 — WeatherCard.vue

Action:
표시할 도시 객체를 city props로 전달받아 도시명, 날씨 상태, 기온, 조건부 라벨을 출력
카드를 클릭하면 select-card 이벤트로 해당 도시 객체를 부모에게 전달
상세보기 버튼을 클릭하면 click-detail 이벤트로 해당 도시 객체를 부모에게 전달하고, 버튼에는 ver1부터 사용한 @click.stop을 그대로 유지

Why:
ver2에서는 카드 내부에서 selectedCityInfo를 직접 변경하고 window.alert도 직접 호출했지만, 분리 후에는 카드가 부모의 상태를 알 수 없음
카드는 어떤 일이 일어났는지만 알리고 그 결과로 무엇을 할지는 부모가 결정하도록 구성하면, 같은 카드를 다른 화면에서 다른 동작에 연결해 재사용할 수 있다고 판단
이벤트로 도시 이름과 상태를 따로 전달하는 방법과 도시 객체를 통째로 전달하는 방법을 비교했을 때, 객체를 전달하면 부모에서 필요한 속성만 꺼내 쓸 수 있고 이후 표시 항목이 늘어나도 이벤트 형식을 바꿀 필요가 없어 객체 전달 방식으로 구현
상세보기 버튼이 카드 내부에 있는 구조는 그대로이기 때문에 버블링 차단이 여전히 필요하며, @click.stop을 유지

## 5. Component별 디자인 분리 — style scoped

Action:
각 Component가 사용하는 디자인만 해당 파일의 style scoped에 배치
패널 디자인은 BaseDashboardCard, 입력창은 SearchBar, 카드와 버튼과 라벨은 WeatherCard, 상태바는 StatusBar로 분리
색상 값은 각 파일에 복사하지 않고 부모의 최상위 요소인 page에 CSS 변수로 한 번만 선언

Why:
style scoped는 해당 Component 내부에만 적용되므로 디자인을 분리하면 다른 Component의 스타일과 충돌할 가능성이 없어짐
색상 값을 Component마다 복사하면 색을 바꿀 때 모든 파일을 수정해야 하므로 관리가 어려워짐
CSS 변수는 style scoped의 적용 범위와 무관하게 DOM 구조를 따라 상속되기 때문에, 부모에서 한 번만 선언해도 자식 Component 내부에서 그대로 사용할 수 있다는 점을 확인

## 6. Slot으로 전달된 자식과의 직접 통신

Action:
SearchBar와 WeatherCard를 BaseDashboardCard의 slot으로 전달하면서, props와 이벤트 연결은 BaseDashboardCard를 거치지 않고 WeatherParent에서 직접 작성
25도 이상만 보기 체크박스도 slot 내부에 배치하고 부모의 hotOnly에 v-model로 직접 연결

Why:
slot으로 전달되는 내용은 시각적으로는 BaseDashboardCard 내부에 위치하지만 스크립트적으로는 부모의 스코프에서 컴파일되고 평가됨
따라서 BaseDashboardCard가 props를 다시 전달하거나 이벤트를 다시 발생시키는 중계 코드를 작성할 필요가 없음
체크박스를 SearchBar에 넣으면 hotOnly를 위한 props와 이벤트를 추가해야 하지만, slot 내부에 두면 부모 스코프이므로 v-model만으로 연결이 가능해 SearchBar를 검색 기능에만 집중시킬 수 있다고 판단
같은 이유로 체크박스와 검색 결과 없음 문구의 스타일은 부모의 style scoped에 유지

## 7. 추가 Component 분리 — StatusBar.vue

Action:
ver2에서 부모 템플릿에 직접 작성했던 상태바를 StatusBar.vue로 추가 분리
부모의 statusMessage Computed를 message props로 전달받아 표시만 담당하고, 자체 상태와 이벤트는 갖지 않도록 구성

Why:
상태바는 선택된 도시에 따라 문구만 바뀌는 표시 전용 영역이므로 상태나 이벤트가 필요하지 않음
표시만 담당하는 Component를 분리해 두면 부모 템플릿에는 화면 구조만 남고 세부 디자인은 각 파일로 이동하기 때문에 부모가 전체 구성을 파악하기 쉬워진다고 판단
props만 받고 이벤트를 발생시키지 않는 Component와, props와 emits를 모두 사용하는 Component를 함께 구현해 두 방식의 차이를 확인

## 정리 (ver3)

이번 실습에서는 props, emits, slot을 사용해 하나의 파일로 작성한 화면을 여러 Component로 분리
ver1이 화면을 그리는 문법, ver2가 데이터를 정의하고 감시하는 방법에 대한 실습이었다면 ver3는 그 둘을 어떤 단위로 나눌 것인가에 대한 실습
상태는 부모가 소유하고 자식은 props로 전달받아 표시하며 변경은 emits로 요청하는 단방향 흐름을 지키면, 값이 어디에서 바뀌는지 추적하기 쉬워진다는 점을 확인
디자인만 공통화하고 내용은 slot으로 주입하면 공통 Component가 내용을 알 필요가 없어져 재사용 범위가 넓어진다는 점을 확인
특히 slot으로 전달되는 내용이 부모 스코프에서 평가된다는 점을 이용해 중계 코드 없이 부모와 자식을 직접 연결한 부분에서, Component를 나누는 기준이 화면의 위치가 아니라 데이터의 소유와 책임이라는 점을 확인

<br>

# Vue Router 실습 — Weather Router ver4 (2026.08.26)

ver3에서 Component로 분리한 날씨 Mockup을 여러 페이지로 나누고 Vue Router로 화면을 전환하도록 구성한 구현

ver3까지는 하나의 화면 안에서 상태와 Component를 어떻게 나눌지가 주제였다면, ver4는 화면 자체를 여러 개로 나누고 주소(URL)와 화면을 어떻게 연결할지에 집중
RouterLink와 Programmatic Navigation, 정적 import와 동적 import처럼 같은 이동을 다르게 구현할 수 있는 경우를 비교하며 상황에 맞는 방식을 선택

파일 구성: main.js, App_ver4.vue, router_ver4/index.js, views_ver4(WeatherHomeView, WeatherDetailView, WeatherRankView, WeatherAboutView, NotFoundView), components_ver4/exercise_ver4(ver3의 Component 4개), data_ver4/weatherMock.js

## 1. 라우터 설정 — Lazy Loading, Catch-all Route

Action:
createRouter와 createWebHistory로 라우터를 생성하고 routes 배열에 5개 경로를 정의
첫 화면인 WeatherHomeView만 정적 import로 등록하고, 나머지 4개 View는 화살표 함수를 사용한 동적 import로 등록
정의되지 않은 경로를 처리하기 위해 path에 '/:pathMatch(._)_' 패턴을 사용한 Catch-all Route를 routes 배열의 가장 마지막에 배치

Why:
정적 import는 애플리케이션이 시작되는 시점에 모든 View를 메모리에 올리지만 동적 import는 해당 경로에 처음 진입할 때 파일을 내려받음
첫 화면은 접속과 동시에 반드시 필요하므로 정적으로 등록하고, 상세와 순위와 소개 페이지는 사용자가 방문하지 않을 수도 있으므로 동적으로 등록하는 것이 초기 로딩에 유리하다고 판단
Catch-all Route가 없으면 정의되지 않은 경로로 접근했을 때 Vue Router가 에러를 던지지 않고 단지 매칭되는 컴포넌트를 찾지 못하므로, RouterView 영역이 비어 화면이 하얗게 보이는 현상이 발생
routes 배열은 위에서부터 순서대로 매칭을 시도하기 때문에 모든 경로와 일치하는 Catch-all을 위에 두면 다른 경로가 실행되지 않으므로 반드시 마지막에 배치

## 2. 내비게이션 바와 콘텐츠 영역 — App_ver4.vue

Action:
화면마다 바뀌지 않는 브랜드 표시와 메뉴를 App_ver4.vue에 배치하고, 실제 페이지가 교체되는 자리에는 RouterView를 배치
메뉴 이동은 a 태그가 아닌 RouterLink로 구성
현재 보고 있는 메뉴 강조는 별도의 상태를 만들지 않고 RouterLink가 자동으로 부여하는 router-link-exact-active 클래스로 처리

Why:
a 태그를 사용하면 브라우저가 서버에 새 페이지를 요청하면서 전면 새로고침이 발생하고, 메모리에 들고 있던 반응형 데이터(ref, computed)가 모두 초기화됨
RouterLink는 새로고침을 차단하고 URL만 변경한 뒤 매칭되는 컴포넌트를 RouterView 자리에 교체하므로 SPA 구조가 유지된다고 판단
현재 경로를 반응형 상태로 직접 관리해 메뉴를 강조하는 방법도 가능하지만, Vue Router가 이미 활성 경로를 알고 클래스를 붙여주기 때문에 중복 관리를 피하기 위해 자동 클래스를 사용

## 3. 대시보드 화면 전환 — WeatherHomeView.vue

Action:
ver3의 WeatherParent.vue를 WeatherHomeView.vue로 옮기고 반응형 상태와 Computed와 Watcher는 그대로 유지
상세보기 버튼을 눌렀을 때 실행되던 window.alert를 제거하고 useRouter로 얻은 라우터 인스턴스의 push를 호출해 해당 도시의 상세 페이지로 이동하도록 변경
이동 경로는 도시 객체의 id를 사용해 router.push(`/weather/${city.id}`) 형태로 구성

Why:
alert는 브라우저가 화면을 멈추고 확인을 기다리는 방식이라 정보를 더 보여주거나 화면을 이어가기 어려운 반면, 페이지 이동은 상세 정보를 자유롭게 구성할 수 있음
ver3에서 WeatherCard가 상태를 직접 바꾸지 않고 click-detail 이벤트만 발생시키도록 만들어 두었기 때문에, 이번 변경에서 카드 파일은 한 줄도 수정하지 않고 부모의 핸들러만 교체해도 동작이 바뀐다는 점을 확인
RouterLink를 카드 안에 넣어 이동시키는 방법도 가능하지만, 상세보기는 버튼 클릭이라는 이벤트에 대한 후속 처리이므로 스크립트에서 이동을 지시하는 Programmatic Navigation이 의도에 더 맞는다고 판단

## 4. 동적 경로와 상세 페이지 — WeatherDetailView.vue

Action:
라우트 경로를 '/weather/:cityId'로 정의해 도시 코드를 동적 세그먼트로 수신
컴포넌트 내부에서 useRoute로 route 객체를 받아 route.params.cityId를 확인하고, onMounted 시점에 Mock Data에서 해당 도시 객체와 상세 관측 정보를 선택
체감 온도, 습도, 풍속, 강수 확률, 미세먼지, 예보 코멘트를 표시하고 이전 페이지와 대시보드로 돌아가는 버튼을 배치
존재하지 않는 도시 코드로 접근한 경우에는 안내 문구와 대시보드 이동 버튼만 표시

Why:
도시마다 별도의 라우트를 선언하면 도시가 늘어날 때마다 routes 배열을 수정해야 하므로, 콜론 식별자를 사용해 하나의 규칙으로 모든 도시를 처리하도록 구성
데이터를 script 최상단에서 즉시 조회하는 방법과 onMounted에서 조회하는 방법을 비교했을 때, 과제 요구사항이 Mount 시점 선택을 명시하고 있고 이후 실제 API 호출로 교체할 경우에도 같은 자리에 들어가게 되므로 onMounted를 사용
route.params로 받는 값은 주소창에 사용자가 직접 입력할 수도 있어 항상 유효하다고 보장할 수 없기 때문에, 찾지 못한 경우를 v-if로 분기해 화면이 비거나 오류가 나지 않도록 방어

## 5. 정적 소개 페이지 — WeatherAboutView.vue

Action:
반응형 상태 없이 서비스 설명과 ver1부터 ver4까지의 단계별 실습 내용을 표시
패널 디자인은 새로 만들지 않고 ver3에서 만든 BaseDashboardCard를 그대로 재사용
메인 대시보드로 돌아가는 이동은 RouterLink로 구성

Why:
소개 페이지는 사용자가 값을 입력하거나 상태가 변하는 부분이 없으므로 ref나 computed 없이 템플릿만으로 구성하는 것이 적절하다고 판단
BaseDashboardCard가 내용을 slot으로 주입받는 구조이기 때문에 날씨와 무관한 소개 내용도 수정 없이 담을 수 있다는 점을 확인
router.push를 버튼에 연결하는 방법도 가능하지만, 단순히 다른 페이지로 이동하기만 하는 경우에는 RouterLink가 마크업만으로 의도를 드러내고 브라우저의 링크 동작도 그대로 활용할 수 있다고 판단

## 6. 본인 추가 View와 Routing — WeatherRankView.vue

Action:
전체 도시를 기온이 높은 순으로 정렬해 보여주는 기온 순위 페이지를 추가하고 '/rank' 경로로 라우팅
가장 더운 곳과 가장 선선한 곳을 요약으로 표시하고, 목록의 항목을 누르면 해당 도시의 상세 페이지로 이동하도록 구성
정렬은 원본 배열을 직접 정렬하지 않고 전개 연산자로 복사본을 만든 뒤 정렬

Why:
sort는 원본 배열을 직접 변경하는 메서드이기 때문에 Mock Data를 그대로 정렬하면 같은 데이터를 참조하는 대시보드 화면의 순서까지 바뀌게 됨
여러 화면이 하나의 데이터를 공유하는 구조에서는 화면마다 필요한 가공을 파생된 값으로 만들고 원본은 건드리지 않아야 한다는 점을 확인
순위 페이지에서도 상세 페이지로 이동할 수 있게 구성해 하나의 상세 경로를 서로 다른 화면에서 재사용할 수 있다는 점을 확인

## 7. 공유 데이터와 전역 스타일 분리

Action:
ver3까지 WeatherParent 내부에 있던 날씨 배열을 data_ver4/weatherMock.js로 분리하고 도시 코드로 조회하는 함수를 함께 제공
ver3까지 최상위 요소에 선언했던 CSS 변수를 App_ver4.vue의 전역 style로 옮기고, 모든 View가 공유하는 페이지 컨테이너와 제목 스타일도 함께 배치
각 View와 Component의 고유한 디자인은 ver3와 동일하게 style scoped에 유지

Why:
대시보드와 상세와 순위 세 화면이 같은 날씨 데이터를 사용하므로, 각 파일에 배열을 복사하면 도시를 추가할 때 여러 파일을 수정해야 하고 값이 서로 어긋날 수 있음
데이터를 한 곳에서 관리하면 이후 실제 API로 교체할 때도 해당 모듈만 수정하면 되는 구조가 된다고 판단
CSS 변수를 특정 화면의 최상위 요소에 선언하면 그 화면 안에서만 상속되기 때문에, 화면이 여러 개로 늘어난 ver4에서는 어느 화면에도 속하지 않는 전역 위치에 선언해야 모든 View에서 동일하게 사용할 수 있다는 점을 확인

## 정리 (ver4)

이번 실습에서는 Vue Router를 사용해 하나의 화면으로 되어 있던 애플리케이션을 여러 페이지로 나누고 주소와 화면을 연결
ver1이 화면을 그리는 문법, ver2가 데이터를 정의하고 감시하는 방법, ver3가 화면을 Component 단위로 나누는 방법에 대한 실습이었다면 ver4는 화면 자체를 페이지 단위로 나누는 방법에 대한 실습
RouterLink와 router.push는 결과가 같지만 전자는 마크업으로 이동을 표현하고 후자는 이벤트 처리 결과로 이동을 지시한다는 점에서 사용하는 상황이 다르다는 점을 확인
ver3에서 자식 Component가 상태를 직접 바꾸지 않고 이벤트만 발생시키도록 구성해 둔 덕분에, 상세보기 동작을 alert에서 페이지 이동으로 바꾸는 과정에서 Component 파일을 수정할 필요가 없었다는 점을 확인
화면이 하나일 때는 드러나지 않던 데이터 공유와 전역 스타일의 위치 문제가 화면이 여러 개로 늘어나면서 드러났고, 여러 화면이 공유하는 것은 특정 화면에 속하지 않는 위치로 옮겨야 한다는 점을 확인

</br>

# Pinia 실습 — Weather Store ver5 (2026.08.27)

ver4에서 여러 페이지로 나눈 날씨 애플리케이션에 Pinia Store를 적용해 화면 간에 공유되는 설정을 관리하도록 구성한 구현

ver3와 ver4에서는 상태를 부모가 소유하고 props와 emits로 전달했다면, ver5는 어떤 상태가 특정 화면에 속하지 않고 앱 전체에 속하는지 구분하는 데 집중 props로 전달하는 방법과 Store로 공유하는 방법을 비교하며 상태의 소유 위치를 결정

## 1. 날씨 단위 Store 작성 — configStore.js

Action:
단위를 저장하는 unit을 state로 정의하고 초기값을 celsius로 지정 현재 단위에 맞는 기호를 반환하는 unitSymbol과 화면에 표시할 이름을 반환하는 unitLabel을 getters로 정의 celsius와 fahrenheit를 전환하는 toggleUnit을 action으로 정의 Store 식별자는 use + 파일명 + Store 규칙에 따라 useConfigStore로 작성

Why:
defineStore를 Option 형태로 작성하는 방법과 setup 함수 형태로 작성하는 방법을 비교 setup 형태로 작성하면 ref가 state, computed가 getters, 일반 함수가 actions에 대응되므로 ver2부터 사용해 온 Composition API 문법을 그대로 쓸 수 있다고 판단 unitSymbol을 각 화면에서 조건문으로 직접 만들지 않고 getter로 정의하면 기호 표기를 바꿀 때 Store 한 곳만 수정하면 되므로 표시 규칙을 Store가 책임지도록 구성 unit 값을 컴포넌트에서 직접 변경하지 않고 toggleUnit action을 통해서만 바꾸도록 하여 상태가 바뀌는 경로를 한 곳으로 제한

## 2. 단위 변경 UI 작성 — UnitToggler.vue

Action:
현재 단위를 표시하는 영역과 단위를 전환하는 버튼으로 구성 부모로부터 props를 받지 않고 useConfigStore로 Store를 직접 구독해 unitLabel을 표시 버튼 클릭 시 Store의 toggleUnit action을 직접 호출

Why:
단위 상태를 App이 소유하고 props와 emits로 UnitToggler에 전달하는 방법과 Store를 직접 구독하는 방법을 비교 단위는 UnitToggler에서 변경되지만 실제로 사용하는 곳은 대시보드와 상세와 순위 화면이므로, App이 소유하면 App이 자신은 쓰지도 않는 값을 들고 RouterView 아래로 계속 전달해야 하는 구조가 됨 Store가 소유하면 값을 쓰는 컴포넌트가 각자 구독하면 되므로 중간 단계를 거치지 않아도 된다고 판단 ver3에서 정한 단방향 흐름과 어긋나 보이지만, 상태의 소유자가 부모 Component에서 Store로 바뀐 것이므로 값을 바꾸는 경로가 action 하나로 제한된다는 원칙은 그대로 유지

## 3. Navigation Bar 옆 배치 — App_ver5.vue

Action:
ver4의 내비게이션 바를 좌측 영역과 우측 영역으로 나누고, 좌측에는 브랜드와 메뉴를 우측에는 UnitToggler를 배치 App_ver5.vue는 UnitToggler를 화면에 놓기만 하고 단위와 관련된 상태나 함수는 갖지 않도록 구성

Why:
UnitToggler를 각 View 안에 배치하는 방법과 App의 내비게이션 바에 배치하는 방법을 비교 단위 설정은 특정 화면의 기능이 아니라 앱 전체에 적용되는 설정이므로, 화면이 바뀌어도 사라지지 않는 위치인 내비게이션 바가 적절하다고 판단 각 View에 배치하면 화면마다 같은 UI를 반복해서 넣어야 하고, 화면을 이동할 때마다 컴포넌트가 새로 생성되지만 Store의 값은 유지되므로 표시와 상태가 분리되는 구조가 됨 App이 UnitToggler를 배치만 하고 상태를 알지 못해도 동작한다는 점에서, Store를 사용하면 부모가 자식의 관심사를 몰라도 된다는 점을 확인

## 4. 메인과 상세 날씨에 단위 적용

Action:
WeatherCard에서 configStore를 구독하고 city.temp를 현재 단위로 변환하는 displayTemp Computed를 작성해 기온과 단위 기호를 함께 출력 WeatherDetailView에서는 기온과 체감 온도 두 곳에 변환이 필요하므로 변환 함수를 한 번 작성하고 두 개의 Computed에서 사용 WeatherRankView의 순위 목록과 요약에도 동일한 변환을 적용 Mock Data의 원본 값은 섭씨 숫자 그대로 유지하고 변환 결과는 화면에 표시할 때만 사용

Why:
Store의 toggleUnit에서 Mock Data의 값을 직접 화씨로 바꾸는 방법과 원본은 두고 표시할 때만 변환하는 방법을 비교 변환식에 Math.round가 포함되어 있어 원본을 직접 변경하면 단위를 여러 번 전환할 때 반올림 오차가 누적되어 원래 값으로 돌아오지 않음 원본을 유지하고 파생된 값만 화면에 표시하면 몇 번을 전환해도 섭씨 값은 항상 동일하므로, ver2에서 원본 배열을 수정하지 않고 computed로 파생시킨 것과 같은 기준을 적용 변환 코드가 카드와 상세와 순위 화면에 비슷한 형태로 반복되는데, 이 부분은 Composable로 묶어 해결할 수 있으나 이번 과제 범위에서는 제외

## 5. 본인만의 추가 Store — favoriteStore.js

Action:
즐겨찾기한 도시 id 목록을 관리하는 favoriteStore를 별도 파일로 추가 favoriteIds를 state로, 개수를 반환하는 favoriteCount와 특정 도시가 즐겨찾기인지 판단하는 isFavorite을 getters로, 추가와 해제를 처리하는 toggleFavorite을 action으로 정의 WeatherCard에 즐겨찾기 버튼을 추가하고 WeatherDetailView에도 동일한 기능을 배치 WeatherHomeView에는 즐겨찾기만 보기 필터를 추가하고 즐겨찾기 개수 변화를 감지하는 watch를 작성

Why:
configStore에 즐겨찾기 관련 항목을 추가하는 방법과 별도 Store로 분리하는 방법을 비교 단위 설정과 즐겨찾기는 함께 변경되지 않고 사용하는 화면도 다르기 때문에, 하나의 Store에 모으면 서로 관계없는 값이 섞여 어떤 화면이 무엇을 사용하는지 파악하기 어려워진다고 판단 isFavorite은 도시 id를 인자로 받아야 하므로 값이 아닌 함수를 반환하는 getter로 작성했으며, 이 경우 결과가 Caching되지 않고 호출할 때마다 실행된다는 점을 확인 Store의 state도 반응형이므로 화면의 ref와 동일하게 watch로 감시할 수 있다는 점을 확인

## 정리 (ver5)

이번 실습에서는 Pinia를 사용해 여러 화면이 공유하는 설정을 Component 계층과 무관한 전역 Store에서 관리 ver3와 ver4가 상태를 부모가 소유하고 props와 emits로 전달하는 구조였다면, ver5는 어떤 상태가 화면에 속하고 어떤 상태가 앱 전체에 속하는지 구분하는 실습 선택된 도시처럼 한 화면 안에서만 의미가 있는 값은 여전히 부모가 소유하고 emits로 요청받도록 두고, 단위 설정과 즐겨찾기처럼 여러 화면이 함께 쓰는 값은 Store가 소유하도록 구분 Store를 사용하면 값을 쓰는 컴포넌트가 직접 구독하므로 중간 Component가 자신은 사용하지도 않는 값을 전달하는 과정이 사라진다는 점을 확인 단위를 전환할 때 원본 데이터를 바꾸지 않고 표시할 때만 변환한 부분에서, 원본은 유지하고 파생된 값만 화면에 사용한다는 기준이 ver2부터 ver5까지 동일하게 적용된다는 점을 확인
