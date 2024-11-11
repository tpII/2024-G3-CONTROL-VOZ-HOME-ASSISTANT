Comando para buildear la imagen (parados en la carpeta rails-server):

`docker build -t rails-server .`

Comando para levantar el sv:

`alias run_docker='docker run -it rails-server --env-file=.env'`