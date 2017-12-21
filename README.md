# Nanum; A Korean community for sharing knowledge

## About
API Link: https://siwon.me <br>
Gitbook Link: https://suhjohn.gitbooks.io/nanum-api/content/ <br>
Website Link: To Be Posted

Nanum은 미국의 지식 공유 SNS Quora에서 영감을 받아 시작하게된 프로젝트입니다.
해당 Repository는 API 서버의 소스코드입니다.
 
## 팀원 
김경훈 https://github.com/namu617

서상원 https://github.com/suhjohn

이시원 https://github.com/2siwon

# Service Stack
## Backend Framework
#### Django
Client 와 주고받을 수 있는 API에 Django Rest Framework를 사용했습니다. 


## 서비스 호스팅 / 배포 & 오토 스케일링
#### AWS - ElasticBeanstalk, S3

서비스는 스케일링이 가능하도록 AWS ElasticBeanstalk을 사용해서 배포하였으며, 
자연스럽게 정적 컨텐츠는 S3를 이용했습니다. 

## 데이터베이스
#### AWS RDS(Postgresql)

Django와 가장 궁합이 잘 맞는 Postgre를 DB로 사용하였습니다. local, dev환경에서는
각자 .config_secret에 정의해놓은 로컬 postgre를, 배포시에는 AWS의 RDS를 사용합니다.

## Rich-Text Editor
#### Quill JS

Nanum은 Medium과 Brunch와 같이 글을 쓰는 분들이 편하고 아름다운 경험을 할 수
있도록 Quill JS를 이용했습니다. CKEditor, Froala와 같이 Quill JS는 
다양한 종류의 텍스트 기능을 추가해주는 WYSIWYG 에디터입니다. 오픈소스이기 때문에 
향후 실 서비스로서 확장시에도 문제가 없도록 처리하였습니다. 

## 비동기처리 & Message Queue
#### Celery, RabbitMQ

'비밀번호 재설정 이메일을 전송하는 것'과 같이 시간이 많이 소요되는 작업을 비동기적으로 처리하기
위해서 Celery를 Worker로 사용하여 작업들을 처리하였고, Celery에 적합한 RabbitMQ를 Task Message들을
보관하고 Celery로 message를 넘겨주는 Broker로 사용했습니다.

현재는, RabbitMQ를 API 서버가 존재하는 같은 EC2 인스턴스에 Supervisor를 사용하여 작동시키고 있으나,
이는, 후에 서버를 재배포할 때 RabbitMQ가담아놓은 message queue들이 전부 삭제되는 문제점이 발생하므로,
elasticache라는 별도의 AWS 서비스에서 Redis를 Broker로 사용하도록 수정할 예정입니다.
 


## 운영
#### TravisCI

TravisCI를 통해 개인의 Forked Repository 에 push된 내용이 bug-free 한지를 확인하고,
Master로 Merge시 Test를 통과하는지 확인합니다. 

#### Sentry

Sentry를 통해 개발 단계에서부터 프론트엔드와의 협업에 있어서 일어나는 500 Server 에러들에 대해
팀원들에게 이메일로 해당 문제 내역이 발송되도록 설정해놓았습니다. 

# To be completed

## Feed / Notifications
#### GetStream.io
[getstream.io website](https://getstream.io/)

Twitter, Facebook 등에서 사용되는 것과 같은 제대로 된 Scaling이 가능한 Feed와 Notification 기능을 개발하기 위해서는
해당 분야의 많은 고급인력의 최소 몇 개월의 긴 개발 시간이 소요됩니다. 이를 해결하기 위해서, 유저가 서비스 내에서 취하는
다양한 액션들을 "actor(ex.김경훈이)", "verb(ex.좋아요를 눌렀다)", "object(ex.답변에)" 가 존재하는 하나의  "Activity"
로 저장해서 NoSQL 기반으로 되어 있는 getstream의 Cassandra를 이용하여 최적화되어 있는 DB에 저장을 해두고, 이를 후에, API로 서비스내로 fetch해와서,
서비스 내에서 유저에게 다양한 Feed와 Notification들을 줄 수 있도록 getstream.io의 서비스를 이용하고 있습니다.

* 해당 서비스는 월 300만 건 이상의 API activity 업데이트 까지는 무료로 제공됩니다.

## Search
#### Elasticsearch 

Text기반 애플리케이션 이기에 검색은 매우 중요한 기능입니다. 
현재 elasticsearch_dsl을 이용해 Django와 연동하는 작업에 구현 중에 있으며, 
AWS ECS 를 통한 배포 중입니다.  
