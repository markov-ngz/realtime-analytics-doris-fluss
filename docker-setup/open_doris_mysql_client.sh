docker run --rm -it \
  --network quickstart-fluss-doris \
  mysql@sha256:8fb11c38b3551e22d50adbb688f027f8ff4ea2d2445aa277c1cc97b4af85ec54 \
  mysql -h fe -P 9030 -u root