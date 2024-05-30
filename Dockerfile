FROM gabrielalthaparro/log3r:1.1

WORKDIR /app

COPY . .

CMD ["waitress-serve", "--call", "index:deploy_server"]