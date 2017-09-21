FROM base/archlinux
RUN pacman -Syu --noconfirm python python-pip
RUN pip install pymongo flask
EXPOSE 80
ENV FLASK_ENV PCS
# set working directory
WORKDIR /app
ADD . /app
CMD python app.py
