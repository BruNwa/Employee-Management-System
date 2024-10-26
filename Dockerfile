FROM debian:buster-slim


RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    dos2unix \
    netcat \
	bash \
    vim-tiny \
    openssh-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# SSH Configuration
RUN mkdir /var/run/sshd
RUN echo 'root:mthree' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/#Port 22/Port 22/' /etc/ssh/sshd_config


COPY requirements.txt .


RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .


RUN dos2unix /app/entrypoint.sh
RUN dos2unix /app/service_restart.sh
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/service_restart.sh


EXPOSE 8000
EXPOSE 5000
EXPOSE 5001
EXPOSE 22


ENTRYPOINT ["/app/entrypoint.sh"]