---
layout: post
date: 2022.01.20
title: DAO, DTO, Entity
author: Hanlien
---

# DAO, DTO, Entity

> 출처 : [https://gmlwjd9405.github.io/2018/12/25/difference-dao-dto-entity.html](https://gmlwjd9405.github.io/2018/12/25/difference-dao-dto-entity.html) (heejeong Kwon님 - DAO, DTO, Entity class 차이)
> 

# 배경

안드로이드의 Github Search MVVM Sample을 보다가 이상한 점을 발견하였다.

다음은 Retrofit 작업 과정에서 Model Class를 나타낸 코드들이다.

- OwnerResponse

```kotlin
data class OwnerResponse(
	@SerializedName("login")
	val login: String,
	@SerializedName("avatar_url")
	val avatarUrl: String
)
```

- Owner

```kotlin
data class Owner(
	val login: String,
	val avatarUrl: String
)
```

여기까지 보았다면, 벌써 눈치챘을 수도 있다. **OwnerResponse와 Owner가 똑같지 않나???**

OwnerResponse도 login과 avatarUrl을 String형태로 받고 있고, Owner 또한 login과 avatarUrl을 String 형태를 띄고 있다. 궁금증은 뒤로한 채 밑에 Mapper코드를 보았다.

- Mapper

```kotlin
fun OwnerResponse.toEntity(): Owner {
	return Owner(
		login = this.login,
		avatarUrl = this.avatarUrl
	)
}
```

Mapper를 보면 더욱 당황할 수 밖에 없다. 그냥 OwnerResponse의 데이터를 Owner로 전달만 해주고 있다.(연결) 

여기서 먼저 생각나는 의문점은 이것이다.

<aside>
💡 OwnerResponse의 데이터를 가져와서 처리하면 되는게 아닌가? <br>
💡 저렇게 연결하면 무슨 의미가 있을까? <br>
💡 오히려 연결하는 작업 시간이 걸려 손해가 아닌가? <br>
💡 그만한 비용을 들일만큼 가치있는 일이기 때문인가? 

</aside>

&nbsp;

# DAO

- DAO는 Data Access Object의 줄임말로 한글로 번역하면, “**데이터 접근 객체**”이다. 말 그대로 데이터가 담긴 실제 DB에 접근하는 객체이다.
- 보통 서버에서 데이터 베이스에 접근하기 위해 사용하며, 데이터의 CRUD 작업을 담고 있다. (Android에서는 Room라이브러리를 사용할 때, 자주 썼던 것 같다.)

# DTO

- DTO는 Data Transfer Object로 “**데이터 전송 객체**”이다.
- 계층 간의 데이터 교환을 위한 객체로 따로 로직이 없고 getter와 setter만 있는 것이 가장 큰 특징이다.
- 하지만, DB에서 꺼낸 값을 저장하는 객체이므로 따로 setter작업이 필요없어 getter만 존재한다. (생성자에서의 setter만 존재한다.)
- toEntity 메소드를 통해 **Entity로 변환하는 과정을 따로 거친다.** (이 부분이 우리가 위에서 문제를 제기했던 부분이다!)

# Entity

- Entity는 실제 DB와 매칭될 Class를 의미한다.
- 가장 중요한 특징으로는 **최대한 외부에서 getter를 못하도록 내부에서 로직을 구현한다**는 점이다.

## Entity와 DTO를 분리하는 이유?

정의는 알았지만 아직 궁금증은 풀리지 않았다. 결국 똑같은 객체를 만들어 매핑해주는 작업이 왜 필요하는가이다.

1. **View와 DB 계층을 철저하게 나누기 위해서**이다.
2. DTO의 경우, View와 연결되어 있어 해당 클래스(Response / Request)에는 변경이 자주 일어난다. 만약, Entity와 DTO가 분리되지 않은 상태에서 변경이 일어난다면 영향을 받은 모든 클래스들을 수정해주어야 한다. 따라서, Entity와 DTO를 따로 분리함으로써 **수정 작업의 범위를 줄여 비용을 줄일 수 있다.**
3. Domain Model을 아무리 잘 설계해도 수정 작업이 필요할 때가 있다. 이때, **Domain Model을 수정하는 것은 모델링의 순수성을 깨트리고 Domain Model 객체를 망치는 작업**이 될 수 있다.

&nbsp;

<u>언제든지 지적은 환영합니다! 메일로 남겨주세요.</u>
hschoi5542@gmail.com

[back](../android_main)