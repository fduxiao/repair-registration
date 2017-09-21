FROM base/archlinux
RUN pacman -Syu --noconfirm mongodb
RUN mkdir -p /var/lib/mongodb/
EXPOSE 27017
CMD mongod --dbpath /var/lib/mongodb/ --logpath /var/log/mongodb.log
