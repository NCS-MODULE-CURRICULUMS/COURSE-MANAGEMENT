# 원격 조사 실습용 «현행 시스템» 서버
#
# 훈련생 PC 에는 아무것도 깔지 않는다. 강사 PC 에서 이 서버들을 올려 두면
# 훈련생은 Windows 에 기본으로 들어 있는 ssh 로 들어와 조사한다.
#
# 바탕 이미지는 아직 지원되는 것으로 고른다 - 지원이 끝난 배포판은
# apt 저장소가 사라져 패키지를 받을 수 없다(bullseye 에서 겪었다).
#
# 조사에 필요한 것만 넣는다 — ssh 서버, 프로세스·네트워크 확인 도구,
# 그리고 그 환경의 DB 클라이언트.
ARG BASE=tomcat:8.5-jdk8-temurin-jammy
FROM ${BASE}

ARG EXTRA=""
ARG START="true"
ENV START=${START}

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      openssh-server procps iproute2 net-tools less ${EXTRA} \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /run/sshd \
 && useradd -m -s /bin/bash survey \
 && echo 'survey:ncs2026' | chpasswd \
 && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

# 응용 서버를 뒤로 띄우고 ssh 를 앞에서 돌린다
CMD ["/bin/sh", "-c", "$START >/tmp/app.log 2>&1 & exec /usr/sbin/sshd -D -e"]
