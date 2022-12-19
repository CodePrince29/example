ssh root@staging.sga-qa.agilekoding.com "pg_dump -U db_user_sga -d sga -h localhost -C --column-inserts" >> sga_backup_QA_04-06-2019_new.sql

# deploy user password: deploy123

# Updated Branch prod on new_origin.

ssh root@sga.frigorificosantander.mx "pg_dump -U db_user_sga -d sga -h localhost -C --column-inserts" >> sga_backup_29-08-2019_server.sql

password:arkasoftwares

dump tp database:-   psql -U postgres sga < /home/pallavi/Python/Working/sga/sga_backup_05-08-2019_server.sql



download from server :

scp root@sga.frigorificosantander.mx:/root/sga_backup_20190517.bak  /home/pallavi/Document

scp root@sga.frigorificosantander.mx:/sga  /home/pallavi/Document


psql sga -c "GRANT ALL ON ALL TABLES IN SCHEMA public to db_user_sga;"
psql sga -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to db_user_sga;"
psql sga -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to db_user_sga;"


scp deploy@sga.frigorificosantander.mx:/sga  /home/pallavi/Document

find . -path "*" -not -name "static/*" -delete

Error fatal: unable to access 'https://git.agilekoding.com/frigorificos/sga.git/': server certificate verification failed. CAfile: /etc/ssl/certs/ca-certificates.crt CRLfile: none:-

Solution: export GIT_SSL_NO_VERIFY=1

Git Agilekoding:
manoj.datt@arkasoftwares.com
Manoj@123

Time Doctor Login:
email: pallavi.sharma@arkasoftwares.com
password: pallaviarka

SGA Admin:

URL: https://sga.frigorificosantander.mx
Username: SGA_Admin_Prod
Password: Pr0ducc10n76===

Local credentials:
username: sga_admin
pass: sga@123$


To get an overview about how much space is taken by what database, call:

SELECT
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
    FROM pg_database;
    
To get more details, call:

SELECT
   relname as "Table",
   pg_size_pretty(pg_total_relation_size(relid)) As "Size",
   pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as "External Size"
   FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;


Pallet 1

{"Folio":"1249","Lotecte":"501","LOTETar":"FS6124","CLIENTE":"GGV_TEST_CUSTOMER","KGTotal":"200.0","CJTotal":"20.0","FCad":"2021-06-30","palet_id":"6855","confirmation":"4873","client_id":"53","product_id":"922"}

Pallet 2

{"Folio":"1249","Lotecte":"501","LOTETar":"FS6125","CLIENTE":"GGV_TEST_CUSTOMER","KGTotal":"200.0","CJTotal":"20.0","FCad":"2021-06-30","palet_id":"6856","confirmation":"4873","client_id":"53","product_id":"922"}

Pallet 3

{"Folio":"1249","Lotecte":"501","LOTETar":"FS6126","CLIENTE":"GGV_TEST_CUSTOMER","KGTotal":"200.0","CJTotal":"20.0","FCad":"2021-06-30","palet_id":"6857","confirmation":"4873","client_id":"53","product_id":"922"}

Pallet 4

{"Folio":"1249","Lotecte":"501","LOTETar":"FS6127","CLIENTE":"GGV_TEST_CUSTOMER","KGTotal":"200.0","CJTotal":"20.0","FCad":"2021-06-30","palet_id":"6858","confirmation":"4873","client_id":"53","product_id":"922"}

Pallet 5

{"Folio":"1249","Lotecte":"501","LOTETar":"FS6128","CLIENTE":"GGV_TEST_CUSTOMER","KGTotal":"200.0","CJTotal":"20.0","FCad":"2021-06-30","palet_id":"6859","confirmation":"4873","client_id":"53","product_id":"922"}