FROM base/archlinux
RUN pacman -Syu --noconfirm python mongodb python-pip
RUN pip install pymongo flask
EXPOSE 80
EXPOSE 27017
ENV FLASK_ENV PRODUCT
# set working directory
WORKDIR /app
ADD . /app
CMD python app.py
