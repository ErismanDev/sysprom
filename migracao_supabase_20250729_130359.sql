-- ========================================
-- MIGRAÇÃO PARA SUPABASE
-- Gerado em: 29/07/2025 13:03:59
-- ========================================

-- Desabilitar triggers temporariamente
SET session_replication_role = replica;

-- ========================================
-- INSERÇÃO DE USUÁRIOS
-- ========================================

INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1581, 'pbkdf2_sha256$1000000$LjhayjGYaxVoPrxr1WNAys$h4ynY647h3zZsOpLGSXKh62/24320MU0vABUUwvWe6Q=', '2025-07-29T12:07:45.829292+00:00', true, 'erisman', '', '', 'erisman@example.com', true, true, '2025-07-25T16:04:28.708581+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1582, 'pbkdf2_sha256$1000000$2lbSLK1XTXhv5i6r4WGhte$MNha1SSP3ZMLi6JD8sr0VyRG7uGK4eeSXPwTNgI+Rp4=', NULL, false, 'teste_permissoes', 'Usuário', 'Teste', 'teste@teste.com', false, true, '2025-07-28T11:33:51.124736+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1583, 'pbkdf2_sha256$1000000$gAKrUTno2PlQRYvQAUCkW0$LY5ZFG6Cf4D4ifyegcp/cB5U4YRMQJ/hbjB+B+MweXE=', '2025-07-29T11:42:05.442836+00:00', true, 'manzin', '', '', 'sgterisman@gmail.com', true, true, '2025-07-29T11:31:26.515145+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1110, 'pbkdf2_sha256$1000000$XLyehOt0PPygt1Y7xPEIFo$l2VN3VkI5L3PsB/dvOTimccoXe1KiABut0aiqVuhEdQ=', '2025-07-28T13:26:03.361617+00:00', false, '49008382334', 'José', 'ERISMAN de Sousa', 'militar_085367-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:02.165927+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1090, 'pbkdf2_sha256$1000000$7DgvjSoeMMhRHrDqU1j1ok$UMzE+ZyCIn7nN3f4+9pl4Lv8kDmwb1hlScnNzr+qrq4=', '2025-07-29T11:46:08.252655+00:00', false, '35110465304', 'José', 'VELOSO Soares', 'josevellloso@yahoo.com.br', false, true, '2025-07-25T15:47:41.940501+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1092, 'pbkdf2_sha256$1000000$DvwE9FlLjoxQPSuYZrWpWI$hEmiOYb2sH74EPp4JXLpc6nmnzhstgLBbxI9oPkuPEE=', NULL, false, '36136794349', 'CLEMILTON', 'Aquino Almeida', 'clemiltonalmeida@hotmail.com', false, true, '2025-07-25T15:47:44.072015+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1094, 'pbkdf2_sha256$1000000$sUtPcszc40WXn3OpwoKlZY$MxpA+xT3FI9mplccwuCB4T/EuMhsYOoaFxMEEXZ8VEs=', NULL, false, '68178182300', 'EGÍDIO', 'Nóbrega de Carvalho LEITE', 'egidioncl@gmail.com', false, true, '2025-07-25T15:47:46.089103+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1091, 'pbkdf2_sha256$1000000$3Oy6WwdTGJs4i6BUuWvkKk$Ep3JmJGU5Sg4Cfq6FipGYWbCO4L4lJPUSKmDKj1iYGI=', NULL, false, '43698239353', 'EMÍDIO', 'José Medeiros de Oliveira', 'emidiomedeiros@hotmail.com', false, true, '2025-07-25T15:47:43.032025+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1095, 'pbkdf2_sha256$1000000$kGtEtG8RmiCJPaS1khB8hN$8PGVcMNATngSpOP7+7/NnPGUbDGZ9jG67gDepi4meJo=', NULL, false, '59036427304', 'Josué', 'Clementino de MOURA', 'militar_084166-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:47:47.072255+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1093, 'pbkdf2_sha256$1000000$e3y5VJbaqSsgpFmYuRe4JQ$jNgNT4X6MlfX7f4b1anxuZA3VxiZ1SSCa+p/xvIgKuE=', NULL, false, '70090459334', 'Vinicius', 'de CARVALHO LEAL', 'viniciusbombeiro@hotmail.com', false, true, '2025-07-25T15:47:45.072454+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1113, 'pbkdf2_sha256$1000000$QHRD1NUBvGXNjxYaC9ouU1$5MLX4hikN02n/7haolOYDCruHPEbSPuCnJ20OHTO918=', NULL, false, '30492491372', 'Chaga', 'MACHADO de Araújo', 'machado2019@hotmail.com', false, true, '2025-07-25T15:48:05.031141+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1112, 'pbkdf2_sha256$1000000$2Qshg8z1CUZfc5Q9OMsLAn$8GAxvfnHdxHjcAyEmt/fxTUM5hU5bdfOH/ZdLZZpXNU=', NULL, false, '45342580382', 'FLAUBERT', 'Rocha Vieira', 'sgtflaubert@gmail.com', false, true, '2025-07-25T15:48:04.070960+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1109, 'pbkdf2_sha256$1000000$hvywn45vHmKXXOetz5oyhk$JvVYx4Qe6gEzLGpyMqIWvO56E3A4aIrFNp4abnJs2i0=', NULL, false, '34230637349', 'Francisco', 'das Chagas TAVARES de Sousa', 'thavarys@hotmail.com', false, true, '2025-07-25T15:48:01.214798+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1114, 'pbkdf2_sha256$1000000$7CZQMwCeLHjdfl4ZYHggzL$udldtowojvjXxYy3bvwuiL/STaQ2yzLc13esc+6zNzg=', NULL, false, '34259597353', 'Francisco', 'de Assis COSTA SILVA', 'sgtcostabm@hotmail.com', false, true, '2025-07-25T15:48:05.989414+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1111, 'pbkdf2_sha256$1000000$TGQ5ZPEBCrPyNrl41HZAy3$TBZqQuB6vzGiWdzTL+lN8GsDv0JOqpit25wib/x7ECw=', NULL, false, '30699649315', 'NÉLIO', 'de Oliveira Cordeiro', 'neliooc@outlook.com', false, true, '2025-07-25T15:48:03.119880+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1102, 'pbkdf2_sha256$1000000$EgqMLyijNT9IOs9RTCnVTP$kkQXJ59+qrQg+XGzTy3H3zQEYk5Mk8bPsdcpuaHsvXg=', NULL, false, '43256007368', 'Airton', 'SANSÃO Sousa', 'airtonsansao@hotmail.com', false, true, '2025-07-25T15:47:54.337586+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1108, 'pbkdf2_sha256$1000000$BGW1wP2xD8cVQVFxDoHMXt$2tbwo5FnzzLen8Oq9YacT8r7j+OqBpZ5K0McoDZsTII=', NULL, false, '70417121334', 'ANA', 'CLÉIA Diniz dos Santos', 'cleia2006@hotmail.com', false, true, '2025-07-25T15:48:00.234060+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1107, 'pbkdf2_sha256$1000000$upEn8gn12Uzec8lPm9au88$TTWvtE/hXZarEAxvcUU91FsXGOUz9Ydc4eVuzEvLsgc=', NULL, false, '93104383391', 'EDILSON', 'Soares Lima', 'edilsonmil@yahoo.com.br', false, true, '2025-07-25T15:47:59.167137+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1106, 'pbkdf2_sha256$1000000$bWisJI1ZKMAcIw5kB9iyKJ$qVf2eHjYTrhAgZ3Z03/FJVvUaJq7S/rQYuVKPzzAO68=', NULL, false, '68933673334', 'ELISABETH', 'da Costa Aguiar Tavares', 'elisabet-aguiar@hotmai.com', false, true, '2025-07-25T15:47:58.218816+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1096, 'pbkdf2_sha256$1000000$m9sw22az9YGawmr8stLCri$XzFTVuiryXOqbnJ+xSdnBnGl2U7CiXfduupFrSV+I88=', NULL, false, '42857040300', 'FREDMAN', 'Wellington Lopes', 'fredmanw@gmail.com', false, true, '2025-07-25T15:47:48.038595+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1098, 'pbkdf2_sha256$1000000$KWN0vkudDbqswFAt1puJNR$XibTDbv843fWAWUBG0lySN3DzdQ0/gcJM8mH8lnsrV8=', NULL, false, '51731088353', 'Glécio', 'MENDES da Rocha', 'protemacequipamentos@gmail.com', false, true, '2025-07-25T15:47:49.971668+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1101, 'pbkdf2_sha256$1000000$OiGjBUZtNhiEQFPR5jAHWR$ljLtQeNwWn7FfFo7R4Ey0uOd43PXsSxDwqPDPyzrkF8=', NULL, false, '68037830306', 'Jean', 'SÉRGIO Gomes Melo', 'sergio_bombeiro@hotmail.com', false, true, '2025-07-25T15:47:53.333805+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1103, 'pbkdf2_sha256$1000000$czmnzOyDGTaVgvmpoOCzuu$SJ+LoEzIxzSz4x3ccAj6iz6YbD1wLRDozXIB92fZ88A=', NULL, false, '38211823268', 'Jullierme', 'CHRISTIAN Lima Vale', 'christianfirelogan666@gmail.com', false, true, '2025-07-25T15:47:55.341149+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1100, 'pbkdf2_sha256$1000000$8knBRYnCvB0hnvHTiPzZtk$bPpwtWE6mZafQMyQ5X8hbhzTvGodBBylpp+g9l5egpU=', NULL, false, '56621540310', 'Kelson', 'Fernando CASTELO Branco da Silva', 'kelsonfernandocbs@gmail.com', false, true, '2025-07-25T15:47:52.367590+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1099, 'pbkdf2_sha256$1000000$Zy4iJzh8wvbFiALsYsZSBS$dJl31yQ/UgNsxzOxfPCMBnYDJqe3JrN1vF6K8igipXo=', NULL, false, '39512835304', 'MARCELLO', 'Rubem Santos Bastos', 'mrsb193@hotmail.com', false, true, '2025-07-25T15:47:50.965395+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1105, 'pbkdf2_sha256$1000000$7cWQQQusumPXYgjOXOIiNi$QQAyuyOpSwL2i2Bvv+w0xDcgVRQVDAN5ukTUpyRiv6I=', NULL, false, '82992703320', 'NAJRA', 'Julite Moreira Nunes', 'najrajulitemn@hotmail.com', false, true, '2025-07-25T15:47:57.265871+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1104, 'pbkdf2_sha256$1000000$JwWObXepnY61xz7gjQeB5N$SYNQ6r5wv42wQugAk5/uFfVWeRsrtKqIhWayoxx/uO0=', NULL, false, '68775881349', 'RIVELINO', 'de Moura Silva', 'rivelino193@hotmail.com', false, true, '2025-07-25T15:47:56.307481+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1097, 'pbkdf2_sha256$1000000$SKSBWS5MsZWePF7wKf3f3F$mNRGE4WFx3qz4AJgLEooQdaGFF6hiyZ6ZtKdblof4SY=', NULL, false, '47898771320', 'SÁRVIO', 'Pereira de Sousa', 'sarviopereira@hotmail.com', false, true, '2025-07-25T15:47:49.004057+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1151, 'pbkdf2_sha256$1000000$Rp9Id8zFr5iBqlRbuwmpTF$Itp9aRNwFgNyP4F2cLt7XvG/dnsJ2/yIMOc+GHRP9GM=', NULL, false, '95180788315', 'BEATRIZ', 'Lustosa Alves', 'beatrizbm10@hotmail.com', false, true, '2025-07-25T15:48:43.022129+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1150, 'pbkdf2_sha256$1000000$nzdmrxmvfM3Xgn8yG3QuHP$q/tQwEtkv9jlmayfdkdMvfYQKlxxTEuAtildWTATrFA=', NULL, false, '51534665315', 'Eriberto', 'ARCOVERDE Soares da Costa', 'eriascosta@yahoo.com.br', false, true, '2025-07-25T15:48:42.054024+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1125, 'pbkdf2_sha256$1000000$ybGAls0oEGko8dHuA6ntzC$quSaeeYxgZBw5TLcJyBRGxbSohSWpVEoiYyLWwtNhIQ=', NULL, false, '34313940359', 'AGNALDO', 'Pinheiro dos Santos', 'agnaldogula@hotmail.com', false, true, '2025-07-25T15:48:17.539592+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1133, 'pbkdf2_sha256$1000000$YsEqpwSPHpwhn3NOmxHmlD$458d3NdUgQoBi9QsxvMAWnu0fOKOIb/g0AFUE4AAdHM=', NULL, false, '03590155302', 'Allisson', 'RANGEL Moura Muniz Martins', 'militar_323173-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:25.368296+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1145, 'pbkdf2_sha256$1000000$4rUvIbwSQCo4p9CcA7WGjR$uoYMvPknjj4iqWkSLC7rRGrlEBbGlqS+3tbUmaFx8T0=', NULL, false, '30636175391', 'Antonio', 'Carlos da Silva LIRA', 'militar_014175-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:37.188190+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1144, 'pbkdf2_sha256$1000000$KqJIVlC4k6ZZMlHgrHLx06$LWDFeue4W073DzNAzRLhHQWmPbReyuqHkYOWszszHIU=', NULL, false, '32736479300', 'Antônio', 'CARLOS do NASCIMENTO', 'tenentecarlosnascimento@gmail.com', false, true, '2025-07-25T15:48:36.187357+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1147, 'pbkdf2_sha256$1000000$ZGmEZX3NyNQdYxvs20E0TX$GaNe0bBPyAma8uJg5vAQbIyMkWCD+HIGOz/q7hAD3JY=', NULL, false, '47098350397', 'Antônio', 'LINHARES de Sousa Filho', 'tenentelinhares@hotmail.com', false, true, '2025-07-25T15:48:39.140331+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1118, 'pbkdf2_sha256$1000000$UmqDjF2U7J83dJEj7CRwGO$Ch5+m2NyxYCUcR+1/4vXyh9lhT6lY0423vFOWr4XyiE=', NULL, false, '35016337349', 'Arias', 'PINHO Lima', 'sargentopinhobm@hotmail.com', false, true, '2025-07-25T15:48:09.836297+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1136, 'pbkdf2_sha256$1000000$N1uhw5ZB2qBCzbfPWFKXOm$hnAMV/UW6LoJmM473SHkZtRXez8KFlQ/w15cH8wOJO8=', NULL, false, '00846985357', 'ARLINDO', 'Rodrigues de Mesquita Júnior', 'militar_323176-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:28.505648+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1122, 'pbkdf2_sha256$1000000$GqrkS0Y6bilQAUpXmwBAFr$cNKOKaIFb4lo1X7V0Qa5Zg3WJJjUaG4kkXaWKKdy+3I=', NULL, false, '71433341387', 'ARNALDO', 'Pereira de Vasconcelos', 'arnaldovasconcelos2011@hotmail.com', false, true, '2025-07-25T15:48:13.701549+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1135, 'pbkdf2_sha256$1000000$KbcfT0J2Uo511ukyQVsDVj$ciI27U2vOOztf1LF0HH5G6N0PmfP2WRCMIQfCb/xLUI=', NULL, false, '60031970303', 'Augusto', 'CÉSAR Pontes Coelho', 'militar_323175-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:27.445852+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1119, 'pbkdf2_sha256$1000000$lmJVDbS00J3fYoEDazdM8P$w+W8O7+e3TxqKlEkAXhYknZfdU+KPdB8UDpg3kZp0do=', NULL, false, '42127521315', 'DIÔGO', 'Martins Fonseca Neto', 'diogo.martinsfonsecaneto193@gmail.com', false, true, '2025-07-25T15:48:10.813348+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1120, 'pbkdf2_sha256$1000000$l0v2Jz4KSf0o2cNRef9SWK$Q5cCOuISKlrxZfEPIfO4QyUHSjJwiBFyQ34k/JdgWQc=', NULL, false, '34308873304', 'EVARISTO', 'Francisco Rodrigues', 'militar_014095-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:11.775007+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1139, 'pbkdf2_sha256$1000000$Bp5hPogbrJACdkqUOW2A28$gKsrUkD6PM6ot73b2i4xvvQLZuAfTkVSGda4VEzQlIY=', NULL, false, '02495300316', 'EVERTON', 'Almeida da Silva', 'evertonbmpi@gmail.com', false, true, '2025-07-25T15:48:31.373937+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1126, 'pbkdf2_sha256$1000000$3flEPOZtOb0vMmSREIq6oP$Y76nCY/yD2qEHzba5HCO0SzxM0895jlblkrkGy7iL6U=', NULL, false, '34006796315', 'Francisco', 'Nonato SANTOS SILVA', 'militar_013009-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:18.600470+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1140, 'pbkdf2_sha256$1000000$gZ1FfOoz9IA1AETaJlfryX$lKruwV7awcbkdoU6AyM7xCfQSLMIRy2M/j46lmGZ/9s=', NULL, false, '00319607313', 'IVAN', 'Ribeiro Feitosa', 'ivannessa@hotmail.com', false, true, '2025-07-25T15:48:32.341159+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1117, 'pbkdf2_sha256$1000000$SoClks2Bz4Q5L6nstIMmfp$T1H288+7TrSi/qybiWgwSnXjeAQ16qVNO26cWYtmcKs=', NULL, false, '42164923472', 'José', 'EPITÁCIO da Silva Filho', 'militar_013600-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:08.875011+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1132, 'pbkdf2_sha256$1000000$blKyJUjQPgPRkVtMCrv9YB$LX9qccut27aM2fcyAwoL6UV+9Tz9Uk9ssttjXMtXyUY=', NULL, false, '22777679304', 'José', 'Francisco Alves da VERA CRUZ', 'militar_014325-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:24.391917+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1127, 'pbkdf2_sha256$1000000$rQbeMnNDIZfCQyK9UfCPut$2ytzrrsQ+Z0d6wbKVglIrEX1ZqHtSJVHmY+9pWPDLL4=', NULL, false, '32791054391', 'JOSÉ', 'GOMES de Oliveira', 'tenentegomesoliveira@gmail.com', false, true, '2025-07-25T15:48:19.544898+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1128, 'pbkdf2_sha256$1000000$ShWjWvCEJ4wPi7VK0PZHya$7mQV5y0NhczPO7khhSfZ4KzkoXRU71Wxkx+G8Z6yVow=', NULL, false, '24097217372', 'José', 'LIMA FILHO', 'limafilhobombeiro@hotmail.com', false, true, '2025-07-25T15:48:20.519257+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1123, 'pbkdf2_sha256$1000000$Ot6pJ1gYCTfAvL3DX8bAkE$0olKVFZi8fb8qUNK6CA+qOiiMknZ91C1BYms1C8Nsoo=', NULL, false, '32757948334', 'José', 'NILTON da Costa', 'militar_014188-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:14.660634+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1138, 'pbkdf2_sha256$1000000$oiR41e07cV8d0KoDKeRfsN$kTaqnLVLFPKcvY1wHXbavrZ+qR2siGBCrDDzgIHJm2w=', NULL, false, '00695761307', 'JUAREZ', 'José de Sousa Júnior', 'juarezjunior003@gmail.com', false, true, '2025-07-25T15:48:30.425346+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1134, 'pbkdf2_sha256$1000000$WPQQ4DD4GhiMh9Rbm8WrvY$wcpO7VX1PlmJ7H8BOhPd/CLaYg+wGaSM0mvhRdYIu18=', NULL, false, '02678796361', 'LUCAS', 'XAVIER Vieira Lopes', 'lucasxavierbm@hotmail.com', false, true, '2025-07-25T15:48:26.340062+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1130, 'pbkdf2_sha256$1000000$fS4OdRppE71q4dK6OlPpbM$S7x9th2868ZHHko6CtXxeO6IFQhX+VPnzwpzT8M6AqI=', NULL, false, '00869684329', 'MARCOS', 'PAULO de Arêa Lira', 'militar_298731-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:22.450124+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1121, 'pbkdf2_sha256$1000000$l1lHazCnn5RF6twt9iobSI$GVWIC61xaU5JW90iuuS9vov5b17SzQdPm/S3Fp2507U=', NULL, false, '32734867320', 'MIGUEL', 'Rodrigues de Sousa', 'militar_014193-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:12.723137+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1124, 'pbkdf2_sha256$1000000$gP1nZSebPOoAIIjCHAl6nQ$L0KcHC70m/IxQOsMsYgRdMZM0T5Pwc1tKM0JAIj9HdY=', NULL, false, '35016329320', 'Pedro', 'CARDOSO da Silva Neto', 'militar_013021-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:16.265845+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1142, 'pbkdf2_sha256$1000000$veiRLDsF0vPs8mHuebisP2$wnG0f0h/Y9XsjC2losHD9annBuf6wPeQ2ztNQMedt2c=', NULL, false, '02403832308', 'PRYCILLA', 'Oliveira Garcia', 'militar_323172-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:34.247401+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1146, 'pbkdf2_sha256$1000000$bxab4LiqIjxDeTXmvP82TV$HgVqa7Ply0KGuqr9mRMU+GGr8aHAeazBhRkWA3daVmU=', NULL, false, '32736134320', 'Raimundo', 'DIAS da Silva Filho', 'gyvago@bol.com.br', false, true, '2025-07-25T15:48:38.170357+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1129, 'pbkdf2_sha256$1000000$NtZZB6fFb3L8qyFHj3WWP2$EV1TA/ySbbe2JEpUE/tsQ3/DviU6vkqlLolZ7qMqLiQ=', NULL, false, '24095060387', 'Raimundo', 'Nonato Mendes BATISTA', 'militar_014195-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:21.486941+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1148, 'pbkdf2_sha256$1000000$VzugHAamyVHZMp8IuNQFFP$7WXkMA0QLJ0dWGTfm8nDhAQj4S3EtLNdM4JpjOFmsSg=', NULL, false, '44422890344', 'Sebastião', 'DOMINGOS de Carvalho Filho', 'militar_015016-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:40.124844+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1131, 'pbkdf2_sha256$1000000$LydKkelj1EnLuia1bPnCGl$jcLZZPLagaNkBMpODbWjk/J4hoA1RW1vtk8iVyf/2LM=', NULL, false, '01809284309', 'Sérgio', 'Henrique Reis de ARAGÃO', 'militar_298348-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:23.410071+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1137, 'pbkdf2_sha256$1000000$mILRRe3LR329TcHXalkpqE$3osvllTKgTYgTgia/G6TBVh9svNlFG2DrhMCtCBlxBU=', NULL, false, '01363641360', 'Thompsom', 'THAUZER Rodrigues de Araújo', 'militar_323177-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:29.457613+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1141, 'pbkdf2_sha256$1000000$iZU83uPleqPhk9TlNdLrR7$gxTjNlS33ZX2bzrJ1++tPDMeM7hVwUfsO2HCcsax3I4=', NULL, false, '44702477315', 'WALBER', 'Meireles Pessoa Júnior', 'militar_323171-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:33.289226+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1116, 'pbkdf2_sha256$1000000$oAA0Wl45MBINvRYuh2SzmJ$nIyq70dhOo9MoPIteR4ioH8S2rMz9EwHf3KjfMCvybg=', NULL, false, '36161799391', 'WILLIAM', 'Borgéa Lima', 'militar_082771-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:07.925507+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1143, 'pbkdf2_sha256$1000000$nNdmZS6AMfzJ2Vr1QA5b4s$eWcf5I2fAPwEcp7Q5vX+saFBTekJ9Ur6vjcdYsREyfY=', NULL, false, '42127335368', 'WILSON', 'Alves Cardoso', 'militar_014197-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:35.234742+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1162, 'pbkdf2_sha256$1000000$YNvxtrhyC6mdZxBu6OYixR$TzT87ZgKDn09ACMB740JzE16Kdzb1m7jl+EaBk/XtmM=', NULL, false, '02893167314', 'ANALICE', 'Padilha de Almeida', 'analicepadilha@yahoo.com.br', false, true, '2025-07-25T15:48:54.687893+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1153, 'pbkdf2_sha256$1000000$bvfC9XCXj6Ze4IhrsbIABs$zWGptbgo53MevcdIEcR7tijLfc2rPI+LgCcGhALaUWA=', NULL, false, '34951970368', 'Antônio', 'CARLOS VIEIRA da Costa', 'ten.carlosvieira@gmail.com', false, true, '2025-07-25T15:48:45.024407+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1157, 'pbkdf2_sha256$1000000$h2SqHtlaUcUNCLkWCouDPA$q8GLCnHkD6kwwLyFWflUg/BieecByDDAvt3RDcMO8EQ=', NULL, false, '39775933315', 'Antônio', 'Luís DEOLINDO do Nascimento', 'bmdeolindo@ig.com.br', false, true, '2025-07-25T15:48:49.290476+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1180, 'pbkdf2_sha256$1000000$ILmfuEqhDnAIq3S1iSG5Vk$ck53BUCifXvAyGcadBFih7j1QvQsYhJpD6y0ukcov5I=', NULL, false, '42874300349', 'Antônio', 'SEVERIANO da Silva Filho', 'militar_014314-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:12.658878+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1155, 'pbkdf2_sha256$1000000$mGs2PVDpIdkcvNOiUmIZYP$RKRkN73v1PUfogmroRpczgbEgi8J+Qb4aoXSMZ5iBjw=', NULL, false, '41167236300', 'Antônio', 'Valdeci MARREIRO de Sousa', 'antonio.marreiros@cbm.pi.gov.br', false, true, '2025-07-25T15:48:47.154918+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1159, 'pbkdf2_sha256$1000000$QnTAM902JmEZr33LWwee7B$fajMPGdW9NYpz7BP++KqVkS5JlgMB86pFX1qVzLWC+k=', NULL, false, '34950451391', 'CARLOS', 'ANTONIO da Cruz Ferreira', 'militar_014103-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:51.367273+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1165, 'pbkdf2_sha256$1000000$VX4y63p3mudhSn30vpc6oP$LzTpLOtkzpit/LRp2W8r1Io7+c5FppD/10Vjqx9TWiw=', NULL, false, '96830190304', 'DAVID', 'de Oliveira FREITAS Filho', 'davidofilho@hotmail.com', false, true, '2025-07-25T15:48:57.689726+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1168, 'pbkdf2_sha256$1000000$DhC8PK5uK1pD3dYNzq2kHP$jZLtM1iiaGtQW637Cdn0Hc7B4w3Pai849uV72w//xS8=', NULL, false, '00357661311', 'FILIPE', 'LIMA Martins', 'filipemartins.adm@gmail.com', false, true, '2025-07-25T15:49:00.788609+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1156, 'pbkdf2_sha256$1000000$MGAShPLJSFXBZ940c7Limw$430rNe+OoeFWVp6wKWMIfVVyyoGgabQInVog4cL34DQ=', NULL, false, '45113912387', 'Francisco', 'Carlos DA CRUZ Silva', 'sgtbmdacruzpi@hotmail.com', false, true, '2025-07-25T15:48:48.239074+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1171, 'pbkdf2_sha256$1000000$BTggU6DW6ahwZrZv7Tx2R4$7E9f6TTNsnuFACI0t+jVhTv1e467BJiNAPIQsjbFe/Y=', NULL, false, '34771557349', 'Francisco', 'das Chagas ALVES da SILVA', 'socorrobranquinha@hotmail.com', false, true, '2025-07-25T15:49:03.809520+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1186, 'pbkdf2_sha256$1000000$IRw6JhjQa3ycBMwxfAnEgT$s8GUQMzwzs7ZtDuFjcicf9NxrpU1KJCaUgETQizXTGw=', NULL, false, '39829855368', 'Francisco', 'GILBERTO da Silva', 'gilbertosilvabombeiro@gmail.com', false, true, '2025-07-25T15:49:19.519566+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1185, 'pbkdf2_sha256$1000000$wODDwMdNt8GhytCLivvE2u$cb7uWLGq9HnViWKuABGu4hZSfy0MUgzHs1ooHX6J3tM=', NULL, false, '69302154300', 'Francisco', 'PIMENTEL dos Santos', 'pimentel.bm@hotmail.com', false, true, '2025-07-25T15:49:18.494815+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1166, 'pbkdf2_sha256$1000000$pt1ktsntv3Hu6WoXCwjEim$VxHiiMfkStuslonIrRTlcJj9eHYivTRZiNchgCUv+Sg=', NULL, false, '93441762304', 'GABRIEL', 'MENDES Rezende', 'gabriel_rezende82@hotmail.com', false, true, '2025-07-25T15:48:58.686500+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1161, 'pbkdf2_sha256$1000000$svlAhF6JiW0QuF6RRryjE5$24Mc+GhWz3qpBnZbL8SADarB8kPCgQ/P/VdIvK3w9GQ=', NULL, false, '50460536320', 'Gerardo', 'Santos GASPAR', 'gesanpar@gmail.com', false, true, '2025-07-25T15:48:53.637386+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1187, 'pbkdf2_sha256$1000000$tKjaHrISq4g9om2BlINgJq$LP22f+WHBB0eis+GO6imSjmwANNtgbiS0S7BPvZJ4OQ=', NULL, false, '83373225353', 'GILDETH', 'de Oliveira Viana', 'evita_515@hotmail.com', false, true, '2025-07-25T15:49:20.507353+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1154, 'pbkdf2_sha256$1000000$hAWR7e7CucVgBLXMXxjeyT$N80q9xrep/tySM4xC/ZIyLqkXBBAO5xBFTHrR3ArZL8=', NULL, false, '86332015420', 'HAMYLTON', 'Lemos e Silva', 'militar_108743-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:46.107572+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1178, 'pbkdf2_sha256$1000000$vq6X5ARLS0YntNavTgBPWT$amCmUVcOOO2jfI52EAGD7pzf7th7rHi86RTfKS3FgO0=', NULL, false, '84800992320', 'HÉLIDA', 'Márcia Oliveira de Moraes', 'hmom16@hotmail.com', false, true, '2025-07-25T15:49:10.707571+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1169, 'pbkdf2_sha256$1000000$zKBReazqsrEKixnxk0GS0q$kkPRp4DpjAr1Rsv0HCCLso1xHyhtP0lBiyMKN0a1Bh8=', NULL, false, '03747612300', 'HUMBERTO', 'DOUGLAS Coutinho Oliveira', 'militar_333663-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:01.836995+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1167, 'pbkdf2_sha256$1000000$GSKYRjhlTLe8UdZdLSLyzC$qDLOHxz2bP7q/3cVrI4qv6Z3S24TmTS/aRsxIf9pRbU=', NULL, false, '03813140300', 'ISAÍAS', 'Emanuel Alexandre Sales', 'militar_333661-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:59.723256+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1158, 'pbkdf2_sha256$1000000$PxLUvwHQh4xZuLjFCIdwau$T9/w3bPbOHzmK68aOZE4NdY0Jc5WRp6kkTivcNg037s=', NULL, false, '21738351300', 'JOÃO', 'de Deus BORGES de Carvalho', 'militar_012528-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:50.321197+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1175, 'pbkdf2_sha256$1000000$Tb7qw2DAVjL17pd0EdPsUD$TJPggNnnBX5H5ctGZ/6uvRHP36c36+iVvRgLmveVsw0=', NULL, false, '39453553387', 'José', 'AUGUSTO Soares da Cruz', 'militar_014083-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:07.771722+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1176, 'pbkdf2_sha256$1000000$AJPj0z5KQRAgcNZXbufqV9$AHSjRxvmODmEFqQsNadP0FC25eqwfJ0iF96GXwl4Dlc=', NULL, false, '28805690368', 'José', 'de Ribamar Itapirema BRASIL', 'militar_013015-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:08.767776+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1179, 'pbkdf2_sha256$1000000$Kme2En5BHnwJF3K2ohLpPr$czOpQCPVacCQwFYFHyQdESb/ZanCf/wEORCObXhgH5I=', NULL, false, '34983945334', 'José', 'dos Reis da Silva BRITO', 'gyvago@bol.com.br', false, true, '2025-07-25T15:49:11.672386+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1172, 'pbkdf2_sha256$1000000$AxRNIapbEft8n9wee6uRq4$7sZkG0Lat1UCiCpCHqSNb8cROmUZ5vVeCb4ZFysOPXg=', NULL, false, '34951920344', 'Luíz', 'GONZAGA Nonato de Sousa', 'luisgnonato@hotmail.com', false, true, '2025-07-25T15:49:04.786039+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1182, 'pbkdf2_sha256$1000000$xU7ZKHmOQ8tw4t3jNq73DC$K8rjqDDcvGvatxpxWsWnovJPlQuavvP1N+/CAJVMh4o=', NULL, false, '00663082323', 'Marcella', 'PRADO Albuquerque', 'militar_343824-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:14.617006+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1152, 'pbkdf2_sha256$1000000$iGriKNT9zHa7C6M9lKQKCo$ImdIeKTlF0fuVtu3pDKujfuo99WFL5Kzg1tVkTi7mGU=', NULL, false, '45117390300', 'MARCÍLIO', 'Bezerra dos Santos', 'ps8rbc@gmail.com', false, true, '2025-07-25T15:48:44.042982+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1160, 'pbkdf2_sha256$1000000$4OoGYtR1shVCRBlZdGe3H8$rigLW+UwR+7q10i8fQ7Z5qjF9/YGeUoisgL/Sn5zR38=', NULL, false, '35368020368', 'MILTON', 'do Nascimento Castro', 'militar_015343-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:52.605490+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1170, 'pbkdf2_sha256$1000000$bAjt5aJeaSKRwRzaBpnsSt$DGYpE6lHq7VRTrT0wxEVDqNP3BJf5YdirY56FPqwOGM=', NULL, false, '56622503320', 'ODAIR', 'José da Silva Santos', 'odairsantos193@hotmail.com', false, true, '2025-07-25T15:49:02.836421+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1177, 'pbkdf2_sha256$1000000$RIZ6nZtzFdyDixSDsg0ku9$kmDWTvkRpY3NNEh7ORcLv3dtmHwxsnZoZur4tdpW56c=', NULL, false, '21738939391', 'ORLANDO', 'de Sousa Silva', 'militar_012479-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:09.742456+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1173, 'pbkdf2_sha256$1000000$PBu0gzlWdHxfLoTFFmeSHu$Alqb5XzqawvL+1cJEHANN3QJmRVZsE8CnsFxal5/8fs=', NULL, false, '47419652368', 'PAULO', 'Henrique Araújo', 'militar_014194-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:05.789506+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1163, 'pbkdf2_sha256$1000000$nUH9udLRqhr8YNPnWeY7L2$+100KOSnVjTL8tSMnL9l+iB7wmTvYzhd8km3Nh24ui8=', NULL, false, '99438852387', 'PEDRO', 'BENTO Bezerra Neto', 'militar_333657-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:55.714949+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1181, 'pbkdf2_sha256$1000000$AKZITDv22VCZurSvLrHMZ9$CIoWc3wVyeDh1GGlH2qmsCcrMHIuZxq2NTsGN/zxWSA=', NULL, false, '00480582386', 'Rafael', 'MEDEIROS dos Reis', 'militar_343628-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:13.633816+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1188, 'pbkdf2_sha256$1000000$5UM4Apjew9zRVlmzkIwzs6$zzijyh7Y8/i2w3OYSr5DIptzSQYBgzEuHkDtN5FFTCI=', NULL, false, '74428063334', 'RICARDO', 'José dos Santos Filho', 'r18bm@hotmail.com', false, true, '2025-07-25T15:49:21.482278+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1184, 'pbkdf2_sha256$1000000$uxUYh2HjdYLVldb7iOqhtp$1zfycN4hZYOxmW6Fj01mNRmmSoyDoZmS9TjjgTqIUoY=', NULL, false, '04167705338', 'Rodollfo', 'OLIVEIRA de Jesus', 'militar_343630-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:17.464639+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1174, 'pbkdf2_sha256$1000000$o0iQSTy9KJmcQKU5NWOsPy$ukmYtFh/sRP+WNnSmYdDbddF2fEZ+aC3z6QomAWis3E=', NULL, false, '28726251353', 'SIDNEY', 'Viana da Silva', 'vianasilva1965@bol.com.br', false, true, '2025-07-25T15:49:06.791984+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1164, 'pbkdf2_sha256$1000000$5uihkqAfG65wyFSvuWqika$1xrUGHzEqgDhyl1S0iC3Lo4bQVRFmMwOCxRtLqzCFO8=', NULL, false, '02015731300', 'Vinícius', 'EDUARDO Santos Martins', 'militar_333658-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:48:56.706759+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1193, 'pbkdf2_sha256$1000000$fh60zIxgnDPXRgPvzrUMOV$3Y4X0eORc2kBhJa/jmhAmbpAk4OIlX/xBvT2ZwyQk2U=', NULL, false, '56634854300', 'AILTON', 'Santana Marinho', 'hotasm@hotmail.com', false, true, '2025-07-25T15:49:26.358071+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1192, 'pbkdf2_sha256$1000000$5gNvBWARJayVKEwyA3ksLX$/SgLZZfvB2Qwuf67nyMze2HCsqIoeN4mwilh4l+T1nk=', NULL, false, '42861578300', 'Carlos', 'ALBERTO Soares da Costa', 'betobm.1970@hotmail.com', false, true, '2025-07-25T15:49:25.387444+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1198, 'pbkdf2_sha256$1000000$ZFf9IZbHrxjzxZp1lzqyOA$xL3X2nPMsEyk6aaCTe0mWQ+IQTDaR1atYn4Y9xkwrHk=', NULL, false, '39454452304', 'ELISEU', 'Gomes de Melo', 'eliseugomes46@hotmail.com', false, true, '2025-07-25T15:49:31.238605+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1190, 'pbkdf2_sha256$1000000$vbpmo2GlSLEwyAGcRChczO$HQ/uRfRpsu2lw8+KOK0sTjhvht9zpNA8xqstbh0okjA=', NULL, false, '00423876392', 'Francisco', 'de Paula dos SANTOS', 'militar_351989-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:23.419805+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1194, 'pbkdf2_sha256$1000000$vQEMwp1lJKK5ccZbZVV93B$04zsYv0jCczDGI01PQdRTVIcEHwWF3BjaSCwa8Mv8tA=', NULL, false, '47007044387', 'Francisco', 'GILBERTO PIRES Teixeira', 'cbgilbertopires@yahoo.com.br', false, true, '2025-07-25T15:49:27.325364+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1197, 'pbkdf2_sha256$1000000$0By188YjGOErzkj2jBYLMT$ROYLrC0pdfiAeDbYHjzD3xZVmjbOLnXePF7fIGndcB0=', NULL, false, '49818635353', 'GILDETE', 'Freire dos Santos Carvalho', 'gildetbm@hotmail.com', false, true, '2025-07-25T15:49:30.257043+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1195, 'pbkdf2_sha256$1000000$9rSRy7nPlsLerpoJyCv649$RqDLeky41Od+6IMQ/h5EWV88i8Rvjci2jiE4xF30FBs=', NULL, false, '78036283387', 'Luís', 'de Morais NUNES', 'gyvago@bol.com.br', false, true, '2025-07-25T15:49:28.289850+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1191, 'pbkdf2_sha256$1000000$7LfTsk6nEY1IwfhydKvYFy$IHkTX8OVKwfGRao0TZ2DnQ7WJzpZij3clM1omkLrROk=', NULL, false, '76827038300', 'Maria', 'DAS DORES Oliveira Rodrigues Damasceno', 'dasdoresbm@hotmail.com', false, true, '2025-07-25T15:49:24.414106+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1196, 'pbkdf2_sha256$1000000$3T6xrPpoNn0zZFRcLF87Bm$H/fBSO6HfgGBoIo2WljcpvoNjyRuFzF5PYimpkZsm78=', NULL, false, '50420186387', 'SILVESTRE', 'Pereira da Silva Neto', 'silperneto@hotmail.com', false, true, '2025-07-25T15:49:29.270544+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1189, 'pbkdf2_sha256$1000000$1k4VD9HFtBlQy8ZBvRrRo0$BVFJcV9VXLmsviD1qv1XoIrWL+BQ2oKmVnHNtdEGY3o=', NULL, false, '03002967386', 'THIAGO', 'Lima CARVALHO', 'militar_351988-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:22.441471+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1210, 'pbkdf2_sha256$1000000$iSWqmJZWGRRXiFoSEs3NvU$DumjGkqhoFk/kf2WzMzZQbVKpGnzWAZE2SdPwiJbEWQ=', NULL, false, '70013438387', 'Charles', 'FRANCO de Oliveira Lopes', 'franco.charles@hotmail.com', false, true, '2025-07-25T15:49:42.988708+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1207, 'pbkdf2_sha256$1000000$gsfCVVRHvJPakFacWPuOmV$X5Glz84ye6cFkfh36ydpoUvVY5zPUSRKGJwHcT5D+6I=', NULL, false, '47436603353', 'CLÁCIO', 'Alves da Silva', 'militar_085413-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:40.082138+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1215, 'pbkdf2_sha256$1000000$4ToG5mpK4CshmKI3Wt6ebc$Kp5qtxhh8WKJM2JEwGhsAZ9TZl/sFR5gYRB6pIvaAJo=', NULL, false, '43972357320', 'DÁRIO', 'Nascimento', 'gyvago@bol.com.br', false, true, '2025-07-25T15:49:47.821452+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1223, 'pbkdf2_sha256$1000000$A9wDYgXV7QwSDK4n6hRQZ1$r2W1vJ6IUSfsGTuZH96+wckn7kMkz8n9x/WJgWhGmfQ=', NULL, false, '55356303300', 'DEOCLÉCIO', 'dos Santos Caldas', 'militar_079685-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:55.971456+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1214, 'pbkdf2_sha256$1000000$fcNbQwniST6Vvbe9WJjzeA$svNvukJfwNd+69Sep9nspdkU9qKSvkGZfGIyjKzZO/8=', NULL, false, '39786889304', 'Edivan', 'CONRADO da Silva', 'econrado1@hotmail.com', false, true, '2025-07-25T15:49:46.854411+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1203, 'pbkdf2_sha256$1000000$X7kewcAORZTGdxnOdRYJJc$zrfOHoeH7QzqHWTbOvM7/CxiK2XIFMnZ7UkX7/kGJ/g=', NULL, false, '41231775300', 'FLÁVIO', 'Gomes de Oliveira', 'flavio---gomes@hotmail.com', false, true, '2025-07-25T15:49:36.173861+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1200, 'pbkdf2_sha256$1000000$wT92qt2L88kvZZvrGHXJCQ$reKjF1OiS9AqZiFt2x4hQZ3RLdO2PjJUUr6zgwgFOk8=', NULL, false, '49857592368', 'Francisco', 'Carlos Mendes FRAZÃO', 'frazaobm@gmail.com', false, true, '2025-07-25T15:49:33.225092+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1209, 'pbkdf2_sha256$1000000$3YtUhAtvuGnIwjxVQuh6c3$pq+hGwy5aCh6KrHJFzkZKzvIXtgIGVfY7rSJnWMcK+w=', NULL, false, '53628055334', 'Francisco', 'da Cruz CARNEIRO', 'karneirobombeiros@hotmail.com', false, true, '2025-07-25T15:49:42.017551+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1206, 'pbkdf2_sha256$1000000$7gBTvzb7tg8D1rcMO7wu5N$qqpIMkQlvUlByg8ZSKOGYlW5Qwt9mrHguA6uKwhVN9Q=', NULL, false, '50453416349', 'Francisco', 'da Silva RIBEIRO', 'ribeirogse@hotmail.com', false, true, '2025-07-25T15:49:39.104572+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1220, 'pbkdf2_sha256$1000000$oyB0JApt5VLQQZfQ3LiWDs$rDwino0BMWBDMoG7sRM6CSRKVtxAVftqVX7yMiN0r6M=', NULL, false, '49019112368', 'Francisco', 'das Chagas DE MELO SANTOS', 'milrosardes@hotmail.com', false, true, '2025-07-25T15:49:53.019888+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1204, 'pbkdf2_sha256$1000000$7GgOlh7zX2rHUFGFT8X13B$ctYpycJWVNsqZPBPfjOSOb8XJJdTBvFo0nCiSbCp9A4=', NULL, false, '73055336372', 'Francisco', 'VALTER Pereira', 'franciscovalterp@gmail.com', false, true, '2025-07-25T15:49:37.158777+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1212, 'pbkdf2_sha256$1000000$0QxOzxdxJl1ISj0ANHWILg$B2ecEWxQ48UAt/htnWBLF1MFN0SQRJ2DMT7hsUgVNgo=', NULL, false, '15132925871', 'GIVALDO', 'Oliveira de Sousa', 'militar_085790-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:44.933477+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1216, 'pbkdf2_sha256$1000000$pDiQh6KQSykrLtDanKbPDR$WCIJYWsJinBNsHerT/RoZ6ZFzJJnjihmcS/4ybqC924=', NULL, false, '85483168372', 'JAIRO', 'Oliveira Figueiredo', 'viverbem.residence@hotmail.com', false, true, '2025-07-25T15:49:48.854254+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1205, 'pbkdf2_sha256$1000000$4WILK3QvOOsBYQyYbMIsMc$nW1SoU4E1LZ9NhIQObsZ1V5L41TrFVcrjo8PfFDLOUY=', NULL, false, '42875900315', 'JOSÉ', 'LUIZ Amaranes dos Santos', 'vivobem@hotmail.com', false, true, '2025-07-25T15:49:38.139242+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1225, 'pbkdf2_sha256$1000000$s4pArjryr2mIbx2qdLq0UK$TQLweQcyN9H2iPP4vQA0N1LyMDyrkAQ6V05cUTjknak=', NULL, false, '67831532315', 'José', 'Wilson Vieira RAMOS', 'valderice31@hotmail.com', false, true, '2025-07-25T15:49:57.917786+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1201, 'pbkdf2_sha256$1000000$i5RCkPN8FupeiAE0jPfnYs$6ZnorJWloB8YMBkHALCiOQiUfPBnJULaH3f73Ih+04s=', NULL, false, '57789924320', 'Juscelino', 'MAGALHÃES', 'juscelinomago@gmail.com', false, true, '2025-07-25T15:49:34.218134+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1202, 'pbkdf2_sha256$1000000$Xtq6SV2Rjl2seC9lcICSvd$1JrFX2VDPFEuv3Y9hOxL0axl5OqeWbVQznUEVBm4vlg=', NULL, false, '69682640300', 'MARCONE', 'Costa Alves', 'marconeresgate@yahoo.com.br', false, true, '2025-07-25T15:49:35.187797+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1224, 'pbkdf2_sha256$1000000$dx2f94ijzuQraB7vNh90OQ$pIAbZRaNygnQtRy+k6I+e6AYXlhhjW5IxDwH/NwNkPA=', NULL, false, '34930230306', 'Raimundo', 'Nonato DE CARVALHO', 'militar_013927-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:56.936638+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1213, 'pbkdf2_sha256$1000000$ks17eptydxkcjmmYavcbTu$u8PLAksmTPsDdLqwXibE/B20vcOQD+lJxlZYNZ7X2Us=', NULL, false, '45173893320', 'Raimundo', 'RODRIGUES Neto', 'militar_084356-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:45.889032+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1208, 'pbkdf2_sha256$1000000$Wbp2MGFMNukw9Xk1HkSAoZ$FVOwUe6GyM57iFpxyLRvtj70VpTRrLx354qp/BRR1F4=', NULL, false, '41163923320', 'ROBERT', 'Costa Santos', 'robertsgtbm@hotmal.com', false, true, '2025-07-25T15:49:41.048773+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1222, 'pbkdf2_sha256$1000000$E2eYDl6wtOHalhDs9jLOAq$Jgt/OXQp1laeVAwkB/tpEM1fT5SnmncgcoQIkFib4dE=', NULL, false, '86404458187', 'Ronielton', 'Marques do AMARAL', 'cbamaral2009@hotmail.com', false, true, '2025-07-25T15:49:55.005818+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1219, 'pbkdf2_sha256$1000000$yIfgN2VLUXc180JHSEP5bD$lWib9MC2rUrjf4+HxFBIznjZf8J5ioCEV3FKiefvbIE=', NULL, false, '62805207300', 'ROSIMAR', 'do Nascimento Granja', 'florbilica@hotmail.com', false, true, '2025-07-25T15:49:52.013950+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1211, 'pbkdf2_sha256$1000000$RFv3Ukmka8FYQia8qNDVO7$rScAsuy/l/X/QwQI7UODOCinMKvWxfsK/uOu56bMVeM=', NULL, false, '42918642304', 'SEBASTIÃO', 'Vieira Rodrigues', 'sgtbm.sebastiao@hotmail.com', false, true, '2025-07-25T15:49:43.953727+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1218, 'pbkdf2_sha256$1000000$CgvEbq5CAlbOx3GB4dGMGZ$em3JewJtfIeVlZ/mFougk3OPQcD0qNxjhUKdXA3GMcA=', NULL, false, '84520337372', 'STANLEY', 'Azevedo Fernando', 'stanley_gbs@hotmail.com', false, true, '2025-07-25T15:49:50.859249+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1217, 'pbkdf2_sha256$1000000$2urxJLnDyda0fiFMDF20zg$hAhvuQKWFfkfQ0nxOQ5jcmJ5NuqLvg1ylbo8b25xIqQ=', NULL, false, '76771385353', 'TUPINAMBA', 'Messias da Silva', 'tupinambamessias@hotmail.com', false, true, '2025-07-25T15:49:49.884917+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1221, 'pbkdf2_sha256$1000000$MYGLK1Z7Gt9N8dbNnTmgwQ$F6KUcfu55Yck4nen95pAsHJigQKG90RjF1i64igc2UU=', NULL, false, '53585925391', 'VIRLANE', 'Mendes Gama', 'semprelutadora@hotmail.com', false, true, '2025-07-25T15:49:54.000960+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1228, 'pbkdf2_sha256$1000000$kgR4obchPpvQcA7gVCIsa6$utY5mTL8yIUPB+H65NV9+fCERAR4RCqEbY7i2Wxskf8=', NULL, false, '40794350372', 'EIRES', 'dos Santos Lima', 'militar_015345-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:00.825507+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1227, 'pbkdf2_sha256$1000000$yhLslJm99cGAAMtPLPGYPL$uFCENdSs9PYMvfRvaKu0RfinL4VnpTtyjfsD4GM2KFY=', NULL, false, '36142085320', 'Genival', 'ARAÚJO da Silva', 'militar_014625-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:59.855101+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1242, 'pbkdf2_sha256$1000000$8puQRZBZ639CVjy8nLKx2p$tN0f08XEni0zBfVeeH1rGClQyVM6Lc7eA+WnAP6fo8k=', NULL, false, '43949983368', 'ANTÔNIO', 'CARLOS de Sousa Santos', 'militar_015331-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:15.036386+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1238, 'pbkdf2_sha256$1000000$XhI6qCPwlL8mT8XTEB6Wh0$uHzAS1hjaKF+uhz387lgtSnFods5BTG2r9qr7UUbr2s=', NULL, false, '80160026334', 'AVA', 'DANYELLA Macedo Silva', 'avadan3678@gmail.com', false, true, '2025-07-25T15:50:11.191340+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1235, 'pbkdf2_sha256$1000000$W2vSqAiBCJrzHi2iIqfqPF$lOCqD/2yxB4p+s6dMJysyGCYCRIRtKgk47U7ugOJsq4=', NULL, false, '46262407391', 'Carlos', 'Alberto da COSTA', 'carloscosta579@gmail.com', false, true, '2025-07-25T15:50:07.918431+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1236, 'pbkdf2_sha256$1000000$HiK7yXXiZBoBQ4fdbCnYbi$3YHZ5QY1V1beU1qIMg2Xqz/KlaekJslYoScKprT4NC8=', NULL, false, '34304916300', 'Carlos', 'Alberto da SILVA', 'militar_015039-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:09.122278+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1251, 'pbkdf2_sha256$1000000$vuIfAdg0dhBixduzECQqDE$MXYwiqZxYhDn30DAcYhWSCiGKe75J4uL3jequl+LlRw=', NULL, false, '74721100353', 'CÉSAR', 'Augusto Madeira Monteiro Junior', 'juniortriballes@hotmail.com', false, true, '2025-07-25T15:50:24.842504+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1230, 'pbkdf2_sha256$1000000$DTnRORfKPrKXUTYmbj88co$VXuv8ErvTAzP1irNy0WWCvUoaP/jKNttl8d+6oHXieE=', NULL, false, '51534150315', 'CLÁUDIO', 'Rodrigues MATOS', 'militar_085394-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:02.759692+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1231, 'pbkdf2_sha256$1000000$w51fqTHm0Uv5EkVouA9fKB$NoHq8jLBAleaA29/8H7XGOwW2g7Ohh8CPLcRb6ZzSmQ=', NULL, false, '48195618391', 'Derivaldo', 'Alves dos SANTOS', 'cbdsantosbombeiro@hotmail.com', false, true, '2025-07-25T15:50:03.719591+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1233, 'pbkdf2_sha256$1000000$vxjknclAT1V34s7AJTO0UW$OtcXP37HtJdBEhNeZcFp0rPVsyL3jCJmi1JmmEudbLU=', NULL, false, '49035851315', 'DEUSIVAN', 'Sousa Silva', 'militar_079853-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:05.680572+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1249, 'pbkdf2_sha256$1000000$G91efOgnmq3P11hj6HbnEp$IRT62CHGLCn7xDXEBjOc4meK2SHi6Y3rqLQTgWSn1z8=', NULL, false, '28735447320', 'Edmilson', 'de AZEVEDO do Nascimento', 'militar_083458-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:22.839815+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1254, 'pbkdf2_sha256$1000000$SXG2RC43Fc3pbwTkROKAlP$U+mCf8MePVf8TAp66fn9jpVCIm3lY6eHwMiC33sf3d0=', NULL, false, '91813395349', 'ELDEAN', 'Silva Lima', 'eldeanlima@hotmail.com', false, true, '2025-07-25T15:50:27.786132+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1262, 'pbkdf2_sha256$1000000$kU2wgFPt9yAqrgXRapC9On$TO4y1YreUUhme0cq1sj8vlAWpy7ioBpQiNRiO2eobQI=', NULL, false, '00755217330', 'ÉRICO', 'Vinícius Mendes da Silva', 'ericovinnis@yahoo.com.br', false, true, '2025-07-25T15:50:35.507643+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1252, 'pbkdf2_sha256$1000000$3fEpHRijScKcSGruQlgCj7$Je87RKkBzhRLbEtlq/20g7izy+yCAlkRFIYlun8/RuE=', NULL, false, '00177587342', 'FÁBIO', 'dos Santos Costa', 'sdbmflavio@hotmail.com', false, true, '2025-07-25T15:50:25.826634+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1234, 'pbkdf2_sha256$1000000$hfNxedsKCFw4FwLDWVBq9x$vh65vrAQ5illryaQmK5frCu2/yNmmmlIL3pP8Iu6zNM=', NULL, false, '35283440320', 'Francisco', 'CARLOS Carvalho Pereira', 'militar_014638-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:06.724266+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1245, 'pbkdf2_sha256$1000000$yHYUkKtUwnyJYZQ9vWQVIU$OdPzR8BqUXCj/Up26LT+q41HQGXvqdRmCdIruk4GvoU=', NULL, false, '44387318104', 'Francisco', 'das Chagas LIMA', 'amilazid@hotmail.com', false, true, '2025-07-25T15:50:18.856323+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1237, 'pbkdf2_sha256$1000000$2yJiA1Cltj7ppmm6q7KGm3$PlatBEwTPrlBmpCIVjK0+oxXx0FbBh9Pn0AOb2W/5oQ=', NULL, false, '11594580812', 'FRANCISCO', 'MARQUES de Oliveira', 'marques1237@hotmail.com', false, true, '2025-07-25T15:50:10.221527+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1261, 'pbkdf2_sha256$1000000$aVS1qe7m9fjXNL0Rp5E0MA$8ls7dIfuE+9ZI8c/xzQxwymqn9HrWg53KxAXkMxghlM=', NULL, false, '95825312315', 'Francisco', 'SOUSA JÚNIOR', 'sousajunior-historia@hotmail.com', false, true, '2025-07-25T15:50:34.533049+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1239, 'pbkdf2_sha256$1000000$6gWeH5jj2LJZvkTTe62dTx$KtSMYUQgLcBocma/WvoyeR4AzXQNPayjUwzZE1qHYi0=', NULL, false, '78834490363', 'GEAN', 'Carlos Barbosa Furtado', 'sdbmgean@yahoo.com.br', false, true, '2025-07-25T15:50:12.154181+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1255, 'pbkdf2_sha256$1000000$Z3CxZJn0w19okqTkmKMgjP$NcNOi6/8/AvgdSUyieui2jyTpNqgHX4P29Qlsbhovgg=', NULL, false, '65225600387', 'GENILTON', 'Wellington de Sousa', 'gntsousa@hotmail.com', false, true, '2025-07-25T15:50:28.739861+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1243, 'pbkdf2_sha256$1000000$QbyN01LZtJiuCw9PdvjwtK$rtku/aT4KKZ8r/xHYUSoUrbfk3VGC7N8/o9XbWsnLHQ=', NULL, false, '44632886300', 'GILMAR', 'Feitosa de Sousa', 'militar_015145-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:16.004483+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1229, 'pbkdf2_sha256$1000000$t80AnTqLdoWHg5C660Xrk1$ox9lkw3UVWbKlgA0b0fCjn6o6rjFh+MR6yBSAGnWn48=', NULL, false, '34929878349', 'HÉLIO', 'Antônio de Sousa Lima', 'militar_014148-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:01.793070+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1248, 'pbkdf2_sha256$1000000$yk11cFxpXBlLW4dSJWfHhk$4O8HEabwxgVPqf9XXm/YD8pZE3CHMweL7K6AbPUMzms=', NULL, false, '73516570334', 'JERRYSON', 'Martins dos Santos', 'jerrysonbidfilhos@gmail.com', false, true, '2025-07-25T15:50:21.840184+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1240, 'pbkdf2_sha256$1000000$AipN9JOeah3lSBEH6hsoUk$Zco2hSoUy6utKX5uWWt1y1+PMHD5fjY75OYI3wFpDoU=', NULL, false, '42123569372', 'João', 'Batista NERY de Sousa', 'bmnery@hotmail.com', false, true, '2025-07-25T15:50:13.109051+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1259, 'pbkdf2_sha256$1000000$Kx82LDmsrePXoyykkX3zzg$Fcem4RUnxlIj+TLNrnd5tgyZzNPr1W/tFf7fAFHHCc4=', NULL, false, '42859360387', 'João', 'de SOUSA Monteiro NETO', 'militar_015030-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:32.600373+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1244, 'pbkdf2_sha256$1000000$iBSF02h6GOqB7giNna4Cy5$pW5xhHhVyPp/Ql63abHCFNBz1JwogjiQYL/GJ/i2LUA=', NULL, false, '48155047334', 'José', 'FRAZÃO de Moura Filho', 'militar_082860-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:17.604121+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1253, 'pbkdf2_sha256$1000000$rS9AL7w9vfSytEC7d0CSNr$YzGv7hRZjR598vsqICyLzjDYmeQLGzArZmRrWggykEM=', NULL, false, '02610970323', 'KÁCIA', 'Lígia Silveira Linhares', 'kcialinhares@gmail.com', false, true, '2025-07-25T15:50:26.820362+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1258, 'pbkdf2_sha256$1000000$LkiqrbwwnZvaAoma6BAS0m$iLiKU3+aeba4mWbI0m0/qbCZsfw7AdqbKmj0JJP3L9o=', NULL, false, '00359881343', 'LUANA', 'Coutinho de Oliveira Caldas', 'luanacoutinho.oliveira@gmail.com', false, true, '2025-07-25T15:50:31.641997+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1241, 'pbkdf2_sha256$1000000$5eN14EFdPe9cJC4Cu1ODhK$sHblVFMfEXx8NWBpaxoU7DBuBUzCHSQgnuePZq9GAHs=', NULL, false, '57844127368', 'Luíz', 'Alves da Vera CRUZ', 'militar_085862-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:14.066357+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1256, 'pbkdf2_sha256$1000000$t8y1JeWgIt06jX4LimMGLH$BoQewwleN8nVgEqazYPMrXieZY2+0OHSHNtEwmEWvls=', NULL, false, '00175028370', 'LUIZ', 'Ramos RIBEIRO', 'luizramosribeiro@hotmail.com', false, true, '2025-07-25T15:50:29.702951+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1257, 'pbkdf2_sha256$1000000$NNATZWRxKMOaXBWTpFDdQ8$GjndRdJ6FPQhgLRpyEccEjQf5f+WaSgPbJEHcKtwu9w=', NULL, false, '80561292353', 'Márcia', 'SANDRA Rego de Sousa', 'militar_108749-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:30.673841+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1246, 'pbkdf2_sha256$1000000$0rvx7fMSOMrJMWYZ8Gppuw$iCoiMhVikm9dcWyzUNb2MOaRC/ImhEDtsYsITWqWEgw=', NULL, false, '35318759300', 'Marcos', 'Antonio Lima Gonçalves MINEU', 'militar_014568-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:19.874305+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1232, 'pbkdf2_sha256$1000000$FkqPXfBMVySpos9O9LKv9U$z1XtIYqW9NwIX1343uZAJDjdjwYg/wT0qm0UF/9e3fw=', NULL, false, '38720060378', 'OSMAR', 'Avelino de Sousa', 'osmarbm2009@hotmail.com', false, true, '2025-07-25T15:50:04.703120+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1260, 'pbkdf2_sha256$1000000$qa924SShv1fyFZzoW038EB$k20uyHnHzsIWhIWkKw1AUOydSycyR95GiLiTnLeuu+M=', NULL, false, '02173684337', 'Paulo', 'BEZERRA de Sousa', 'paulobsousa@outlook.com', false, true, '2025-07-25T15:50:33.559120+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1247, 'pbkdf2_sha256$1000000$5KnVblxrAG5qYce8RL9lpQ$fmIIhy6AAD+vEraIaCaaVv7IuypRSrE675VP6/c0H2o=', NULL, false, '36207748387', 'Raimundo', 'NONATO Barbosa dos Santos', 'nonatopanteracb@hotmail.com', false, true, '2025-07-25T15:50:20.854001+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1250, 'pbkdf2_sha256$1000000$eIOjr4Sdbf7M3ee6GoiIb7$dXKAIj8D1+wqx6YpQihBzUbKrMnYNsrKA59vsDS+uGw=', NULL, false, '93809484334', 'YONESKO', 'do Brasil Marques Carvalho', 'yonesko@hotmail.com', false, true, '2025-07-25T15:50:23.851428+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1287, 'pbkdf2_sha256$1000000$qqhoe2tI1cSmjut1gjsaqu$MaEHQLniR8gkXb8PQ6GXqVEvyNJOS1ij/2NWCb+h4hU=', NULL, false, '88203212387', 'CHARLES', 'Ivonor de Sousa Araújo', 'charlesivonor@hotmail.com', false, true, '2025-07-25T15:50:59.988187+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1293, 'pbkdf2_sha256$1000000$rw6eQ9LT9140R2tbuji0pQ$BqmgfTqRipMzEWKT99DM/x/Kcm/ZwzX2P9yPhfxq1Dg=', NULL, false, '66440157353', 'Cleiton', 'Carlos Silva SABINO', 'cleiton_sabino4@hotmail.com', false, true, '2025-07-25T15:51:05.799920+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1294, 'pbkdf2_sha256$1000000$ixyojVVxwwDr3srCLLuXvC$P2B3EFO3YboXmxyrIqsJz05essLQePGwMPezc9FUsBE=', NULL, false, '91324718315', 'Daniel', 'OLIVEIRA dos Santos', 'daniel-oliveirasantos@hotmail.com', false, true, '2025-07-25T15:51:06.754677+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1298, 'pbkdf2_sha256$1000000$kJYUFE9dJ6kCklk8c0KTwa$pJ4F5DhpXc9vZYvDE7rdli9srbfy7PZlM7DB8bYNP4A=', NULL, false, '01192819373', 'Eduarddo', 'PENHA Viveiros', 'eduarddoviveiros@gmail.com', false, true, '2025-07-25T15:51:10.518641+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1296, 'pbkdf2_sha256$1000000$rSrP0qI4Y3jsahJoS1S1zi$/PLBH62O4R+DSaTQUFoPafoze3g2gCerfzGHMYvaB9k=', NULL, false, '02668418305', 'ELVIS', 'Vieira Leal', 'elvis-vieira-leal@hotmail.com', false, true, '2025-07-25T15:51:08.629241+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1290, 'pbkdf2_sha256$1000000$yofBcEzeyOeqPBq5svw2tN$AqdDHYHo2F5e7/Pu7ZJ3+fybnomQ6P9Y/0RcYurjM+Q=', NULL, false, '04999950316', 'Jardson', 'Viana FALCÃO', 'militar_244861-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:02.888888+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1292, 'pbkdf2_sha256$1000000$GoeMoWmm4PCzjnW13eNc1J$ccriCB4xLgL0VvQvwWsNi9psoZEX4i2CyMsAGaFaFBo=', NULL, false, '02753631395', 'Johnathan', 'Patrício Cavalcante SEIXAS', 'militar_244863-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:04.853487+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1285, 'pbkdf2_sha256$1000000$s0PMGj2vnpNQiND8AWdKdW$AtAFZ+4nkkC7jg7Mv7pl1dO+AkiBykpQKTvThFJUMhI=', NULL, false, '00691310319', 'JORGE', 'Henrique Rodrigues Miranda', 'jhrm21bm@hotmail.com', false, true, '2025-07-25T15:50:58.053290+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1299, 'pbkdf2_sha256$1000000$aI6AUagA2EgbJgdLzcLh3e$IDtCxUM2F8VLp5Zbr2BwgBhcscAGYq2luINFmn81eVc=', NULL, false, '99742039372', 'Lamartine', 'LAVOZIÊ Aborgazan Barreto', 'llabarreto@hotmail.com', false, true, '2025-07-25T15:51:11.484447+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1295, 'pbkdf2_sha256$1000000$zeud9PHwIY4UnKxbgv012W$1SbS8a3E8ME3BbuIVejtpcEiQ/+06HXwyFmZ06zk1mY=', NULL, false, '65234588300', 'Moisés', 'Andrade Fernandes CANTUÁRIO', 'moisescantuario@gmail.com', false, true, '2025-07-25T15:51:07.697158+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1289, 'pbkdf2_sha256$1000000$rITUyP1fWqbt9xJJP5LsAO$VzPWh0+/A9dq+kRLUAi3dt7xF0WhzzrZQkf8btpNKqk=', NULL, false, '02803639319', 'Pedro', 'Yuri LAGES Costa Melo', 'pedroyurilcmelo@hotmail.com', false, true, '2025-07-25T15:51:01.919386+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1288, 'pbkdf2_sha256$1000000$oJUl30PZrXPQ7a6p5dx1VX$TW57g2nGoVicgglkrVF26ZP2j09EkOAu+J/EhFpVrws=', NULL, false, '02682383327', 'RAFAEL', 'LOPES de Araújo', 'militar_244873-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:00.967819+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1297, 'pbkdf2_sha256$1000000$1Ak1ozOeAjIb4wwZL97uVd$5TYS2j/p/ko5tWVWj+GtDMAo4N35A5LQJZrJu791sHg=', NULL, false, '01767710348', 'SAMUEL', 'Lira do Vale', 'militar_244865-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:09.579048+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1286, 'pbkdf2_sha256$1000000$0XYEYqJsDFv2q68RMI9Rny$zGzbJKJgSeS6Z6cUb5Wm5qdbbeN48ok6kzmK70VoFxg=', NULL, false, '66092884372', 'THIAGO', 'Lima de Oliveira', 'bm_thiago@hotmail.com', false, true, '2025-07-25T15:50:59.020159+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1265, 'pbkdf2_sha256$1000000$3IMZzKGdSEbA355KIslR6u$gXFIRAvE9WBMOr+rPg5YfQ55cd3NBVeHKq45jrsksJ4=', NULL, false, '00262860333', 'ALEXANDRE', 'Torres Brito', 'alexandre_piaui@hotmail.com', false, true, '2025-07-25T15:50:38.476062+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1283, 'pbkdf2_sha256$1000000$r0b53f1Bz9WGM63uoTHPjS$dE/PED0OzUqrFwDl8BjfUE40OVR6XppJVrUorT9aC+Y=', NULL, false, '88401634334', 'Antonio', 'CARLOS da SILVA', 'carlosmthl@hotmail.com', false, true, '2025-07-25T15:50:56.094886+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1279, 'pbkdf2_sha256$1000000$3uzxcCYNxddDb8efFFpQzS$++lX8zodwbCpmrUJiPRfT/NS932Q09kAyM/LDJ/L15Q=', NULL, false, '01674761309', 'Antonio', 'MARCELINO Ribeiro Junior', 'marcelinobmpi@gmail.com', false, true, '2025-07-25T15:50:52.168129+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1284, 'pbkdf2_sha256$1000000$cvynrvLUPNumdEKYZpYvMw$by1EyZQB5rL+5OjAFOxUgewJffvar7rKq2F5ddf4Myo=', NULL, false, '91900751372', 'BRENO', 'Bandeira de Alencar', 'breno_ce_ara@hotmail.com', false, true, '2025-07-25T15:50:57.083431+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1273, 'pbkdf2_sha256$1000000$WwVBXBhdq28lBIEADb78mp$V+L5EANZQzb24hEm6hIOa3MQ+ByxAJVnqjaqLpskufQ=', NULL, false, '74860305353', 'Carlos', 'Alberto Pereira OLEGÁRIO', 'bmolegario@hotmail.com', false, true, '2025-07-25T15:50:46.321875+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1263, 'pbkdf2_sha256$1000000$T07HDlBbNmv4b99sjUpPC2$3F7Z+AhaztmLBJWfXB+8HkS5TUHjPzYCdTYO4FXiFpA=', NULL, false, '02486847367', 'Dâmaro', 'STÊNIO Melo Viana', 'steniobm48@hotmail.com', false, true, '2025-07-25T15:50:36.484283+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1264, 'pbkdf2_sha256$1000000$w2vbX3AT9jQpc1xHJA11SV$9Q8oNkj7qMlX5yHKOMY4L314KMsg+UsYcQkjB9wypP4=', NULL, false, '83915443387', 'DANIEL', 'Nepomuceno de Sousa ABREU', 'bmdanielfire@hotmail.com', false, true, '2025-07-25T15:50:37.502543+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1278, 'pbkdf2_sha256$1000000$u42XkE1d2p9wZizJZAEB1p$yqWfmqlUL4CCBA0w6putDLF2AgeAgE6c5TTEvosIc54=', NULL, false, '91436370353', 'FABRÍCIO', 'Bacelar Salles', 'fabriciobepe@hotmail.com', false, true, '2025-07-25T15:50:51.152114+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1277, 'pbkdf2_sha256$1000000$cO6C8d1kuVhn70hnH1qRxP$9/KJQeuXpFquOCAFM0+cbkQtENQmgzQL8U1f1upquxw=', NULL, false, '76919099349', 'Francisco', 'das Chagas Carvalho dos SANTOS FILHO', 'franciscoiza@hotmail.com', false, true, '2025-07-25T15:50:50.183149+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1282, 'pbkdf2_sha256$1000000$sX0TZHapgqmGN6J2WkXH6h$xlqy+neT64hmXuqWrWU8+m5F+3MM9hGYeMiuSZb6EEg=', NULL, false, '01732645302', 'Francisco', 'das Chagas da ROCHA Praça', 'militar_207479-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:55.118833+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1274, 'pbkdf2_sha256$1000000$Xo1Mj2KXgghWGB8FoB8fdz$LTihSSclcRfq9ReZ4R38kzm+Ohbiz5SeE1TXG3ON8es=', NULL, false, '85231908304', 'GYVAGO', 'Lira Moreira', 'gyvago@bol.com.br', false, true, '2025-07-25T15:50:47.291511+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1269, 'pbkdf2_sha256$1000000$X54NX0Tt53e0IEMxJ35GIw$66jrYzAHl3rkxF6lO1Jbc8wrTV/yzf731JwjskvQE7I=', NULL, false, '60044549318', 'Helio', 'Marcio FONTENELE Filho', 'firemanfontenele@hotmail.com', false, true, '2025-07-25T15:50:42.421951+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1267, 'pbkdf2_sha256$1000000$ecy2mqxG1tovDLtggf0spc$R237VfOoZluj6VgbHPnWkIKsvSyicf1KaZJBP2BPVmA=', NULL, false, '01089116322', 'ITALO', 'Vieira Lima', 'ythalolima@gmail.com', false, true, '2025-07-25T15:50:40.433342+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1281, 'pbkdf2_sha256$1000000$rhPKfyPxz3FgXwjrNCgt2a$TR4sJDHY1ILxnn+8TrlMov/0rWi6vtEf9Km8qEGo2rE=', NULL, false, '00926856332', 'José', 'Francisco de ARAÚJO Silva', 'jfaraujo6@hotmail.com', false, true, '2025-07-25T15:50:54.115051+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1275, 'pbkdf2_sha256$1000000$cJijMpJVJnQSevednvmmd8$ckBQmTBqc/4HDAhHA1uyPxL/5n3CT477QLyJO6JkTC8=', NULL, false, '00255267312', 'MARCIO', 'Rogério Bernardes da Rocha', 'marciorocha6@hotmail.com', false, true, '2025-07-25T15:50:48.253885+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1270, 'pbkdf2_sha256$1000000$FraQJVieg910enKE5mpqsc$ZjBYiUvP7hUkonPlwwk+s4RBTdCmoZsGrtgdXLrXEmc=', NULL, false, '84811234391', 'Marcus', 'VINICIUS Bernardes da Rocha', 'marcus.25@bol.com.br', false, true, '2025-07-25T15:50:43.398032+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1268, 'pbkdf2_sha256$1000000$bCtVt2S52WOEL5ePptHYWF$wmrA7Z9/5xohRA94KxsNXBBfcEBaogiFBR5B9615z5A=', NULL, false, '02932912330', 'NATHANAEL', 'Araújo da Silva', 'naelterrier@gmail.com', false, true, '2025-07-25T15:50:41.417276+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1280, 'pbkdf2_sha256$1000000$wDDlNexhDopUWJlbeU196O$4Lw6df70v+yLwk5OnWeio04gmlTRv7+kM5nju0yN3M8=', NULL, false, '99817713334', 'NELSON', 'Pires Sadalla Júnior', 'militar_207488-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:50:53.134543+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1266, 'pbkdf2_sha256$1000000$FUB4EoywqrQcIUGVHLHHGa$9/GaqcfLTPJZ1c3eAXPD8Z9vWQaPyxoKwy8a+bjLrCg=', NULL, false, '03199162436', 'Pedro', 'Augusto RAFAEL Bezerra Neto', 'rafael.pedroaugusto@yahoo.com.br', false, true, '2025-07-25T15:50:39.452994+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1272, 'pbkdf2_sha256$1000000$zCJkKDb24z8gl9kH9KSKki$Y/nEQzQcZDZT3nykL4ae0MRF+lKbpSixfnSV2kc1uFM=', NULL, false, '65086724368', 'Renato', 'Oliveira SANTIAGO', 'presizao@yahoo.com.br', false, true, '2025-07-25T15:50:45.369781+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1276, 'pbkdf2_sha256$1000000$OBgjaSaRpRohwlacQImSkn$Ofsaigt9A9xVv156sinxLqygXBzY5b4W1RSn0QYNCbc=', NULL, false, '78797071315', 'RONIERE', 'Alves de Azevedo', 'roniereazevedo@gmail.com', false, true, '2025-07-25T15:50:49.226110+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1271, 'pbkdf2_sha256$1000000$TT7JU4QbEHzA6mvJ80Gmdl$UzuSxf3/jbtL29oZBYL7b8ircCL63/ObWnlJGA7vrec=', NULL, false, '02417655365', 'WILMAYKOM', 'Sousa Fontenele', 'wilmaykom@hotmail.com', false, true, '2025-07-25T15:50:44.368339+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1306, 'pbkdf2_sha256$1000000$1Cs52PZTgcdR4ftZjBr5Zu$GDq2SosRIg0qsnIDB/VVn+gDBJourhpjBvKfHgM/55Q=', NULL, false, '04047484300', 'ANA', 'LAÍS Martins Aragão de Lacerda', 'laisaragao.direito@gmail.com', false, true, '2025-07-25T15:51:18.524561+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1300, 'pbkdf2_sha256$1000000$W7q6wfEDx9bXv0OMBM9Aeo$pp9LP3stzW+NHV2ajjpuduHVRUSvxH2Qni45rgq6tvE=', NULL, false, '01690030356', 'Diego', 'FREIRE de Araújo', 'diegofreirearaujo@hotmail.com', false, true, '2025-07-25T15:51:12.448649+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1302, 'pbkdf2_sha256$1000000$FK8RMiNrUncu46RsWXsg0b$RsruwT2pYObxGvNHC1acIRGenpNkp1bV6cHlBk8X6Ac=', NULL, false, '04161824378', 'GEORGE', 'Ricardo de Sousa Honorato', 'georgericardosh@yahoo.com.br', false, true, '2025-07-25T15:51:14.367056+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1309, 'pbkdf2_sha256$1000000$Mx8NehoJkgHVs45Gz4fNuo$ecZBTDIr2pXTU2UqinrlmNlxAtW2aTGn2N8pvOGfVyw=', NULL, false, '88175090359', 'GILVAN', 'de Freitas Rodrigues', 'gilvanfr2014@gmail.com', false, true, '2025-07-25T15:51:21.825082+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1301, 'pbkdf2_sha256$1000000$Gnwe7UrVzoZjPriArAxBbE$YRE8fv6j5DqeWpmuCwmUijApGYdc6crPoZgBSBzwaCs=', NULL, false, '02467595340', 'JAMMES', 'Magalhães Silva', 'jammesmagalhaes@hotmail.com', false, true, '2025-07-25T15:51:13.405296+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1308, 'pbkdf2_sha256$1000000$mmQoFfNkSWpQSFMZ1XLisr$m4ANJowK6eho0c7UtC5YIjZFLIBB4yO/q4xcxL1mJTc=', NULL, false, '05396294302', 'Jorge', 'GLEYSSON da Cruz de Carvalho', 'jorgegleysson@hotmail.com', false, true, '2025-07-25T15:51:20.886362+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1307, 'pbkdf2_sha256$1000000$vhyW5qjxJOo6S6KVFY55u6$92ABpb1R35CK/Nvnv8E3anVYNSY2HVPsVIULden8DvA=', NULL, false, '04014914399', 'MAYLSON', 'Damasceno Mariscal de Araújo', 'MAYLSONCENO@hotmail.com', false, true, '2025-07-25T15:51:19.920493+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1305, 'pbkdf2_sha256$1000000$chaIp4DuFznbuWyiWLc3Vn$OgTw3omWfEFS1Fx2f/NxQXJSi0PZBAdX5nMgycOUZx0=', NULL, false, '00211306398', 'PEDRO', 'PAULO Bezerra', 'pedropaulo.mh@bol.com.br', false, true, '2025-07-25T15:51:17.206825+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1304, 'pbkdf2_sha256$1000000$fe6c18d7zzD5kcSbwVwWZQ$V2ljsnM25qnWvShZKN/pRCmCqQriASg3CIMu3p74T/w=', NULL, false, '02194214550', 'WENES', 'Bastos Ribeiro', 'militar_244878-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:16.260208+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1313, 'pbkdf2_sha256$1000000$MBTZWHMDlewQ9muWjIsi9C$AkIxfmBhttscqGLtoyasKwyLK5q9lIOQAaPeVHgKDCE=', NULL, false, '00727769359', 'ALDERI', 'de Melo Pereira', 'alderimelo@hotmail.com', false, true, '2025-07-25T15:51:25.642931+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1314, 'pbkdf2_sha256$1000000$JLIHIYJdVt67cRV8ZBnWZ4$ygOW8eR7RPktzSVur5Yu8tG7FtVqY61MiTvGEw7Nf2E=', NULL, false, '01309318379', 'ALEX', 'Karol Carlos da Rocha', 'alexkarolca@hotmail.com', false, true, '2025-07-25T15:51:26.604556+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1321, 'pbkdf2_sha256$1000000$G273kh0jfSSBNMSvvcsw5j$00UxkYmik6olHG/WT1GyVKS5aYsztvHjll8WmY2X4M4=', NULL, false, '60017508312', 'BRUNO', 'de Oliveira Lopes', 'bruno-llopes@hotmail.com', false, true, '2025-07-25T15:51:33.271362+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1310, 'pbkdf2_sha256$1000000$rVPp1K18aOYqwUdrxLkJ6b$tSwcpBcnvdcRS6YUB9KrRSvz6ekhOtNvlrlczCkFwCk=', NULL, false, '01819415384', 'David', 'Silva MAGALHÃES', 'DAVIDSILVAMAGALHAES@hotmail.com', false, true, '2025-07-25T15:51:22.769903+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1312, 'pbkdf2_sha256$1000000$WmHEv7tQJuFNxzFvTW1pNC$EIilduXT2xZBY5AOg4F5lMPomIQKQ2cwOQVI2o9keCI=', NULL, false, '01705951376', 'FELIPPE', 'da Silva VIANA', 'eusoufelippe@gmail.com', false, true, '2025-07-25T15:51:24.698912+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1317, 'pbkdf2_sha256$1000000$6mm08EOxvMlDelXXCQvSBt$FLxFppnfHSmnw1mur9NpdHSyblZOdIYog/hmqszYDd4=', NULL, false, '00076735311', 'FRANCINALDO', 'dos Reis Lima', 'francinaldorlima@hotmail.com', false, true, '2025-07-25T15:51:29.463774+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1324, 'pbkdf2_sha256$1000000$3l9MoHAQQA6TFVYpLKWB20$p9ajQeNT559MiMxvwtQVkDzVzKVT3453Pc2RMn+iH/U=', NULL, false, '97705420325', 'Francisco', 'das Chagas PABLO de Morais Leite', 'bpablo.leite193@gmail.com', false, true, '2025-07-25T15:51:36.107707+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1323, 'pbkdf2_sha256$1000000$VtIntPIzfy8WOlpddGUHCM$PrIvHX7nU8Arx55aNb0es5Ys2Sgcdi4H//DCLtGUUD0=', NULL, false, '01054972311', 'Georges', 'Davis NORONHA de Menezes', 'georgedavys@hotmail.com', false, true, '2025-07-25T15:51:35.171894+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1322, 'pbkdf2_sha256$1000000$5zqcyY1wO71prKNkAs6uOb$6Fgs1GMB6b+6zHGHQmoT4fhL8BBPC0aMcXFutkdnZtc=', NULL, false, '00998447374', 'KAROLLINY', 'Barbosa Silva', 'xkarolbarbosax@gmail.com', false, true, '2025-07-25T15:51:34.225177+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1325, 'pbkdf2_sha256$1000000$27tDAsGvQdnrzHzvXBiG91$cSZydl603zk0InWsLut3nGHX6m1Cnm2+eefs+qH0rwU=', NULL, false, '02691869300', 'LUCIANA', 'Lís de Souza e Santos', 'lis-luciana@hotmail.com', false, true, '2025-07-25T15:51:37.046885+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1316, 'pbkdf2_sha256$1000000$24i4C8sqlppGViHNdOJq0o$O4e57I6PbXCAAlw26aYttKKdN9sBmiNNPJjJmxQ/WiQ=', NULL, false, '00725909390', 'MARCOS', 'AUGUSTO Lima Soares', 'militar_270313-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:28.514859+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1319, 'pbkdf2_sha256$1000000$viOD9HNHwquiABbWcYUKY2$yhM3kViGpaN9iA7tWBMr5P9LnXzQ2CjVBUp0276jImo=', NULL, false, '04106307308', 'MICKAEL', 'da Silva Nascimento', 'mickael.nascimento@hotmail.com', false, true, '2025-07-25T15:51:31.374982+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1320, 'pbkdf2_sha256$1000000$Nom0GOAFDlIg2YVIvMhlvI$4CUdBbpsSC4OAflsZSF1g1T8xuPifN8A4k/tlYWbGoA=', NULL, false, '00242445381', 'Rafael', 'ESCORCIO Pinheiro', 'rafaelescorcio13@hotmail.com', false, true, '2025-07-25T15:51:32.319478+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1315, 'pbkdf2_sha256$1000000$mhfugDB4ZePuB7L4wumWqn$kw0Rdxy71q0YwPAgJfBy9yAy4Q2q2PoUYM4NdYseMSM=', NULL, false, '02172353361', 'RILDO', 'Kelson da Cruz Gonçalves', 'kelson.geo11@gmail.com', false, true, '2025-07-25T15:51:27.547285+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1311, 'pbkdf2_sha256$1000000$5wtLEypWYDOuV2dA28fdze$7bKDiD2doRlsAAZGRufogTDRQZNPhQCYiWniEPZABQo=', NULL, false, '02768970301', 'Thiago', 'ARCANJO Pires Oliveira', 'th-phb@hotmail.com', false, true, '2025-07-25T15:51:23.709522+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1318, 'pbkdf2_sha256$1000000$wheZKWXGndRzxBddZiNzX3$KpHzfOfD2G/FqszDwGEMDoMSfRmRW/kLXapEz4UTgxo=', NULL, false, '02553338384', 'Vagner', 'Alves VIANA', 'vagnerviana007@hotmail.com', false, true, '2025-07-25T15:51:30.419410+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1330, 'pbkdf2_sha256$1000000$gS9PY91T1ud0OW3p4G92xq$M6ifzkGdgP4jKU9GQsGnGjWHLl2e9ALgU9H7MXdzv4s=', NULL, false, '02426181389', 'EDUARDO', 'Lira de Oliveira', 'militar_292164-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:41.986604+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1328, 'pbkdf2_sha256$1000000$R4wfDXy4kTt0hQmiklvCM3$hljndGayWyDL0Fk1BceAAkTmGw2jPX5MVNXgb+9snpw=', NULL, false, '00145544370', 'Felipe', 'Santiago MONTEIRO Neto', 'felipetotal@hotmail.com', false, true, '2025-07-25T15:51:40.010903+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1333, 'pbkdf2_sha256$1000000$9vBqhEZiAfIU6RMbwSw3pl$Vuy7+7EgP+xfNNqjN2fdh+/QxZJxGGrVtG+/BjwEnaQ=', NULL, false, '65842936372', 'Francisco', 'dos SANTOS de Sousa Batista', 'militar_270305-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:44.904688+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1332, 'pbkdf2_sha256$1000000$C3MdNByUz0B36OM4y7FdZW$V5HvoqaG+KLMW87OJJZQ81yRsYXYf8a773cXaVT2qRs=', NULL, false, '01586830309', 'Gustavo', 'FELIPE de Brito Lopes', 'gusttavobritto.13@hotmail.com', false, true, '2025-07-25T15:51:43.948315+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1331, 'pbkdf2_sha256$1000000$6K0SY2v8U2F19I8u4mJbtk$dRssykqbjpRW8a7tLi/25M9Cm4XYpym97juvxnVRB+A=', NULL, false, '99864347349', 'JESIFIEL', 'Arnout Silva Sobrinho', 'jesifiel@gmail.com', false, true, '2025-07-25T15:51:42.966496+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1329, 'pbkdf2_sha256$1000000$HupH6d1kaiLLhUAdvXI8I5$Zhr448mItPgHcdpukam6/tr2K3ZGyT/zH3SNKbP4tc4=', NULL, false, '99784297353', 'João', 'Bezerra NOVAES Neto', 'joaonbneto@hotmail.com', false, true, '2025-07-25T15:51:41.019500+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1335, 'pbkdf2_sha256$1000000$DCFGitpFCUxql3QONhiB2g$SYIzJNwcbmFROlw6EuRZ5UlVrluw1hSNv+fMMz3Xdb8=', NULL, false, '65293983334', 'Josué', 'FELICIANO de Melo', 'joshuahenry8@hotmail.com', false, true, '2025-07-25T15:51:46.832567+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1327, 'pbkdf2_sha256$1000000$lc4RFaFguQCcBOVI07Yp31$vKBD6cJPPhrtLeilezGMniUJ6j0ywVxV7IT04KMhNu8=', NULL, false, '90949781304', 'Manoel', 'Antonio de FRANÇA JÚNIOR', 'manoeljj3@hotmail.com', false, true, '2025-07-25T15:51:38.937065+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1326, 'pbkdf2_sha256$1000000$iL0i5pvVth0VJ1rQlf9KaH$D7a86Ys4g7S7Aonkiv83/4HG63NelIlWpEpoA3/prQ0=', NULL, false, '03597260381', 'RAMON', 'Thiago Pereira da Costa', 'ramonthiago00@hotmail.com', false, true, '2025-07-25T15:51:37.992226+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1334, 'pbkdf2_sha256$1000000$oIeRqhYukC3Zg5FAFi9PGo$EC+tJCGs/KjlV3teLPqHpQHIGDeOxAtige03KF2xJtU=', NULL, false, '00766079333', 'RENATA', 'Pereira dos Santos Silveira', 'nanaka23@hotmail.com', false, true, '2025-07-25T15:51:45.865885+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1336, 'pbkdf2_sha256$1000000$LOEaCUTKimlDI45DL6BACm$KdeY26AZzTGPKXB/I7WdZl+R917ds95oEvqm+Swo6iU=', NULL, false, '02638446335', 'FÁBIO', 'de SOUSA da Silva', 'fabiosousa.adm@outlook.com', false, true, '2025-07-25T15:51:47.788733+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1355, 'pbkdf2_sha256$1000000$TzLXBK0S8v3ju0YU3CAF1x$93zIggI/o4Myi8tPbJ+3mepHBF/Blyfpim9y8KWthlQ=', NULL, false, '03939280399', 'Antonio', 'BARROS Leal Neto', 'militar_332412-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:06.175684+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1361, 'pbkdf2_sha256$1000000$H4TSKQdEsF27sjgCPeAqWh$Yw5CQDFtEEIsntdv10aaRCiUEwABdKugkJMKUqglX9M=', NULL, false, '01444061364', 'APARISA', 'Maria Coêlho dos Santos', 'militar_332399-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:12.008982+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1349, 'pbkdf2_sha256$1000000$8bmDTD2D9LPGIqTifhKrcI$nqh769IG0YBAZk94as/61+QI/Q+IfFnUD/8MQTtqlyU=', NULL, false, '05973981355', 'Bruno', 'GONÇALVES Costa', 'militar_332424-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:00.133054+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1352, 'pbkdf2_sha256$1000000$AMprsNO96lD388skMwasKV$qY3Ml/5+G6t7nc9F4AfaXCmq7gUaSU24HKNCmUYdPWc=', NULL, false, '05502246370', 'DARLAN', 'Cunha Lima Filho', 'militar_332428-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:02.992165+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1362, 'pbkdf2_sha256$1000000$doKVzdbIqXsb3XX0gnBtWy$vH8SCpxvkqfdi3LAK3AFCbhKBC892M4rqIHrewBmN8Q=', NULL, false, '02434167330', 'DOUGLAS', 'Teixeira Ferro', 'douglastf91@hotmail.com', false, true, '2025-07-25T15:52:12.950671+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1370, 'pbkdf2_sha256$1000000$o3ZnlSLrCY9NElnjJQMpOB$tGBRV4wVQpMLNQ8JLPD6VoJKAuV2/p0PtzzAd2u1cJo=', NULL, false, '06096764312', 'Erida', 'THAYNARA Assunção Araújo da Silva', 'militar_332451-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:21.505075+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1366, 'pbkdf2_sha256$1000000$WraGLo12mZZeSIIgx3IT7b$dGxWbE6/qMP+ew4jA/MfzHBZQszaEHIH0qvzN4Vr0M4=', NULL, false, '05497836364', 'Fabrício', 'de MOURA Medeiros', 'militar_332420-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:16.705229+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1343, 'pbkdf2_sha256$1000000$bYYEKlbIioQ7kyT9uVSOrU$F0ltiDi+95SgAZ5W6CSN7KZhkfGNZC35HD7r1tERz0c=', NULL, false, '01675033323', 'Francisco', 'MARQUES Brito Neto', 'militar_332436-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:54.482705+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1371, 'pbkdf2_sha256$1000000$cAryvfzlgWb24tlhyeu8vU$ryNZ6J4yhlpyX905cpbfXA+voAAJvnFLsGX4+bdDOlg=', NULL, false, '02521963330', 'Giovanni', 'PIO Viana', 'militar_332433-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:22.443134+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1339, 'pbkdf2_sha256$1000000$tBaYnB14fLWbxQuWFzeMgk$1HyCN7I3U/QN4N7XYuvXBkZ2CoSLEzvOOuBSG9kmrtc=', NULL, false, '06603999110', 'IGOR', 'Araujo Ferreira', 'militar_332425-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:50.643141+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1364, 'pbkdf2_sha256$1000000$Ws5DLNo93mRICREk2sjyC1$jn4a+fwAYhqO5igsxsNgzjuXVMjybEaGaXNSpmJaygs=', NULL, false, '05215965307', 'JACKSON', 'da Silva Bezerra', 'militar_332430-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:14.824060+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1358, 'pbkdf2_sha256$1000000$TWwyACCEVWljtLZle4Wn2X$tvqxQsHFHXg4erNONl7vKyedCXWYY76jTn29HqY8e3M=', NULL, false, '04881595393', 'Jackson', 'de Melo SALES', 'militar_332398-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:09.141716+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1363, 'pbkdf2_sha256$1000000$pL5HmSRJaMl2lDXUeajvje$bvEMLyDSUmkLuQmPYEI8Wc8hDC++GZsv7TLYXj5pxUw=', NULL, false, '01062235347', 'JARDEL', 'Carlos Santana Abreu', 'militar_270308-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:13.882642+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1360, 'pbkdf2_sha256$1000000$qYSeaURZugqqHbChtzfSw7$8Ygq+oS0tZDDQH7dIhqNR5fKzoBeOG4oAkLOrkUpbts=', NULL, false, '06159780379', 'JESSÉ', 'dos Santos Ribeiro', 'militar_332434-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:11.071373+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1338, 'pbkdf2_sha256$1000000$JulYtlNj3DJBtecOUqnuT1$iLezosW+K4YD7J9vppcK78lW6gHoC/HrxkqolLsXTOQ=', NULL, false, '06149683303', 'Josiel', 'AFONSO dos Santos', 'militar_332439-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:49.692718+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1368, 'pbkdf2_sha256$1000000$qiI46w2W9ISiP1sboMEZSX$uANae/jlfem9nL1lAvz/AeNRCf8kRCLXSlGtA48HcoI=', NULL, false, '03991477300', 'KLAUS', 'Henrique Martins de Morais', 'militar_332472-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:19.424306+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1369, 'pbkdf2_sha256$1000000$hdTPx5BRgAaGfMR1MMCvNf$A9bFjSc+LzRFUrfN29H+JCR78madFk/YwYpbjyiniQY=', NULL, false, '02696409323', 'Leandro', 'DO VALE Teixeira Cunha', 'militar_332452-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:20.574932+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1347, 'pbkdf2_sha256$1000000$avOwvVp3uHoSSZMD6P7sDO$6BCPje2rBUVI70OJbCu3ZqLomtV3fuAvKHWNKjT3Eyk=', NULL, false, '07121235390', 'Leonardo', 'Alexandre MACIEL Deodato', 'militar_332413-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:58.237562+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1337, 'pbkdf2_sha256$1000000$pif5YjkRl5drfzHxWaATSK$qXVORVI1UxqljSbwm4Vm+EAiFukZcJSa3MIkEIB5KHc=', NULL, false, '04844049380', 'LEONARDO', 'Moreira Gomes Alves Rufino', 'militar_332426-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:48.741128+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1350, 'pbkdf2_sha256$1000000$aX4xRVCxwU2art68o65ROP$8lirnW7wNrTbxtEWEx0e/5SbHL1PEwBl3TdQa6v+dp0=', NULL, false, '03695390360', 'Luis', 'Henrique de ALBUQUERQUE Lustosa', 'militar_332453-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:01.074750+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1345, 'pbkdf2_sha256$1000000$2xafktwG0kQ5z11KmrLpcg$RiTYQYzyEWgPm1ySEICkcEfk78d56d1KoKfTf6UQp6I=', NULL, false, '03253893308', 'Luiz', 'Silva CASTRO', 'militar_332419-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:56.350172+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1348, 'pbkdf2_sha256$1000000$qISzdTYwB3ZQjFscSaWcAi$Hsq6ZiP4CsEWhWlq8X5RPgRpLn8jnXufEXRSZ4va6aI=', NULL, false, '06116869378', 'Marcos', 'FERNANDES da Silva Rocha', 'militar_332396-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:59.184110+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1356, 'pbkdf2_sha256$1000000$RdCgxdcZCcJ3E8WGPDd904$SBJtPdzMxAOZ82v/gu5ruITsORuqoGF2MsYuIl3xDtI=', NULL, false, '02173789350', 'NATALY', 'Cristina Silva Carvalho Costa', 'militar_332450-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:07.213428+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1341, 'pbkdf2_sha256$1000000$VnkyGFqDt0P8TPOuv9dzzr$VdmWxEq2d3FfnX1YU9872jdalnFb+sYEHzvIRMDLEKg=', NULL, false, '02162931389', 'NAYARA', 'de Araujo Luz', 'militar_332414-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:52.588999+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1344, 'pbkdf2_sha256$1000000$IUWn3hi3mKIrofJySjj2Hu$EEiqJmBU+Xw51qHil6yV6PbpqADnAJyXj0YD7649Uko=', NULL, false, '02538418364', 'NAYRON', 'Isack Oliveira Melo', 'militar_332397-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:55.435587+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1340, 'pbkdf2_sha256$1000000$3Lyl1wnxFbqHeDYGKN1L3A$0KyFABEkHCGj9J+ZdBPTM8H8UsBn4nuzR67OKrxK79M=', NULL, false, '05498251343', 'Paulo', 'Santiago Lima Dantas BRANDÃO', 'militar_332444-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:51.622317+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1365, 'pbkdf2_sha256$1000000$rVLe0QlgEVhoYKxT0msI6V$RbZD981403CHJvWTpACDwIwSff8uePH+CGKwjtR4qtc=', NULL, false, '03202967339', 'Paulo', 'Thiago de Jesus BANDEIRA', 'militar_332408-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:15.775035+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1353, 'pbkdf2_sha256$1000000$YgmmbqPBUgxPsYE8VkOLXz$MAo5LmXKY4ifgsbf0viPqfJ0W3JUFVPl+x8CqNKq+/Q=', NULL, false, '03796425305', 'Raphael', 'Rubens de Sousa CAMPELO', 'militar_332410-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:04.160838+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1367, 'pbkdf2_sha256$1000000$B92LfFVz7fDwb0OMa3ynqS$eHFAfL5Zi4lrGZp0tUfyBrJfwtuyh1PCHmvoqS77Fjs=', NULL, false, '04577312301', 'Rildo', 'de Sousa Araújo JÚNIOR', 'reldojunior@icloud.com', false, true, '2025-07-25T15:52:17.625433+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1342, 'pbkdf2_sha256$1000000$lH24VCTiciqZuR0RWIwdlb$QZvr4rCJPQlRaM/0PZN2KtejZpUnUB1U4l6lWYVugYM=', NULL, false, '04751786377', 'RÔMULO', 'Castelo Branco Bezerra Filho', 'militar_332437-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:53.532967+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1346, 'pbkdf2_sha256$1000000$Au8Si0FnwQeBvRnYwIDDka$5Tg6MD2e2KW427dh3gT+JrLF0mO2x9fmzEx9unlrdSc=', NULL, false, '02165010322', 'Ronand', 'Santos Ferreira DANTAS', 'militar_332435-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:57.299195+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1359, 'pbkdf2_sha256$1000000$TJ7Cn5dlYhKgPRm7FVn8tn$M8tHoZ2CKTU1+PUHM1Y7tnR1jXzZY68jAltkTEqCac4=', NULL, false, '02416651323', 'TÁCITTO', 'Pimentel Albuquerque', 'militar_332409-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:10.109457+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1357, 'pbkdf2_sha256$1000000$XEJotvo4jNWoqfzjWX4Plv$5Xu92GlYuEoqwGvWIcBoZA0gBolLGKMgPi80Ex0A/Ls=', NULL, false, '05163666371', 'TALYSSON', 'Aguiar Alves de Oliveira', 'militar_332427-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:08.192408+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1354, 'pbkdf2_sha256$1000000$kYvk8hFtPAbT9aLzIpxOrU$WG8DJODArHN9m3IFYZhJYJ3c1aiWV417AoZqvZ5PbVw=', NULL, false, '05504620317', 'TAMIRES', 'Silva Santos', 'militar_332411-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:05.125888+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1351, 'pbkdf2_sha256$1000000$qnNq5XVcXGymKYH5eDDRTC$1NfONp+a7tyYUJpWoNwGhjK7IV0s0ClVyWIN8WUO7aA=', NULL, false, '04356393317', 'WEILLA', 'da Silva Araujo', 'militar_332438-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:02.036272+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1374, 'pbkdf2_sha256$1000000$KtWEyOCO1MA8LPySw3izBq$8XS0QPSTKxKhRl83QomClWOMZqRaPoygMyHhynK3kYg=', NULL, false, '05386074326', 'DANYELLE', 'Ribeiro da Silva', 'militar_332443-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:25.334283+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1386, 'pbkdf2_sha256$1000000$HqXF2cQmMSRMfL7mkETMZw$BOtdsuRkHfkZI6EAqqNklZLFg5bzEoq/3O91rrET+6A=', NULL, false, '02987148330', 'DICLEYSON', 'Pereira da Rocha', 'militar_332404-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:37.210252+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1383, 'pbkdf2_sha256$1000000$SUd6sN8QQvwt7ltnDWyuHl$tpODQRayohgEwGni8gZHCvpmd+MkfyBVPoyIvrZX5hE=', NULL, false, '07422640413', 'Fagner', 'Jairo Fernandes de MEDEIROS', 'militar_332456-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:33.906196+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1381, 'pbkdf2_sha256$1000000$eIgPLT9J2UEqP4kkG6C1gz$6yoLm0vHO78rxv8JkHfTk6ioLsIH3KM9Uaw1mu5v2VI=', NULL, false, '04429543364', 'Francisco', 'CARLOS da Silva Borges', 'militar_332402-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:32.074209+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1380, 'pbkdf2_sha256$1000000$qKHWhEP3QJuSREoTou4j93$nb1MonjRO1zXCguFWeKHQ/3kquxDL4w95eWFBXwOxn4=', NULL, false, '06191499302', 'Francisco', 'Eduardo Alves RIOS', 'militar_332400-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:31.154545+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1375, 'pbkdf2_sha256$1000000$0Ick7XUp1t5CAEB2MVJZUK$VlPat8+43pKs9FX+2ZHx6GVWpmKf1lVIWqGJMucuVHI=', NULL, false, '02324581388', 'GUSTAVO', 'Marques da Silva Alves', 'militar_332454-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:26.276803+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1378, 'pbkdf2_sha256$1000000$yLH5yt7xP9vN64adla4yx5$pGKAJiI9eB3AVeYp1Szf5Zj5SDWbjA65UFmEqENXkVk=', NULL, false, '04248785340', 'James', 'Rodrigues de FRANÇA', 'militar_332455-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:29.188013+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1376, 'pbkdf2_sha256$1000000$r3fMpy64cAtex3OXIrE0R8$4pgeVV4hASSJ/3EenPOAsah97pp25oyUivePBE8x1AA=', NULL, false, '04145884361', 'Laécio', 'WILSON Cordato Pereira', 'militar_332415-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:27.192881+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1377, 'pbkdf2_sha256$1000000$CTuZxe0SywI3aoSFPiuoIZ$IjR7C8yvj+JqvWJyFfmho6rZocDvextVP60BvIZuDKE=', NULL, false, '04550997150', 'LUCAS', 'Ribeiro Cardoso', 'militar_332448-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:28.133391+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1382, 'pbkdf2_sha256$1000000$tmLVfOCLiLYLyLQSOKzj9H$85FBK4msgsaEPRdeXr6b1kTO9ox/hwoeP0hOM5zsCZk=', NULL, false, '06047008305', 'MYSSHELEN', 'Ribeiro Cardoso', 'militar_332447-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:32.990338+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1384, 'pbkdf2_sha256$1000000$natRcuDEveACjitgQ51fbu$Ld62T1uYPn41GgzPXi/LAH1Hex1T/l9JdpBzTt0oeD0=', NULL, false, '02399661397', 'Pedro', 'Henrigue Carvalho de OLIVEIRA', 'pedrohenrique@hotmail.com', false, true, '2025-07-25T15:52:34.852592+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1379, 'pbkdf2_sha256$1000000$bjj48XNmc7cCiLep2DmvYL$2/dcA+/AqONMrwmuLZv3cdPn0BBP6/NeFU9YVwp3EB8=', NULL, false, '05293176307', 'Ricardo', 'DA SILVA Batista', 'militar_332421-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:30.232104+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1385, 'pbkdf2_sha256$1000000$Ax2VfpSloaxGtOl3pH2AwR$q+t09MyJRdRiVnWqGEcuBlwNy6lGNgs8Q/WJKx1eIeI=', NULL, false, '01354371135', 'VÍTOR', 'de Araújo Brito', 'militar_332405-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:35.838201+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1403, 'pbkdf2_sha256$1000000$G9IvG64PDQ4rCbSSppdRBs$xsdQjJnceQ1Gre3Alh+VGsDIyX2hqwzNz8bYKTllsRU=', NULL, false, '03993200322', 'ALEXSIONE', 'COSTA SOUSA', 'militar_416711-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:56.402320+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1408, 'pbkdf2_sha256$1000000$PQIpGVD4cAC8HXUi37grnJ$M251RIsaMDcPSjqLHSNASw6wH0/hD26ehelbEHC3LWY=', NULL, false, '06475068314', 'AMARO', 'LUÍS RODRIGUES DE ARAÚJO', 'militar_416905-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:01.583811+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1397, 'pbkdf2_sha256$1000000$AD0u6oJDcHCKvSSsFxy51U$TofI0V+c1rBF/mcQRDAhrh4nUOVy4x6XQGXUFIeHgvk=', NULL, false, '04861843316', 'ANTONIA', 'KAROLINE DE OLIVEIRA SOUSA', 'militar_416724-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:48.106522+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1402, 'pbkdf2_sha256$1000000$IDs8bkZArNFc1mgePmOIMq$4ugQ0TTivbt23/rQKk4Je3dtmqwnan720tPNok1RSaI=', NULL, false, '06540371322', 'CARLOS', 'EDUARDO PIMENTEL SALUSTIANO', 'militar_416732-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:55.338290+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1398, 'pbkdf2_sha256$1000000$AAO7KFiygT9dSaP5Pj3MUm$g/Q+vnsiUQMyJFYQ9RAnyZHTblXivWRItXkxAu55c44=', NULL, false, '05656115348', 'DENISE', 'CLARA DE ARAUJO SILVA', 'militar_416738-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:49.133281+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1391, 'pbkdf2_sha256$1000000$7JwYlC0eBMBp4Q2RwC5BoS$S+5Rk7GjkWS31rQ9ObnKDjjq58WKAGOZfhjQU+MIR+c=', NULL, false, '06071894360', 'DOUGLAS', 'PIRES MENDES', 'militar_416742-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:42.267916+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1405, 'pbkdf2_sha256$1000000$TG7i2hWwLzyy1mwigN5TLW$dH/DstjXSy6kLxToLeW0406nuZ6PxfMct3UiAOFrmRM=', NULL, false, '07726553324', 'FELIPE', 'RAFAEL DA SILVA', 'militar_416764-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:58.682068+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1396, 'pbkdf2_sha256$1000000$2a0ENCENWc7JucSxktGydF$EBWonJaY1iwBaRHiqu6E04bYC7rcy68wRE9xfhq9ZkE=', NULL, false, '01548919322', 'FRANCISCO', 'SANTHIAGO HOLANDA FRANÇA SILVA', 'militar_416771-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:47.129030+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1399, 'pbkdf2_sha256$1000000$9nMJmVT2XIa0NNEMU1ses8$4ulAxOW6ZL5X7J7aBg5GSFUB7mbwrbbqGip0I5HSoRQ=', NULL, false, '06042154362', 'GIOVANI', 'AUGUSTO ARAÚJO COSTA', 'militar_416773-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:50.146055+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1392, 'pbkdf2_sha256$1000000$jWaLfb7iFLWEU2P4zGyNG3$ix2eTik16S8F6joH++H96RkWZxT7DpR9FtDrfNvjO8Y=', NULL, false, '06634070369', 'IAGGO', 'RAMONN FERNANDO FEITOSA DA SILVA', 'militar_416778-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:43.233320+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1404, 'pbkdf2_sha256$1000000$JxPgupLqLDVyRw9rGlibM9$GCwd5E5OTlpcxamYpt1OLqgdJSqUW/LUgxMSMhJJGC4=', NULL, false, '05368789351', 'ÍTALLO', 'FERREIRA DE ARAUJO', 'militar_416781-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:57.532743+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1395, 'pbkdf2_sha256$1000000$UPdxjNCIFcbiHBlOkDQ9VE$SN7LIKYg9pNaXdTYby+u7RRxd8J+4D+arRrdeop+qRk=', NULL, false, '05528746396', 'JHONAS', 'PAULA DA SILVA', 'militar_416786-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:46.151977+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1387, 'pbkdf2_sha256$1000000$H1E7nKCV8TgZzwOHugpgu7$kq8PrL4RhAw8eMhzHns25lN49fXKp4Vb4krwHmI+Qc0=', NULL, false, '04834699390', 'Lucas', 'BORGES Leal', 'militar_332432-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:38.267261+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1400, 'pbkdf2_sha256$1000000$rZff61Ae4WxkyuZjL7xP8u$9srxwDwA6n2PXIn+j/ovw9ci1Dj/GHYQhNnGIhXudQY=', NULL, false, '08155065383', 'LUIS', 'GUSTHAVO NORONHA SOUSA', 'militar_416819-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:52.529891+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1406, 'pbkdf2_sha256$1000000$EP6y7HZ8u9kAFS9vctRrOB$Ed653XZu7ikNJUdUJ0Pmj3/nOXLgWq8xq4esv2ATo7Y=', NULL, false, '07398340370', 'MURILO', 'DE SOUZA LINHARES', 'militar_416852-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:59.666197+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1393, 'pbkdf2_sha256$1000000$W0FLHpXcc0REnMN9jxHXfU$QagYvAGKf4hspCizQ75N91Sz3AhV58CLLM9QXFm3WRk=', NULL, false, '60665867344', 'PATRICK', 'HYAN COSTA AYRES', 'militar_416856-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:44.211408+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1388, 'pbkdf2_sha256$1000000$MrgxqXBewvQvlfEEmvTwZU$t4eevBn4ZVEdRfbex3tp9hFM4cfsVlZ4w3f541OtvI4=', NULL, false, '03276798328', 'PEDRO', 'GERALDO FILHO', 'militar_408199-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:39.332954+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1407, 'pbkdf2_sha256$1000000$q8kuxyHRFFxxLWYvCSHO90$Jq7CkbNak+9edkQ4TjpK3vr1JIh70vOEnJGCcSw9ylw=', NULL, false, '07193007386', 'PEDRO', 'LUCAS MILANÊS DE SOUSA', 'militar_416863-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:00.636638+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1390, 'pbkdf2_sha256$1000000$0QznaCKwsVz4G3oOjUnjZU$OA/4OCi2GpTuK5NgzIVtV/QQS/W4XchlukNHYZiwv0w=', NULL, false, '06075627308', 'PEDRO', 'RENAN DE SOUZA LIMA DA SILVEIRA', 'militar_416862-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:41.315359+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1389, 'pbkdf2_sha256$1000000$h7fdh78WTH7x0358vwM6lg$K1HqKAy86zyPkESeimRyfgXwmO5hAK2I13qVTkbDRfA=', NULL, false, '04549150394', 'RODRIGO', 'FERREIRA DE CARVALHO', 'militar_416875-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:40.326081+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1401, 'pbkdf2_sha256$1000000$n9D63sUQJ0IXoS2nWhRrr8$+xZ3lmpDcnNlHuMWulLqj0FZ8ZQU5A7QZdtcwkivDpA=', NULL, false, '05595187301', 'RONY', 'DOS SANTOS ARAUJO', 'militar_416878-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:54.208602+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1394, 'pbkdf2_sha256$1000000$RsSRgNj0E3ppKRg9OPAayk$wUNjgbcLHpnh7jRT8oflWEF8PCU2ujz3H0uqRNdC56Q=', NULL, false, '05889512340', 'WALLESON', 'CLÁUDIO DOS SANTOS ROCHA', 'militar_416889-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:45.182157+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1415, 'pbkdf2_sha256$1000000$ECk7vMH0uxl79EliWkiEpL$VC4AmNg+j8QcjCFqxgk0fgdc7yzHKoFdBVyra5bPlBg=', NULL, false, '07113691358', 'ALIELSON', 'FERNANDO DA SILVA SOUSA', 'militar_416712-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:08.264857+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1413, 'pbkdf2_sha256$1000000$o4dR2K6FIibvoxvkNhf4PZ$a4LbCqOXd6q4TA0WnRH7CVjpU3sTnjhadKU+WPta1tY=', NULL, false, '07028206360', 'ALYNNE', 'LARA DA SILVA ARAUJO', 'militar_416718-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:06.367494+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1442, 'pbkdf2_sha256$1000000$TPpA5pvgBNRAl7fCjFEiMv$iY5jZki9Y3ZVIfGvNnn0/HpyDJ987VcAAVNWRgNo/i0=', NULL, false, '05404352361', 'AMAURY', 'MARTINS CUNHA', 'militar_416720-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:35.201322+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1433, 'pbkdf2_sha256$1000000$NbebQ2vAGhFwa3pEJjJdFM$Hc42IFAeRe0cWrvu+HlX5b01Tpx0yfr6wY/IOFiMWXY=', NULL, false, '03225059331', 'ANA', 'PAULA DOS SANTOS PINHEIRO MARTINS', 'militar_416721-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:26.616654+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1416, 'pbkdf2_sha256$1000000$XSipi6I82NBillSdR7LjOt$THjXzUeXXyB73bo0W+Cij1g7E9yQw54d0w7L3kTxAeI=', NULL, false, '05724389312', 'ANDRÉ', 'FELIPE DO AMARAL OLIVEIRA', 'militar_416906-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:09.213192+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1426, 'pbkdf2_sha256$1000000$FeJDjFaPRbS4hGb1TNpG5D$MrkLI5qVx7M5MGycATMipfymAPZGV3dfu/CXuBbxpkg=', NULL, false, '06800657336', 'ANTONIO', 'SOARES DE MELO NETO', 'militar_416725-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:18.854708+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1439, 'pbkdf2_sha256$1000000$cVuRQhjhS7yNiYILgHbiPW$cjpdmuKvFqMHjshGFA9W8JwT6JJ9wtQScoReNDLgaFg=', NULL, false, '03268488358', 'ARLLEI', 'MARTINS MUNIZ', 'militar_416726-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:32.332581+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1431, 'pbkdf2_sha256$1000000$dKTL1uLbszbm8Hk2mQNSpn$SMYJKwUYQL0k10EOYrXAu5ss75jp/ds+QiU1gM3AsnU=', NULL, false, '05567047380', 'CRISTO', 'JUNIOR DE CARVALHO SOARES', 'militar_416734-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:24.662413+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1444, 'pbkdf2_sha256$1000000$5QZ2fiMUMAtGmi1YK5d3cd$moxuLZEDh//CJI9NxNCOFcsX3/47jrWev2cLHQl4+ro=', NULL, false, '04854968362', 'EDER', 'SANTOS DE MORAES', 'militar_416744-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:37.047761+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1409, 'pbkdf2_sha256$1000000$6gjGUMyf2Wxk53W3tycSdV$BNc+jzEoLpYydxyqzX4ZJIjhu2fKnRgcYexApHvBey8=', NULL, false, '05663328335', 'EZEQUIAS', 'RODRIGUES CAMÊLO', 'militar_416758-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:02.530046+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1438, 'pbkdf2_sha256$1000000$TioodupPQsYLGrW5JyjkGg$PFlvK2A0eU8hlh2MmcNZdJMOLwwNQ2G8B1dtcRzuXrc=', NULL, false, '03897993350', 'FELIPE', 'AURÉLIO NUNES DE SOUSA', 'militar_416761-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:31.398652+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1435, 'pbkdf2_sha256$1000000$4wfQvD23udTx3K3GWL51S1$3+W/N81Y9yxlaH2sK0HwvQZhUbnDzPxZij46t8RtXag=', NULL, false, '05468182343', 'FILIPE', 'MOUSINHO LIMA', 'militar_416766-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:28.579563+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1420, 'pbkdf2_sha256$1000000$whpiQN4PBKeO8VGrmqXvM0$b2CwJmpkSQO+gN74CwTEe2JYDItEbAAlAz3bXFV9Pc0=', NULL, false, '07796562373', 'FRANCISCO', 'EDUARDO SOUZA SANTOS', 'militar_416767-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:12.984435+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1424, 'pbkdf2_sha256$1000000$RnHazcEO3R0XUBxLzdpGTl$jbKhTTrTR5v4ZK76YBoXs0JCANVKsud3Hu260oQfCOs=', NULL, false, '06388278337', 'FRANCISCO', 'LUCAS DE ASSIS NASCIMENTO ARAÚJO', 'militar_416769-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:16.755127+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1427, 'pbkdf2_sha256$1000000$N3oNtPDdcck1GytchtWCog$jEipDwpLKP7qrpss+3A+NxHkBr3/5rCFoODqin32O94=', NULL, false, '05170548338', 'GUSTAVO', 'AUGUSTO ARAÚJO COSTA', 'militar_417811-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:20.483146+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1411, 'pbkdf2_sha256$1000000$IyD4jSxvjUo7W7oW0HRj53$P+dvgZvx1K9eo/K0xyo7X45OTxF4xCUuo9iRb9iIIgk=', NULL, false, '04936413356', 'JOÃO', 'MARCOS DE ARAÚJO ESCÓRCIO', 'militar_416789-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:04.452796+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1414, 'pbkdf2_sha256$1000000$OGePAkyMwqlzK57ACe2hnR$UHWqKkSiHFI5yn3P4K0Scmengu7ftDOB1ZmFMRC/Xfc=', NULL, false, '04534414323', 'JOSÉ', 'EVANILSON DE SOUSA BARROS', 'militar_416797-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:07.314381+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1443, 'pbkdf2_sha256$1000000$4F8qeHHOuXvnBNXXeAaoAQ$Hj8xslSbpDHFhqKhsk1Xxxa2/18Kgfg9/yrbxaE4oPc=', NULL, false, '03590081350', 'JOSUÉ', 'MARCELO SOARES LEAL', 'militar_416806-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:36.119267+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1429, 'pbkdf2_sha256$1000000$o2JAspmKsOLpnMcZCzJNsP$WU3iy3mHSyvH694/SHpCgE2iKqMYoFcVrOstPANhxNY=', NULL, false, '06763067305', 'KAYRON', 'EDUARDO PEREIRA DA SILVA FONTINELES', 'militar_416811-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:22.628852+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1423, 'pbkdf2_sha256$1000000$OW1WkYRm5bHVzLxR3P9EHF$9uiaL3C6TJyQ3NMfg3LBWYoeQPrfuO8oB5DlkE7oMKs=', NULL, false, '06595908328', 'LUCAS', 'GOMES DE CARVALHO', 'militar_416817-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:15.818756+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1441, 'pbkdf2_sha256$1000000$FMMZzt3iqZ2N29Hv20A7wm$r6Vuf91WJTYHxIeNFY2FBAztJS6Vzj/oWOMJxvIJa8o=', NULL, false, '03899439325', 'MAIRON', 'ARAUJO DE OLIVEIRA PINHEIRO', 'militar_416820-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:34.271618+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1421, 'pbkdf2_sha256$1000000$ENxjJLgDdtIjwTcIuG29Lh$Mm29etzkczMxGmamMT5rwayh5/TpcAYRGm0ntDDeMFI=', NULL, false, '06142534388', 'MARCOS', 'ANDRÉ DE SOUSA LIRA', 'militar_416823-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:13.950224+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1428, 'pbkdf2_sha256$1000000$v97eVO1mxWNVu5qB5vf1Im$LQy2WNlN3uqSVOXNWafZ24f1weGTeR22BG/053SIELY=', NULL, false, '04829376376', 'MARIA', 'CAMILA LEAL DE MOURA', 'militar_416832-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:21.502508+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1417, 'pbkdf2_sha256$1000000$rnApWbRCySzIv2loQLbzZt$N7CzuvaIF2iTq+uvVR6VrE/96nUkx6IX7yM4veU1We0=', NULL, false, '07279427359', 'MARIA', 'CLARA ALENCAR CARVALHO BORGES', 'militar_416833-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:10.181962+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1410, 'pbkdf2_sha256$1000000$Ydtsf19MP7JHiyPf2J1Hrr$0gikSkhjpP0l0B72kLHYuoeUyCcOXcf7hvYbeGnPwYM=', NULL, false, '06038159363', 'MARIA', 'FRANCISCA DA SILVA PACHECO', 'militar_416834-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:03.478101+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1419, 'pbkdf2_sha256$1000000$Vzw9uPh9NmuIIOkHNM45su$qBG6cZ4Zcd/nOwXBtboQ1dTO1hUWYXduZxpvEjnCWZc=', NULL, false, '10982562470', 'MARIA', 'GABRIELA RODRIGUES RAMOS', 'militar_416835-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:12.043390+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1436, 'pbkdf2_sha256$1000000$SksSmzI8O2qyl77g9SgLB1$WaBXROWtaTvt2PJ6ObdfTa7yaqLvuYZ45Xz0FQjMq60=', NULL, false, '04011405396', 'MARINA', 'RODRIGUES MOREIRA', 'militar_416836-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:29.514845+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1440, 'pbkdf2_sha256$1000000$gdy3BcFK5ihaEfesvgzu0V$mtCgo2LfX1B2NVBUYq9rnzLTZ2MxlufhaQOUcdIvSlQ=', NULL, false, '07453276306', 'MATEUS', 'BORBA NEVES', 'militar_416840-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:33.265991+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1422, 'pbkdf2_sha256$1000000$c1D2fPye0A25HzbsrFs8VV$ibKrt2QSDN/rfaFWffjlfo6INleLdPfu/B28hQMxdio=', NULL, false, '07618815305', 'MATHEUS', 'CHRISTIAN SILVA MARINHO DE CASTRO', 'militar_416844-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:14.883154+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1418, 'pbkdf2_sha256$1000000$ROv1WyyWEc2sa7fSGSRAiC$o5FsoIusdQdGnvy6tImJt8U6GB8PgN6F330w951WfSg=', NULL, false, '06547953394', 'PEDRO', 'RODRIGUES DE OLIVEIRA', 'militar_416864-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:11.115093+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1437, 'pbkdf2_sha256$1000000$sOFj8RdTc3ePjR99CNjQzn$yHPOsabNZfzOAZ/FlnkBlj8lb45hNjorbgrVM2JdtX4=', NULL, false, '06168707360', 'REHIMUNDY', 'WRIKI SANTOS DA SILVA', 'militar_416870-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:30.453083+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1425, 'pbkdf2_sha256$1000000$GZmF6dc2rB1AHUnycgwtd1$UbwkVHYMntSZByThXfALtOnnqbsom1b+rrz13wSsBNk=', NULL, false, '06161776316', 'ROGÉRIO', 'AGUIAR SOARES', 'militar_416876-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:17.677920+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1412, 'pbkdf2_sha256$1000000$knAtH7Wl5t6aftB2YCwNxS$OkzK/PhMHB0VkGi77BBxZOA5Ov1F0kABAMZM99/YOsA=', NULL, false, '02933720396', 'ROMÁRIO', 'VIEIRA RODRIGUES', 'militar_416877-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:05.415118+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1430, 'pbkdf2_sha256$1000000$DqLLKuamhPUZ6uSPsMHYrW$Ymsyftms9C5G6IsZ2lPng/ZF/HuM8fzzLACp6uYyi18=', NULL, false, '07035291377', 'SANDINO', 'AVELAR HILL COSTA', 'militar_416881-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:23.631400+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1434, 'pbkdf2_sha256$1000000$B7z7DBzBKQ3maKv7uQ8bnO$WlK+GFDxLGS+RuQQzVoLsBvfjMOUDrKEAVKoWTF+oro=', NULL, false, '04290855326', 'WESLEY', 'KELTON PEREIRA DA SILVA', 'militar_416890-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:27.599302+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1449, 'pbkdf2_sha256$1000000$nzmSWu92yQvqQXaKiXUR75$GyB0pzZFiYkyF8k1zgQspwFNhtT9ThV+AvhURb3fWys=', NULL, false, '04472183366', 'ALLAN', 'GARDSON SILVA SALAZAR', 'militar_416716-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:41.685153+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1452, 'pbkdf2_sha256$1000000$qBBW8jxnsTtkRQXm4IIeko$9eciPhkgRAagWQoVRPV6MZqqkTWsStwsK4r03rUpt0I=', NULL, false, '09537981436', 'ANDERSON', 'BARROS PEREIRA', 'militar_417809-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:44.599218+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1454, 'pbkdf2_sha256$1000000$U74PT2ynYpoo8zCT0aQ0ej$gD3LZ9Sfb8GT+txuQQgeXLxEaRoc2fP4zlthwkJSaA0=', NULL, false, '07298940376', 'ANDRE', 'LUIS DA COSTA', 'militar_416722-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:46.812508+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1456, 'pbkdf2_sha256$1000000$48JTdvu5x6o8xFbk3ghxFB$ECbvR/ahAu4hXrTLvC6GOKGXcF67KQEy35e5KvpLJnc=', NULL, false, '04468016310', 'ARTHUR', 'VALENTE SOARES', 'militar_416727-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:48.919718+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1453, 'pbkdf2_sha256$1000000$vHPJsuCmGz2LFc7wjRY1UN$vQppmf+m80tWSJsa1qxMsZ0Fdhndq6CtLyQwBmTqY4s=', NULL, false, '07620876413', 'BRUNO', 'HENRIQUE VIEIRA LIMA', 'militar_416730-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:45.705908+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1446, 'pbkdf2_sha256$1000000$3zqkchD01K0xwyGxCNHbM0$f3k35Q85UpHs2CF59xyMTk6mgmmTNRZJ7GZN2slT2JE=', NULL, false, '07224816329', 'CAROLINE', 'MERCES DE SOUSA SANTOS', 'militar_416733-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:38.902113+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1463, 'pbkdf2_sha256$1000000$2cc7rS2Viav7eTAoYvkyuQ$tKmYBAGZ9eiWbvP82/SDc//GujwnCrmD6+UhWlW5wqE=', NULL, false, '04963537303', 'DEYVISON', 'DE SOUSA GOMES', 'militar_416739-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:56.261873+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1475, 'pbkdf2_sha256$1000000$lkw2FoKDkptX50ehiKJvcz$JzdJ+n2h05CgSJH9wuTT+NdKdZTe8cvIfcginucHZDc=', NULL, false, '06215908355', 'EDSON', 'FRANÇA SILVA DE SOUSA', 'militar_416746-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:08.005824+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1471, 'pbkdf2_sha256$1000000$Zl6jMkU18p59TU3S9pmVTy$HLF8mn/B4pXuzVxtFnO06eaQNbmxIGiTOHLMCb14xyI=', NULL, false, '05782560371', 'ELIVELTON', 'DO NASCIMENTO SILVA', 'militar_416749-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:03.931943+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1478, 'pbkdf2_sha256$1000000$VtZZtPeexLRn2ClGMbrlaA$c/JdaNG+UsInYIz2wLw8USqXLrIB3yrBHvH1p2JAldg=', NULL, false, '01412045320', 'EMIELSON', 'DE SOUSA AMÂNCIO', 'militar_416751-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:10.952909+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1468, 'pbkdf2_sha256$1000000$63aKMZdHFMKid8kFOliKI2$Xz9rMHYdO7KKSKB5wOHT9kQi5uuTj2FQEB5vrT3ThOs=', NULL, false, '60047300337', 'FELIPE', 'AUGUSTO PESSOA SILVEIRA', 'militar_416760-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:01.135433+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1458, 'pbkdf2_sha256$1000000$mJAeog3Osb1mXotIHaVdTN$QHIRrJ/RUhwFqKoAuh6Ivh/0hJRw7L+00agS7w+lphY=', NULL, false, '02142323367', 'FILIPE', 'MELO DE SOUSA', 'militar_416896-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:50.992153+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1472, 'pbkdf2_sha256$1000000$w6eJXRkLVE2x9NStT5qwNz$wgdx4cUUjy05jVnZ6ow6nEdBBI3FY3TwIyzA2m7ZOBo=', NULL, false, '08172458398', 'FRANCISCO', 'MARLON LIMA BARBOSA', 'militar_416770-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:04.884334+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1455, 'pbkdf2_sha256$1000000$r4sHQcoP7GcrxctK9arCCV$hMbMJuBJdo+0JHaKx82MCx/DpcMcLAD7UK+EBBzjJhk=', NULL, false, '06059073310', 'HYGO', 'JOSÉ MACHADO DE SOUZA', 'militar_416777-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:47.764688+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1445, 'pbkdf2_sha256$1000000$t2poxubkN2GJZaePLRAe6g$WPUTVfsODeSJz/WurMt1uwSV47phEmZVsU5cV40ohGA=', NULL, false, '03634592354', 'JÉSSICA', 'LAISA LEITE MENDES', 'militar_416785-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:37.979624+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1460, 'pbkdf2_sha256$1000000$oEFaFOhuEaW5mAfbdQeYMf$levQJ+xPPYt1gP36OUmXlGcjCeHaw1MlZehtSlZ8b00=', NULL, false, '05230516380', 'JOÃO', 'MANOEL PINTO ANDRADE', 'militar_416788-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:53.047126+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1465, 'pbkdf2_sha256$1000000$YZGAFU5a3tsfbDzsLYjqVI$9UcB2QpCvIEd4p+0UqyCsVM5sCoG5RakTmeY+4Ia/QI=', NULL, false, '39126220865', 'JONATHAN', 'MURIEL DA COSTA', 'militar_417812-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:58.263929+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1470, 'pbkdf2_sha256$1000000$xN2SxJ3Xi00Www6RmRSvZd$g69iSOAieJFUvwLfQLSPaxOxNIJxHV89Lb8emoy7Zrg=', NULL, false, '05681257380', 'JOSÉ', 'FELIPE ALVES SAMPAIO', 'militar_418118-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:02.984564+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1466, 'pbkdf2_sha256$1000000$K22tMC5lo1DH7V975pjKk9$FerdRcERbbOhyWZLd+jphm721nFjKVvMd01cwpRAhOk=', NULL, false, '05441806311', 'JOSÉ', 'GUILHERME ALMENDRA NEVES', 'militar_416798-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:59.229205+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1473, 'pbkdf2_sha256$1000000$Qy8qOP6Og6BfgOJkju0wnG$mwfYfZ9OPW85y9UjdguMGRbthbg6zxzgwLqIg9soj2c=', NULL, false, '04905120381', 'JULIO', 'RODRIGUES JULIO', 'militar_416807-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:05.832920+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1448, 'pbkdf2_sha256$1000000$J9r7JybnhAh2vk74oaX7ZB$bcXmWm1cTSHN2k9/5oJcm4aKipuA/U1iWVkoqFeopcU=', NULL, false, '04243057397', 'KAROLINA', 'RIBEIRO DE OLIVEIRA', 'militar_416808-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:40.748026+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1476, 'pbkdf2_sha256$1000000$2oAP4th2qHGMkpNaQYQDWh$041bsH3ttSbOzS0rCa2tHi21szn4T/Zu87LXnLxtd+g=', NULL, false, '07392643380', 'LUIS', 'CELSO DA COSTA FERREIRA JUNIOR', 'militar_418114-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:09.023464+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1477, 'pbkdf2_sha256$1000000$yqJ8rYhcgbyF7wVKHTPbfu$wXR12npAbSbcFixt12FN/KHp5m3WbcFrYiu1XDy7H/g=', NULL, false, '62006029304', 'MARCÍLIO', 'MADSON DOS SANTOS SOUSA', 'militar_416822-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:09.980903+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1467, 'pbkdf2_sha256$1000000$gDAYJU9LAfcmxkbSWoWQPp$CWwOg9n+h3nONLw9fIHXsSRQvMnVceyigy7G33lafJo=', NULL, false, '05942369321', 'MARCOS', 'VINICIUS COSTA DE ALENCAR OLIVEIRA', 'militar_416829-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:00.194822+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1451, 'pbkdf2_sha256$1000000$EnWZnzUTLCZkcWrKF5aUeb$/oWXFtz47gvU3uJ5lCBRYbeBWSsP0PtBEJNwDH0Bbx4=', NULL, false, '05088754396', 'MARCUS', 'VINICIUS DA SILVA SOUSA', 'militar_416830-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:43.685868+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1474, 'pbkdf2_sha256$1000000$kHzKq6YU8cOMn6rxernivr$ObgUiZYjn+nZw4HeNYafaMWYXC1Z4zc0PjMEnBfChwE=', NULL, false, '06797138329', 'MATEUS', 'CAVALCANTE DE MOURA', 'militar_416841-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:06.848209+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1457, 'pbkdf2_sha256$1000000$xH3HNvr9FJZQx8FQ39wAUc$a+zPKhCwfIrGjUwKiGYHCBaBZJ/wzoObafRa9j4mnpE=', NULL, false, '06677094367', 'MIGUEL', 'CAMPOS DA ROCHA', 'militar_416848-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:50.016385+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1462, 'pbkdf2_sha256$1000000$G8kfz0EQ9Qn8nq9Ve8jMkv$bQfIhslmsMKZEuTdmRwshzOb+v03+3cNfCkureG2CNU=', NULL, false, '31501118897', 'NAOMI', 'LUZ MARTINS E SILVA', 'militar_416853-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:55.297811+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1479, 'pbkdf2_sha256$1000000$YZ3HjXSSOXzKS5vjFe1VlJ$TVRJmVD53P8RKS0WLAah+RquBdLH1MdXFLNdkvz3sV0=', NULL, false, '04453335377', 'PEDRO', 'BARBOSA DE CARVALHO NETO', 'militar_416860-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:12.063823+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1447, 'pbkdf2_sha256$1000000$VDxtTWNmXroC38HKqnY3Yj$GVmjXWu7t66h89v5N2Jd/FHZcR/NjXnXRV5qFP2cvv4=', NULL, false, '01026450357', 'RAIZA', 'LORENA RODRIGUES DE AGUIAR CARVALHO', 'militar_416867-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:39.833819+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1459, 'pbkdf2_sha256$1000000$9IuLNJPKu10sWqQ8nebNCA$JnJdI0hDVOqjZlLdQCoCnVx+33bZ8nb99s4KP+HS66Y=', NULL, false, '06055319357', 'REINALDO', 'MELO DA SILVA', 'militar_416871-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:52.016742+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1450, 'pbkdf2_sha256$1000000$9uiNwSD3bLUboqHg2tbHIC$5SNTnHXUw38uhuGF5NNzOMGhAmzLE6OP0iAaOYID4n8=', NULL, false, '06505869301', 'SAMUEL', 'MOURA DUARTE', 'militar_416880-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:42.719546+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1469, 'pbkdf2_sha256$1000000$QeY5AuwF91CEKIvGsRymua$aKzS8epFRfANp/8GbeMaiYS3d6FMso0qaoR3MuQ3YOM=', NULL, false, '04284774379', 'SERGIO', 'MATOS FRANCO', 'militar_416882-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:02.046532+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1461, 'pbkdf2_sha256$1000000$p2JSCHcOeM42uak3aeTQj7$Uz7VWvdOJd3QOLkNdiRwk7f0XiZiAIK2QdAkxc6GUhE=', NULL, false, '05140067307', 'VALMÁRIO', 'SOUSA ANDRADE', 'militar_416887-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:54.248830+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1464, 'pbkdf2_sha256$1000000$LjxNuw5v7LNobUkforQBja$SGxeUefEailFS3qTnxl00j0D/Ni+Y4bceIFX22eWT4Y=', NULL, false, '04224399326', 'YTALLO', 'ENNOS DE JESUS SOUSA', 'militar_416893-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:57.252125+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1491, 'pbkdf2_sha256$1000000$ioBgwFtmtsPbo5w2YVK3Ag$HZoAKiQiDHq5Wg7sIt40bhIrKvtnRW31zqJYs48xRAc=', NULL, false, '07463522393', 'ALYSSON', 'JORDAN DA SILVA SAMPAIO', 'militar_416719-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:26.213272+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1514, 'pbkdf2_sha256$1000000$gjSgSSQEjMqq6TzidnlW5L$qIhSJ3492x/0bNKrEBWXSN7DcTgoBcd35QUOnTPiEEA=', NULL, false, '08120939336', 'ANTONIO', 'MARCOS VIANA FILHO', 'militar_416723-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:48.951929+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1494, 'pbkdf2_sha256$1000000$RspqovhNBNDQjamdGzUatY$iSSqq0bxd2koir7wpy6K4QSY4SLKgB4dk8OFZlz5vZQ=', NULL, false, '06673629320', 'BERNARDO', 'LUCAS RODRIGUES DO NASCIMENTO', 'militar_416728-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:29.100195+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1499, 'pbkdf2_sha256$1000000$6yxeYlfco64StVcjI5YyeF$yH2DGEqUvmb/7279dBg1/fUqdIQoJZXHR3TCYb7U/Ys=', NULL, false, '05726486340', 'DIEGO', 'DE SOUSA BEZERRA', 'militar_416740-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:33.968818+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1513, 'pbkdf2_sha256$1000000$fRWhFHqHpgo1VxaqCqVAkC$xiG7/y3M14cqZPjUH59ay6zhqHK6ybRBzrGOZh5NVcs=', NULL, false, '06537209390', 'ELIESIO', 'ALVES MENDES JUNIOR', 'militar_416748-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:47.967161+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1484, 'pbkdf2_sha256$1000000$OylLnD1lgGBPg7hFpOEglf$mgyquPlTNdkfZMAXqN0l6E0vDVSf0NeHRZ3Z+UcxsFs=', NULL, false, '04794064306', 'EVARISTO', 'DE BARROS ROCHA SEGUNDO', 'militar_416757-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:17.273952+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1481, 'pbkdf2_sha256$1000000$GRAfRjkq4JKfd1vtcQ6flj$XUaVljfZDPaVzMMqzg9X8kc8GDM401kENUERQpDAOmo=', NULL, false, '60009346376', 'FABIO', 'DE SOUZA CLEMENTINO', 'militar_416759-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:14.095901+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1495, 'pbkdf2_sha256$1000000$TiSgD75dQxPWek682B87jj$1RntbVb2w26jNiRE5TMTE+ltjo45AtsScL4tVoMZR3s=', NULL, false, '00463662377', 'FERNANDO', 'DE OLIVEIRA SILVA', 'militar_416765-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:30.114922+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1506, 'pbkdf2_sha256$1000000$fnWdsEgQJzeGTAsyVJKctg$FNG2iqlBAkU9soRkX8PiE84G6AzHoS8kIAzWOU/mHRM=', NULL, false, '05463774323', 'GUILHERME', 'FERNANDES DE SENA SILVA', 'militar_416899-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:40.937406+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1501, 'pbkdf2_sha256$1000000$aXXCYUJBcOflSfNmPhXSYV$UJVvbei4cIvV3ijNY0mxYEZu1jrxsAc4OTyEVUkuA6o=', NULL, false, '04302565314', 'GUSTAVO', 'NUNES DE MOURA', 'militar_416774-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:35.862702+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1508, 'pbkdf2_sha256$1000000$xVwqA8vW4vGV99ZIZ5a9wZ$TRhr295C0yHwW7PVZ1GBnu8EdWMhuG+BHYmPDa6/ZnY=', NULL, false, '04723655336', 'HARLLEY', 'RAMOS DE SÁ', 'militar_416775-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:43.134817+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1505, 'pbkdf2_sha256$1000000$kT6Lzacyq75vOcVUeoaMbZ$sic4WFJUcRV8cknTYMRD9ib+/2PRXzW22bJ3Qh4q+jU=', NULL, false, '06620335314', 'JEFFERSON', 'OLIVEIRA DE SOUSA', 'militar_416784-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:39.895739+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1490, 'pbkdf2_sha256$1000000$2UmCtyZ7C3js0MtEFov8dR$gPJIC9+3mIFpClpZJAuzhUTJdpZu08Likfqf/LFp+h0=', NULL, false, '07280329373', 'JOABE', 'ALMEIDA SOUSA', 'militar_416787-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:25.236092+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1493, 'pbkdf2_sha256$1000000$sofXpK5pNlJmcRzCMQ0XJA$1kr6AwBSwvRPcoTKBVZxE4UIEwapyENHZ4MlB5zzkqM=', NULL, false, '08625777309', 'JOÃO', 'PEDRO SILVA ROCHA', 'militar_416790-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:28.148936+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1504, 'pbkdf2_sha256$1000000$pDhbuAZaEUmSqkvurYzeoi$wxeyBkIPp7f1UliivRhrFIsmruh//SfFw6m4227eXko=', NULL, false, '04427657389', 'JOSUE', 'DOS SANTOS OLIVEIRA', 'militar_416805-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:38.914025+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1489, 'pbkdf2_sha256$1000000$l6cUFpMKTLxV1ISQVP1VBn$/Clf1FE8qO4UGV1Hez5DhXPK6Hy9AldKGI2/TJYAWuk=', NULL, false, '05747299336', 'KAYO', 'HESDRAS PINHEIRO SILVA', 'militar_416810-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:24.231896+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1510, 'pbkdf2_sha256$1000000$mVDv4i7h8QxmKERn62rT4m$4dy8vh3EiphG8He4464VVcrCExTAIKl+hpLHVN5eIeQ=', NULL, false, '07068275389', 'LEONARDO', 'RODRIGUES GOMES', 'militar_416813-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:45.012946+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1486, 'pbkdf2_sha256$1000000$eoobfHpbTkSnHnVYeQmcut$qVgl8yOg6HIQf5UdMyDd9IHvuLtqZmrpy8GJnQSc0ro=', NULL, false, '60896185354', 'LEVI', 'BARROS NERY', 'militar_416814-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:19.882813+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1483, 'pbkdf2_sha256$1000000$uHgJmJVH6buKakJrCEa0ub$3F8w3s13efMi8eGVEPmOSj+BIb37Qx/ipbUQkyfBzpA=', NULL, false, '02628924307', 'LHANA', 'LETTÍCIA ARAUJO DA SILVA PEREIRA', 'militar_416815-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:16.157346+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1503, 'pbkdf2_sha256$1000000$qdmCFfUIdos2qSHLSmihUY$wZtZGpSndM+fW8IEHtEyKhDmU5ve21qvAJIRTvai9K8=', NULL, false, '03259449388', 'LUCAS', 'GUIMARÃES DE ALMEIDA ROCHA', 'militar_416818-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:37.883306+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1497, 'pbkdf2_sha256$1000000$j5m9pAk9jm7TPqRwn5IvJC$zpmBBkIR4StXt8bug2jg90SvEN5L/mL1E9GalEeK3kk=', NULL, false, '01977996396', 'MARCIO', 'MENDES DANTAS', 'militar_416824-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:31.996319+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1511, 'pbkdf2_sha256$1000000$5Vc5jKKFcnXNotOb5MFOMZ$lmxZVnyahyILhNxHaT0YMj7Whe3fMvC39RcfbDOtlfI=', NULL, false, '05177433374', 'MARCOS', 'VINICIUS PACHECO SOUSA', 'militar_416828-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:46.083594+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1515, 'pbkdf2_sha256$1000000$A2YbwYcBtyhhpw2Z86LyaU$NbEO/XDmq2inJboafDBhgVkmEZOjuyaStE1UOQUpuaY=', NULL, false, '08102500395', 'MARIO', 'PEREIRA DA SILVA', 'militar_416837-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:50.112518+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1500, 'pbkdf2_sha256$1000000$azUblqJ7kNNr31fvHrFuaD$8IBwhErf9TP7YmAduUAYU9yjK63LfYbjTd+iM28Yt20=', NULL, false, '03899440331', 'MARLON', 'ARAUJO DE OLIVEIRA PINHEIRO', 'militar_416839-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:34.940209+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1502, 'pbkdf2_sha256$1000000$PbQ8nratpxx9wOBgYUGzjV$GWY7YbF9RURUxzPuyH/3EGEbgNo8xVCGiPO4lvpzJWM=', NULL, false, '96243937372', 'MÁRNIER', 'BEZERRA ROCHA', 'militar_416838-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:36.831794+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1492, 'pbkdf2_sha256$1000000$DQUp02rezII8fqHF6g2NuX$hNxzWfiGI59mzBYBMgX4hC/MKz0TZzJTpr3t4fTiWvE=', NULL, false, '06981885352', 'MATHEUS', 'ROMÉRIO SOUZA DOS SANTOS', 'militar_416845-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:27.217874+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1496, 'pbkdf2_sha256$1000000$TO7OPDFyXmCAb8O2kbKP6u$R2PGircCmPWNXVAWHx944a1yJJk56x6SMa/Q/hq5f10=', NULL, false, '06965905301', 'MAURO', 'GUSTAVO GONZALEZ SAMPAIO FILHO', 'militar_416846-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:31.068187+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1498, 'pbkdf2_sha256$1000000$Dl0bYAiKUeGTpuafqtxesS$li6DSCVgoV9llfqcfCkUJ8AZrFoqC8dglG4ivul6JpU=', NULL, false, '07818318305', 'MIGUEL', 'ALVORES LIMA NETO', 'militar_416847-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:32.969706+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1507, 'pbkdf2_sha256$1000000$yJtS2VaUhnIHllIXXEAQGL$yx5Ols4OHRsKn6KHIix+l8vMsUeRF+s9jniRt6Ys34o=', NULL, false, '06788273383', 'MIGUEL', 'DOS SANTOS ARAÚJO', 'militar_416849-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:42.035724+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1488, 'pbkdf2_sha256$1000000$eDCXJjcztI07KqW7jvqA4z$RNScvFjvVJZ+UxM6iTsIgYAeW1+SS4PEC6AlidzUyMo=', NULL, false, '06361213307', 'PATRICK', 'SANTOS BRAGA', 'militar_416857-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:23.135255+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1485, 'pbkdf2_sha256$1000000$KWdQw9FYaZkLdHDptiOIZ0$ZEQMnG/BwcWbPMESzSiM6PQjy33qK/6zJV76chw12Mc=', NULL, false, '01992056390', 'PAULO', 'HENRIQUE DA CUNHA COUTINHO', 'militar_416859-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:18.319107+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1509, 'pbkdf2_sha256$1000000$W1xosuQikpVz5zSVlMuj27$MuS/60P4zsvPCDO7mhikVb8DZ83qeFH1nrwuRgqiu20=', NULL, false, '07026743384', 'SAMUEL', 'MARQUES FERREIRA', 'militar_416879-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:44.071888+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1512, 'pbkdf2_sha256$1000000$2PiRyf1BKanJlTrk9gLFbw$6Bw8Ih68D56v+IHIUcME/618E04Pr/cInX4RmeyVJ0E=', NULL, false, '05988809332', 'TAMIRES', 'SANTOS BARBOSA DOURADO', 'militar_416883-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:47.051884+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1516, 'pbkdf2_sha256$1000000$wRAFgy8t1Y4sNuQAssdofP$I9opDlcQIg6ZjTVtQoxhEaHsRHtVVhp3oErgPZr+Xj8=', NULL, false, '03435191350', 'THYAGO', 'LUIZ DOS SANTOS SOUSA', 'militar_416886-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:51.390780+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1487, 'pbkdf2_sha256$1000000$MWamPoUheM4GHi20zN6gIX$zebQqB/hbKfo8+2XuioSb2gRvXb2TY2DTveCiLzITok=', NULL, false, '04881704354', 'WESLEY', 'RESENDE DOS SANTOS', 'militar_416891-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:22.034346+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1519, 'pbkdf2_sha256$1000000$73iR36CMMSpw8CHhvKfmyj$leK7AYRNdu7yFzMEv4MPQbrkY/bdYC9IWQ3S7B7LEpY=', '2025-07-28T13:34:22.883959+00:00', false, '07031461308', 'ISAIAS', 'SILVA CANABRAVA', 'militar_416780-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:54.668601+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1538, 'pbkdf2_sha256$1000000$G9DDff3fzFFfbwakahucCQ$iiBT5Ge8G/XN5yPO2cUlGOWDkYoWWNn4r4aC2XR5WR8=', NULL, false, '02505498326', 'DANIEL', 'MARKUS GUIMARÃES MIRANDA', 'militar_416735-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:12.760035+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1541, 'pbkdf2_sha256$1000000$yPAvl9WHg5jculol65lNHo$2PLShReHNEsM1U5e2mVY23nSmOlXKLHseocvGn8n1yM=', NULL, false, '03490474309', 'DANIEL', 'VICTOR CARVALHO', 'militar_417810-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:15.529709+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1533, 'pbkdf2_sha256$1000000$SGznpCqBdED3LJh9FOxP6r$uKnjiwrspEMxwbXzavQPLyv/EMlBaFg4QM2NYJW1O6w=', NULL, false, '06999640327', 'DÁRIO', 'GUILHERME ALVES DE SOUSA', 'militar_416736-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:08.143251+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1532, 'pbkdf2_sha256$1000000$kI1D8jKgH3TYEQb7cAFLqT$K0ebPbjpIWWbaKXKDJT5+avyYTFS65PGOuUXD5XPeiU=', NULL, false, '02485831319', 'DEISON', 'KYLLER VAL MORAES', 'militar_416737-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:07.203964+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1550, 'pbkdf2_sha256$1000000$IW4AH2qEY6YVEyBB6BClmd$nTOfb/pACUg6IFfMZdh2rYet85Ga2/v+gj16ITr3Wao=', NULL, false, '03125843340', 'EDER', 'OLIVEIRA DE SOUSA', 'militar_416743-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:26.332985+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1544, 'pbkdf2_sha256$1000000$DvxjLGKmg4gJjCFZKcFuCT$UG86GgBHRYpDk2v+VS7axACwzs70TvUfxM+R0pk17I4=', NULL, false, '07035908390', 'EDIEMERSON', 'SOUSA BRITO', 'militar_416745-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:18.360820+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1522, 'pbkdf2_sha256$1000000$7aozq1pBo1GGQkes3kIkSM$wRwAOUnykbXQdk2+JE5DDM2eCQO0uRApGkprEFWGzRc=', NULL, false, '06792402338', 'ELYDA', 'RAVENNE RODRIGUES E SILVA', 'militar_416750-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:57.600943+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1548, 'pbkdf2_sha256$1000000$GUxzT1EawdNJRrsFfK9TvK$Rcm6mSXzJYxx4MT4V1zNmWG5iZeT+4kYK71tvo+L8CE=', NULL, false, '03731892308', 'EMILIANO', 'MARQUES FARIAS DE ARAÚJO', 'militar_416898-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:24.368367+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1551, 'pbkdf2_sha256$1000000$fxEZMplZASQiWI5YwJ8Ek6$93VCLsTYImpzd9555wbyFJF1e8bUGbbqLp2DVEBdnHU=', NULL, false, '06798646360', 'ERIC', 'FELIPE RODRIGUES DA SILVA', 'militar_416752-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:27.272372+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1529, 'pbkdf2_sha256$1000000$VXOMcwdRD6dQys2RnkMGyO$J9FbTlGzW9UT7VGM1h7zwDyDr6/D24lVnVQualjoo5Y=', NULL, false, '04346258336', 'ÉRIKA', 'FERREIRA E LIRA OLIVEIRA', 'militar_416753-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:04.398530+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1549, 'pbkdf2_sha256$1000000$PRVEbrsnIXUUtfmyJ3dhIG$CneFQvsuUeJsahMGk5jEXTh12RpNadYUGabHMGd4wR8=', NULL, false, '07078992300', 'FELIPE', 'DA SILVA VILELA', 'militar_416762-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:25.364014+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1525, 'pbkdf2_sha256$1000000$CepcoDsoW41e3zt2kVqIIw$St9iKVq/icLukvSqyPUspxV++VzNAe+/6KzofPNOnfc=', NULL, false, '04959974397', 'FELIPE', 'DE OLIVEIRA MATOS', 'militar_416763-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:00.623180+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1517, 'pbkdf2_sha256$1000000$JCbXAHrLvyCc277kDHpqn7$9JKlh6S3drYJxL6YIbEVpt0Z/Fmc/PH4VZ62gKAFngY=', NULL, false, '02971108376', 'HITALO', 'DA SILVA FREIRE', 'militar_416776-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:52.747161+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1536, 'pbkdf2_sha256$1000000$8cPdnDhDwIDXsFVTOwXkPC$tfyq6cFiIxovTLFOT62eO93vDExVShsQ/u5UKE3AtNY=', NULL, false, '05201731392', 'ISLAIRAN', 'SANTOS DA SILVA', 'militar_416900-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:10.919783+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1547, 'pbkdf2_sha256$1000000$Uaoc3wunEp4058BiwFcvgh$8dhWH51WWodsXh+SG+A00et/OA9gjtRK0twtwRNGLmY=', NULL, false, '06222264360', 'JEFERSON', 'DE OLIVEIRA LIMA', 'militar_416783-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:23.152750+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1526, 'pbkdf2_sha256$1000000$jTKnG80Bau7p8eEE71mN0u$FWK3Z5Emt/dq+jMvOxAsRrftwV+bMHXOTFTvZ8grmuQ=', NULL, false, '07332473348', 'JOIANA', 'NARA FELIX GRAMOSA DOS SANTOS', 'militar_416793-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:01.572234+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1530, 'pbkdf2_sha256$1000000$Tu9kpea81KRwxcBikpIc7o$PuByyUZHNlhHlpjirfGMuVNU8H5nqpQIJXsq95iQQWg=', NULL, false, '02918696374', 'JORGE', 'LUIZ DE MELO ARAUJO', 'militar_416794-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:05.330377+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1528, 'pbkdf2_sha256$1000000$iyWH4vBHCN3ZBHup8G8JAx$QM2LdsTgaRJEjSKznCpLbrvXs0GyCTOCFkiQEIAFuRQ=', NULL, false, '00303459360', 'JORGE', 'LUIZ SOARES AZEVEDO', 'militar_416795-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:03.444841+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1524, 'pbkdf2_sha256$1000000$gjPlWFEb6ThUpZsxVT9iFJ$SRVS/a2j1jpDrNQHis+A2ZMeqEzaCZxofdM0DAdlyDQ=', NULL, false, '06099325352', 'JOSE', 'WANDERSON DE MENESES MORAIS', 'militar_416800-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:59.546464+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1534, 'pbkdf2_sha256$1000000$rFIhCC0gNb5YLiKv2tKz4U$30V8UfT3ao1rGkdLNBIde75DeITzF6YmvnWjP6Y0j1Q=', NULL, false, '07568522342', 'KAWAN', 'MACHADO DE ARAÚJO', 'militar_416809-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:09.062678+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1539, 'pbkdf2_sha256$1000000$sNx4TeTwfFsBIo1GwP8tRw$RAeBNnWxh247dIQRLpMAeN9EPk0vMaP7NOauoMU5Fh8=', NULL, false, '04302629304', 'LAERTH', 'DE JESUS ABADE', 'militar_416812-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:13.679680+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1518, 'pbkdf2_sha256$1000000$CKejp9aSJ7vyCldgl4mr1A$11TPJKTygeT8zw9ru1lnapvJBf2pplHWwoTwRQYbuCU=', NULL, false, '60663127319', 'LUCAS', 'DE OLIVEIRA SOUSA', 'militar_416816-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:53.710398+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1523, 'pbkdf2_sha256$1000000$MkTmSStkoQ9NTaKkIGTMN7$syJGbadu7sup35hvTifPEjI4XINdsIzcN8AIp4F3is8=', NULL, false, '06779756350', 'MARÇANIO', 'ALVES MARQUES', 'militar_416821-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:58.536255+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1531, 'pbkdf2_sha256$1000000$r6SCpLmwBVxH05ekkTiWhR$ZMGWVQ/+6Y6WfpuB0FzL5OL0pzxXmww1bcEludoD+DE=', NULL, false, '11376407400', 'MARCOS', 'GOMES DO NASCIMENTO FILHO', 'militar_416827-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:06.277463+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1543, 'pbkdf2_sha256$1000000$7aah6Nk4PTnzDKIHbalePr$irljVZkgC1Nn43+tIJC7rTAsvXR6k5R6kgwmEj1FStM=', NULL, false, '05498402309', 'MARCUS', 'VINICIUS SILVA MOURA', 'militar_416831-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:17.410751+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1537, 'pbkdf2_sha256$1000000$KI3oSemu4UHuzG7K7QqNkp$tQ6otRb98D6DMDo9us+XyX+f+eZqhmiGb3ROSox3DEA=', NULL, false, '03956662369', 'NILO', 'LEONARDO DOS SANTOS CRUZ', 'militar_416854-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:11.837140+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1520, 'pbkdf2_sha256$1000000$pe2udlz5VaoBtCayFhkJGF$6PcafUgA3Sac/7l/i4sv7A0bqHRhA3Zov0R49fCm93c=', NULL, false, '05055143380', 'OZIAS', 'GONÇALVES LIMA JÚNIOR', 'militar_416855-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:55.603580+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1542, 'pbkdf2_sha256$1000000$S8A2Ley1DaOVdpOGnMTfYf$YQxQpzA1GDlQ7n3ZL4MH0DCGZ5nj6VUCwJPTgOFx5wI=', NULL, false, '07215696413', 'RAFAEL', 'LOPES HOZANO', 'militar_418120-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:16.450030+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1545, 'pbkdf2_sha256$1000000$OQvaNOm92rINqIGrZdYgEv$ghiDPz5ny7fsoo82nEq+EUa5ua7OTzJkc2kWs9WvwSo=', NULL, false, '08140821306', 'RAFAEL', 'NONATO DE SOUSA', 'militar_416865-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:19.427441+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1546, 'pbkdf2_sha256$1000000$raLZyUcFQSiOjevT7ks9ky$LcPjElGVkIJUsbjnjFYF/uFf/+r4BE+Mp+gHbSkCieI=', NULL, false, '04334041329', 'RANIERY', 'SANTANA DA SILVA', 'militar_416868-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:20.766676+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1535, 'pbkdf2_sha256$1000000$iUCQHRxcAZz3mx6arSseIp$bdAOqwRGXy2biot5ZtXDyu0mw8sjgos35H5N4M3KMBg=', NULL, false, '06243722350', 'RENATO', 'ALVES SOUSA', 'militar_416872-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:09.988923+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1540, 'pbkdf2_sha256$1000000$kF0KDIzJFZDRRHWLkSrGJ2$VmO8xmtwi0nmgd7WNdtmsiD1OGomiw3TmCWVkdoRcWc=', NULL, false, '05492908340', 'RICARDO', 'ALEXANDER VIANA SILVA', 'militar_416873-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:14.598906+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1527, 'pbkdf2_sha256$1000000$8cvwAzj7s0QN48H8HptoWD$LHukUWpAzeSQP1z0MjIdH45g2xiXHSvZrqjOMiUZBXE=', NULL, false, '06825488392', 'THELIO', 'MENDES DE CARVALHO', 'militar_416884-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:02.498140+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1552, 'pbkdf2_sha256$1000000$eeNQUimi4dRwWQ8xxcFphI$q+Y6/Ehl7hZy1wng2mTre9OxEEVdqj7ErFUcTYQrbXo=', NULL, false, '05587419320', 'WILLIAN', 'SANTOS DE CARVALHO', 'militar_416892-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:28.235043+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1291, 'pbkdf2_sha256$1000000$wGk7WKmKPg5Ntx7YUxKAFE$pPZKd8o5q6aLj8haLr8YwAI+yViXe+2MUq/Kds3mdfQ=', NULL, false, '01692457306', 'Adoniram', 'PLATINI Moura Martins', 'adonirampm@hotmail.com', false, true, '2025-07-25T15:51:03.886485+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1303, 'pbkdf2_sha256$1000000$IhWqviTB2HH5apUSjCzOVG$U+tRO9S1kfA0WVJrfJzuFwWXWKbQ3DgZ6lOH+5Zvo7A=', NULL, false, '02696678308', 'Alex', 'Gonçalves ALMENDRA', 'militar_244844-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:51:15.316870+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1199, 'pbkdf2_sha256$1000000$EtBIX132o30jDeik0um30V$FdgrERvOlxrGFW/tF5/5q1B4bGEyqVBL6J1KhEz65jY=', NULL, false, '93269110391', 'Ademar', 'DAMASCENO Soares', 'militar_354524-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:32.236008+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1183, 'pbkdf2_sha256$1000000$jEq2NKukH4Au3GBJNGRpHh$o/cbgJJruExzOAa8ERicZjdvV5dPAUxZa8TX0ppx3AI=', NULL, false, '01729739377', 'Alcimario', 'Fernandes Lima DUARTE', 'militar_343629-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:15.972343+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1149, 'pbkdf2_sha256$1000000$wm8zsHov7g8HCEhAeX7dYg$uhaJT2yxyNOn/3AIPKI+9GXvq6iXlurr4iHZNZotU98=', NULL, false, '39540200334', 'Antônio', 'José de Melo LIMA', 'sgtmelolima@hotmail.com', false, true, '2025-07-25T15:48:41.091117+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1226, 'pbkdf2_sha256$1000000$lPysAZpEeoVuyahFdFbwQw$zDrkFuMztnfGPFKLm+Yb5gdhUCmN9Fa6e3oQzjb1Lck=', NULL, false, '47081775349', 'CLÉBIO', 'Araújo de Queiroz', 'militar_082772-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:49:58.890092+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1373, 'pbkdf2_sha256$1000000$JCciU06xxFcngQXPU5m0Iq$CJyyIDc/OW+F4e6KRNn+x1ZNtDG25EOtYwCBUfYZaH0=', NULL, false, '04500165363', 'Albert', 'Moreira de MENDONÇA', 'militar_332422-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:52:24.381326+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1372, 'pbkdf2_sha256$1000000$PWD57ETQQw15YpfGu7IEnW$pra0YJuIaycC/vWbmA1UDsMdIIXBrUtfO0LQBq7qU60=', NULL, false, '05799885384', 'Alcenir', 'Augusto Barbosa DORNEL', 'alcenirdornel@hotmail.com', false, true, '2025-07-25T15:52:23.399512+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1580, 'pbkdf2_sha256$1000000$no43f3AHzNSiDUaYGJZz4B$vhhIg/+9oBingxqCWa9TLHmD3VFiYWK6Yg0WMdXw6cc=', NULL, false, '00932484310', 'ANGELO', 'JOSÉ FONTENELE DOS ANJOS', 'militar_433915-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:56.435263+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1557, 'pbkdf2_sha256$1000000$tscHITXlw9WbRuovUralkh$yvpVRvuXB5hce06bQWK0f/Nv+tf2ReoNpeVUIRAIzfQ=', NULL, false, '05960674378', 'CARLOS', 'EDUARDO ALVES DA SILVA', 'militar_416731-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:33.174626+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1560, 'pbkdf2_sha256$1000000$5ON8Fr1m74t3Zy4HxtflVu$fF7ZgMFOqdV2wCdKYjxS0A43OOq7P0vZbV3vADWOdhs=', NULL, false, '05400829376', 'DOUGLAS', 'CARDOSO GUEDES DA SILVA', 'militar_416741-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:36.169792+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1554, 'pbkdf2_sha256$1000000$oQ3Ipm3LJIVurBjHrLJxLR$dKLXKlKc+wAa4BwS/LQNVgHqeHSqawTc/5ELMuf8FH0=', NULL, false, '05811629354', 'EDUARDO', 'MOURA DA SILVA', 'militar_416747-3@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:30.240533+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1570, 'pbkdf2_sha256$1000000$GAfHAgNkwxkdgWmmIve3mc$YXFeSqj4biGF3pwq34loK8OKEWJ/GcHhyqbsh4vRjDE=', NULL, false, '04175843345', 'ERISVALDO', 'DE CARVALHO FERNANDO', 'militar_416754-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:46.773497+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1561, 'pbkdf2_sha256$1000000$N6Mz11dtjycT2WMp3PBM7K$1GHRek8dy9P9E3JT5vo9rDrwts8ZeTqy0XsRwOBvgWA=', NULL, false, '04646743361', 'ESMERALDINO', 'SOARES GODINHO FILHO', 'militar_416756-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:37.534626+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1578, 'pbkdf2_sha256$1000000$nr2SAUR2MN0TcCQdJYoaj1$7SHoxeJvPC3Oi+93brVszSeXQxr2DCMxYMcbcugyWS8=', NULL, false, '04601592321', 'FRANCISCO', 'FLÁVIO CABRAL LEÃO', 'militar_416768-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:54.373668+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1572, 'pbkdf2_sha256$1000000$teHHQTL2UVMw3Hxc6t9oX7$U50Au1oIa+63MSBAocznt8kdq4lURbj1k+nTYoXxJO8=', NULL, false, '04107591395', 'GABRIEL', 'SIMPLICIO DE ARAUJO SILVA', 'militar_416772-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:48.662426+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1577, 'pbkdf2_sha256$1000000$A3F2nzHGxTO0WFJ2ZtW2j0$33CGNSb4rbLhlniQuyrB9MEhSxH0fCQRmHIlplJ0kjQ=', NULL, false, '06216999346', 'IAGOR', 'DE ÍCARO SOUSA MACHADO', 'militar_416779-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:53.397186+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1576, 'pbkdf2_sha256$1000000$EaBjbGBtJwpA8E2om1woD5$pCr/PvBI7FAjsJZTg3WgeqV89I8ECRrreZydZDseD2k=', NULL, false, '07669298413', 'JACIEL', 'JOSE DA SILVA', 'militar_418122-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:52.448329+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1575, 'pbkdf2_sha256$1000000$5VhteHEg6oVRXVzsB3dBhO$YGynwfBVozWhkh2QcE5CgB324ZA7yBkj2QW9y1ifG+U=', NULL, false, '98385089349', 'JÂNIO', 'DA SILVA LIMA', 'militar_416782-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:51.499477+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1553, 'pbkdf2_sha256$1000000$uEl9oWNiKQAwmojsnxO47U$9gj0yobLp7F6Swiz1pYF2UONbWxyhbUPjVIR/YaBKKA=', NULL, false, '13019839424', 'JOÃO', 'VICTOR MARANHÃO NASCIMENTO', 'militar_416791-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:29.198646+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1555, 'pbkdf2_sha256$1000000$y2Sh82LVlJER7dPEJELZMx$kgCm4hxTYt0EheO/2DZaRbm+2YhdwgDUlhVMyvKQ+l8=', NULL, false, '06994969347', 'JOAQUIM', 'ISIDIO DE MOURA', 'militar_416792-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:31.214856+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1574, 'pbkdf2_sha256$1000000$pe21AxMnsv5wblvIty9irS$7l6L09VwnrMZBSzmDnATMks73UKJx6uN8bRzUuNPO3Y=', NULL, false, '01964495377', 'JOSÉ', 'EUCLIDES DE SOUSA NETO', 'militar_416796-1@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:50.541629+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1565, 'pbkdf2_sha256$1000000$ypHYQqnb5402iObAbLrL89$k8VBIKEIKC6crHscxRbwa9gSNPh0rr2Y2XXUAQroLBI=', NULL, false, '07482138307', 'JOSUÉ', 'AMORIM DANTAS', 'militar_416804-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:41.944467+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1564, 'pbkdf2_sha256$1000000$jdtu5mVEG0nenHNDQ3nhWK$Jp5aGOVIsNuKOSKnN/GM4iXVMmcKbpAW+f5seHmmgn8=', NULL, false, '05488589341', 'LEANDRO', 'SILVA BITTENCOURT', 'militar_417813-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:40.968455+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1563, 'pbkdf2_sha256$1000000$DOAm1o0USwRNJT08uCXqNY$Yj/XXG4DkqCSTrdzHsF90Yq60+1AedbRM54keaTPnaU=', NULL, false, '03950090304', 'MAICON', 'HENRIQUE MARQUES BATISTA', 'militar_416901-8@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:39.761877+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1566, 'pbkdf2_sha256$1000000$1JH4Xw3171Qs9cYl0GJsKX$++IMAutpHdkJzlaIzPMrDXzoXKbxgw9QFQW3GmXlfQM=', NULL, false, '06669651376', 'MARCOS', 'ANTONIO CARVALHO DE OLIVEIRA', 'militar_416825-9@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:42.915135+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1558, 'pbkdf2_sha256$1000000$qtroukW9OgQvOVYBEICpOD$Gx365xiOw+yFvQjnJMZGeyYWTBXeKK6cQ7Lgx2VpaPg=', NULL, false, '06199140338', 'MATHEUS', 'CARDOSO COUTINHO', 'militar_416843-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:34.148660+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1569, 'pbkdf2_sha256$1000000$0B0yEK6Eyl5X3FP8YpdCkE$21v4dzwek87rhuL224JSLtGr7hC4EHBYhnW8e/ga7ZY=', NULL, false, '01880347300', 'MOISÉS', 'JOSÉ DE ANDRADE FILHO', 'militar_416850-0@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:45.814710+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1573, 'pbkdf2_sha256$1000000$2apo9RhmQbKv9YKNlfXkwU$BURV8b/cmL6uQVGWiOpjzXIz7AHedz9Dfr2pFClNXBQ=', NULL, false, '05882987350', 'PATRIK', 'ANDERSON MENEZES RIOS', 'militar_416858-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:49.584348+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1568, 'pbkdf2_sha256$1000000$DvjG5iBLq3up0smucwuuYo$wi3cv7HKHzG/34oJVseFBF417W7l++XxlFbw+hbwG8Y=', NULL, false, '02413716351', 'PEDRO', 'HENRIQUE BORGES DA SILVA', 'militar_416861-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:44.860647+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1559, 'pbkdf2_sha256$1000000$GabJinLEP7P8xJDcBt3fxx$RRw7Msv8IxWRZEz1mBgmvjgUP9qOEGcDuDlH0/0jYvE=', NULL, false, '01999631340', 'RAFAEL', 'SOARES DA CRUZ', 'militar_416866-6@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:35.168354+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1556, 'pbkdf2_sha256$1000000$YTvJTTuSJWFhtZPpxMbXKn$isspyZkqGgJP8m5sP34U+dA/zeKS8ZSmPAVnaRyg47Q=', NULL, false, '03232300324', 'REGINALDO', 'LOPES MORAES JUNIOR', 'militar_416869-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:32.203380+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1571, 'pbkdf2_sha256$1000000$Omri1o5IABU9ZoOSXNzD61$QgGuVo8F9ri1EiViXBDMSXkqlJqs7w2KZLiaYbLI9JU=', NULL, false, '03158563355', 'RIVALDINO', 'DE LIMA OTAVIO', 'militar_416874-7@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:47.721602+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1562, 'pbkdf2_sha256$1000000$ACuMKbPCiiboSCfShPWAed$W/EvP0pGzurfUgxlckhMUclkd7tx5hOz1eGzHxNq3DY=', NULL, false, '04299855337', 'THERCIO', 'ANTONIO DOS SANTOS ROCHA', 'militar_416885-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:38.809897+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1579, 'pbkdf2_sha256$1000000$ZztM4G1gnsWT192XtkdrEl$Cx4OQLK1A2KUhP+yZ4fqjHS/tTyXvGghtx97YpaTwhg=', NULL, false, '03043278321', 'WILK', 'RICARDO RESENDE FEITOSA', 'militar_418089-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:55.437176+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1521, 'pbkdf2_sha256$1000000$miKCB7qqTUaK0Uddkg1ack$IxKIotAqddORD9nwfa/ROkIw+CjYghiYWYZksfb+e24=', NULL, false, '03859089382', 'ADRIANO', 'AMARANES DOS SANTOS', 'militar_416904-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:56.629293+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1482, 'pbkdf2_sha256$1000000$xNbBZ99BPNPRl4nRJGNzP3$NWVV0dxlBs92K9xgN6mDzP/A+cCFATcEzvb4Ib9AiMA=', NULL, false, '06524162331', 'AFONSO', 'AMORIM DE SOUSA FILHO', 'militar_416707-4@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:15.131305+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1480, 'pbkdf2_sha256$1000000$13rkRt2jhO27fUWASVZ65u$C8IQPd5EOxW/ccJiNSTqKShX8rtKqyjU1yz2orjzm5g=', NULL, false, '07208694397', 'AIRTON', 'PEREIRA DE SOUSA', 'militar_416709-X@cbmepi.pi.gov.br', false, true, '2025-07-25T15:54:13.035557+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1567, 'pbkdf2_sha256$1000000$6on7pTtAQzVwumRWwEwLaU$g/R1ZuqsVTqdUYh5FX6zbhJocZQTCy0iby77+YbnoTI=', NULL, false, '61101081384', 'ALISON', 'RIBEIRO BONFIM', 'militar_416715-5@cbmepi.pi.gov.br', false, true, '2025-07-25T15:55:43.898306+00:00');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES (1432, 'pbkdf2_sha256$1000000$cLZ6LIvYaMVZWKlzkuxpSV$OD2OPQLw1JVgmUXfEVCcWYoo7FmsADGR3Ouf7mu+2b4=', '2025-07-28T13:25:35.546887+00:00', false, '03191096310', 'ABIMAEL', 'HONÓRIO CORREIA JÚNIOR', 'militar_416708-2@cbmepi.pi.gov.br', false, true, '2025-07-25T15:53:25.652181+00:00');

-- Resetar sequência
SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));

-- ========================================
-- INSERÇÃO DE MILITARES
-- ========================================

INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2269, 7, '244843-2', 'Adoniram PLATINI Moura Martins', 'PLATINI ', 
    '016.924.573-06', '10.368-11', '', '1985-09-21', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'adonirampm@hotmail.com', '(89) 9 8813-3345', '(89) 9 8817-9819', NULL, 
    '2025-07-25T15:51:03.884451+00:00', '2025-07-25T15:51:03.884451+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1291
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2281, 19, '244844-X', 'Alex Gonçalves ALMENDRA', 'Alex ALMENDRA ', 
    '026.966.783-08', '10.375-11', '', '1987-12-24', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:51:15.313874+00:00', '2025-07-25T15:51:15.313874+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1303
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2284, 22, '244845-9', 'ANA LAÍS Martins Aragão de Lacerda', 'ANA LAÍS ', 
    '040.474.843.-0', '10.366-11', '', '1989-12-10', 'F', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'laisaragao.direito@gmail.com', '(86) 9 9926-0719', '(86) 9 8813-4431', NULL, 
    '2025-07-25T15:51:18.520554+00:00', '2025-07-25T15:51:18.520554+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1306
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2265, 3, '207489-3', 'CHARLES Ivonor de Sousa Araújo', 'CHARLES ', 
    '882.032.123-87', '10.333-08', '', '1980-06-04', 'M', 'PRACAS', 
    '1S', '2008-03-27', '2023-12-25', 'AT', 
    'charlesivonor@hotmail.com', '(89) 3 4441-1107', '(89) 9 8804-0728', NULL, 
    '2025-07-25T15:50:59.985154+00:00', '2025-07-25T15:50:59.985154+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1287
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2271, 9, '244879-3', 'Cleiton Carlos Silva SABINO', 'SABINO ', 
    '664.401.573-53', '10.370-11', '', '1981-09-01', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'cleiton_sabino4@hotmail.com', '(86) 9 8476-6862', '(86) 9 9516-9057', NULL, 
    '2025-07-25T15:51:05.797939+00:00', '2025-07-25T15:51:05.797939+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1293
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2272, 10, '244847-5', 'Daniel OLIVEIRA dos Santos', 'OLIVEIRA ', 
    '913.247.183-15', '10.355-11', '', '1981-07-31', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'daniel-oliveirasantos@hotmail.com', '(86) 9 8119-6575', '(86) 9 9483-0929', NULL, 
    '2025-07-25T15:51:06.751680+00:00', '2025-07-25T15:51:06.751680+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1294
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2278, 16, '244851-3', 'Diego FREIRE de Araújo', 'Diego FREIRE ', 
    '016.900.303-56', '10.373-11', '', '1987-11-11', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'diegofreirearaujo@hotmail.com', '(86) 3 2764-4520', '(86) 9 9985-1676', NULL, 
    '2025-07-25T15:51:12.442640+00:00', '2025-07-25T15:51:12.442640+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1300
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2276, 14, '244852-1', 'Eduarddo PENHA Viveiros', 'PENHA ', 
    '011.928.193-73', '10.360-11', '', '1987-06-25', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'eduarddoviveiros@gmail.com', '(86) 8 8256-6474', '(86) 9 9953-0725', NULL, 
    '2025-07-25T15:51:10.515638+00:00', '2025-07-25T15:51:10.515638+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1298
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2274, 12, '244854-8', 'ELVIS Vieira Leal', 'ELVIS ', 
    '026.684.183-05', '10.372-11', '', '1987-07-02', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'elvis-vieira-leal@hotmail.com', '(86) 3 2192-2057', '(86) 9 9966-5027', NULL, 
    '2025-07-25T15:51:08.623228+00:00', '2025-07-25T15:51:08.623228+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1296
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2280, 18, '244857-2', 'GEORGE Ricardo de Sousa Honorato', 'GEORGE ', 
    '041.618.243-78', '10.377-11', '', '1989-11-06', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'georgericardosh@yahoo.com.br', '(89) 3 5224-4588', '(89) 9 9974-3076', NULL, 
    '2025-07-25T15:51:14.365018+00:00', '2025-07-25T15:51:14.365018+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1302
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2287, 26, '244870-0', 'GILVAN de Freitas Rodrigues', 'GILVAN ', 
    '881.750.903-59', '10.380-11', '', '1982-11-15', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'gilvanfr2014@gmail.com', '(86) 8 8229-9770', '(86) 9 9844-6736', NULL, 
    '2025-07-25T15:51:21.822060+00:00', '2025-07-25T15:51:21.822060+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1309
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2279, 17, '244860-2', 'JAMMES Magalhães Silva', 'JAMMES ', 
    '024.675.953-40', '10.381-11', '', '1987-01-08', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'jammesmagalhaes@hotmail.com', '(89) 3 5213-3229', '(89) 9 9973-5545', NULL, 
    '2025-07-25T15:51:13.403267+00:00', '2025-07-25T15:51:13.403267+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1301
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2268, 6, '244861-X', 'Jardson Viana FALCÃO', 'FALCÃO ', 
    '049.999.503-16', '10.376-11', '', '1991-02-04', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    '', '(86) 3 3045-5354', '(86) 9 9830-2782', NULL, 
    '2025-07-25T15:51:02.886880+00:00', '2025-07-25T15:51:02.886880+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1290
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2270, 8, '244863-7', 'Johnathan Patrício Cavalcante SEIXAS', 'SEIXAS ', 
    '027.536.313-95', '10.379-11', '', '1986-12-08', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    '', '(86) 9 8217-7057', '(86) 9 8866-4216', NULL, 
    '2025-07-25T15:51:04.851521+00:00', '2025-07-25T15:51:04.851521+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1292
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2286, 24, '244868-8', 'Jorge GLEYSSON da Cruz de Carvalho', 'GLEYSSON ', 
    '053.962.943-02', '10.356-11', '', '1991-11-23', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'jorgegleysson@hotmail.com', '(86) 3 2173-3290', '(86) 9 9429-1714', NULL, 
    '2025-07-25T15:51:20.884397+00:00', '2025-07-25T15:51:20.884397+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1308
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2263, 1, '207497-4', 'JORGE Henrique Rodrigues Miranda', 'JORGE ', 
    '006.913.103-19', '10.349-08', '', '1983-04-16', 'M', 'PRACAS', 
    '1S', '2008-03-27', '2023-12-25', 'AT', 
    'jhrm21bm@hotmail.com', '(89) 9 9058-5575', '(89) 9 9905-8555', NULL, 
    '2025-07-25T15:50:58.051270+00:00', '2025-07-25T15:50:58.051270+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1285
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2277, 15, '244880-7', 'Lamartine LAVOZIÊ Aborgazan Barreto', 'LAVOZIÊ ', 
    '997.420.393-72', '10.363-11', '', '1983-01-23', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'llabarreto@hotmail.com', '(89) 3 5222-2971', '(89) 9 9934-0987', NULL, 
    '2025-07-25T15:51:11.482450+00:00', '2025-07-25T15:51:11.482450+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1299
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2285, 23, '244864-5', 'MAYLSON Damasceno Mariscal de Araújo', 'MAYLSON ', 
    '040.149.143-99', '10.382-11', '', '1990-05-15', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'MAYLSONCENO@HOTMAIL.COM', '(86) 9 9495-5146', '', NULL, 
    '2025-07-25T15:51:19.918531+00:00', '2025-07-25T15:51:19.918531+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1307
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2273, 11, '244877-7', 'Moisés Andrade Fernandes CANTUÁRIO', 'CANTUÁRIO ', 
    '652.345.883-00', '10.362-11', '', '1983-08-30', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'moisescantuario@gmail.com', '(86) 9 9882-2880', '(86) 9 9483-3001', NULL, 
    '2025-07-25T15:51:07.692120+00:00', '2025-07-25T15:51:07.692120+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1295
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2283, 21, '244872-6', 'PEDRO PAULO Bezerra', 'PEDRO PAULO ', 
    '002.113.063-98', '10.374-11', '', '1982-06-29', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'pedropaulo.mh@bol.com.br', '(89) 9 9973-3329', '(89) 9 9973-3329', NULL, 
    '2025-07-25T15:51:17.204861+00:00', '2025-07-25T15:51:17.204861+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1305
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2267, 5, '244867-0', 'Pedro Yuri LAGES Costa Melo', 'LAGES ', 
    '028.036.393-19', '10.351-11', '', '1991-06-26', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    'pedroyurilcmelo@hotmail.com', '(86) 9 9763-3899', '(86) 9 9976-3899', NULL, 
    '2025-07-25T15:51:01.915390+00:00', '2025-07-25T15:51:01.915390+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1289
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2266, 4, '244873-4', 'RAFAEL LOPES de Araújo', 'RAFAEL LOPES ', 
    '026.823.833-27', '10.353-11', '', '1987-09-08', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:51:00.959859+00:00', '2025-07-25T15:51:00.959859+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1288
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2275, 13, '244865-3', 'SAMUEL Lira do Vale', 'SAMUEL ', 
    '017.677.103-48', '10.350-11', '', '1986-07-15', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:51:09.574015+00:00', '2025-07-25T15:51:09.574015+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1297
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2264, 2, '207474-5', 'THIAGO Lima de Oliveira', 'THIAGO ', 
    '660.928.843-72', '10.323-08', '', '1982-03-18', 'M', 'PRACAS', 
    '1S', '2008-03-27', '2023-12-25', 'AT', 
    'bm_thiago@hotmail.com', '(86) 9 9499-9559', '', NULL, 
    '2025-07-25T15:50:59.017153+00:00', '2025-07-25T15:50:59.017153+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1286
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2282, 20, '244878-5', 'WENES Bastos Ribeiro', 'WENES ', 
    '021.942.145-50', '10.361-11', '', '1986-05-07', 'M', 'PRACAS', 
    '1S', '2011-06-16', '2024-07-18', 'AT', 
    '', '(86) 9 9009-9072', '(86) 9 8102-2441', NULL, 
    '2025-07-25T15:51:16.258207+00:00', '2025-07-25T15:51:16.258207+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1304
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2177, 51, '354524-5', 'Ademar DAMASCENO Soares', 'DAMASCENO ', 
    '932.691.103-91', '10.329-08', '', '1982-12-20', 'M', 'COMB', 
    '1T', '2008-03-27', '2024-12-25', 'AT', 
    '', '(86) 3 3228-8067', '(86) 9 9821-9593', NULL, 
    '2025-07-25T15:49:32.232031+00:00', '2025-07-25T15:49:32.232031+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1199
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2171, 45, '082775-4', 'AILTON Santana Marinho', 'AILTON ', 
    '566.348.543-00', 'GIP 10.10717', '', '1974-08-06', 'M', 'COMP', 
    '1T', '1993-09-01', '2024-07-18', 'AT', 
    'hotasm@hotmail.com', '(86) 9 4270-0799', '(86) 9 9427-0799', NULL, 
    '2025-07-25T15:49:26.357098+00:00', '2025-07-25T15:49:26.357098+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1193
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2161, 35, '343629-2', 'Alcimario Fernandes Lima DUARTE', 'DUARTE ', 
    '017.297.393-77', '10.500-19', '', '1987-01-07', 'M', 'COMB', 
    '1T', '2019-09-12', '2023-07-18', 'AT', 
    '', '(98) 9 8225-9021', '', NULL, 
    '2025-07-25T15:49:15.968344+00:00', '2025-07-25T15:49:15.968344+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1183
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2140, 14, '333656-5', 'ANALICE Padilha de Almeida', 'ANALICE ', 
    '028.931.673-14', '10.491-19', '', '1987-10-09', 'F', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    'analicepadilha@yahoo.com.br', '(86) 9 9984-6999', '(86) 9 3219-1535', NULL, 
    '2025-07-25T15:48:54.686891+00:00', '2025-07-25T15:48:54.686891+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1162
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2131, 5, '014100-3', 'Antônio CARLOS VIEIRA da Costa', 'CARLOS VIEIRA ', 
    '349.519.703-68', 'GIP 10.8062', '', '1965-07-01', 'M', 'COMP', 
    '1T', '1987-03-01', '2022-07-18', 'AT', 
    'ten.carlosvieira@gmail.com', '(86) 9 8827-0846', '(86) 9 8827-0846', NULL, 
    '2025-07-25T15:48:45.022406+00:00', '2025-07-25T15:48:45.022406+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1153
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2127, 1, '085380-1', 'Antônio José de Melo LIMA', 'LIMA ', 
    '395.402.003-34', 'GIP 10.11907', '', '1970-04-27', 'M', 'COMP', 
    '1T', '1994-03-01', '2022-07-18', 'AT', 
    'sgtmelolima@hotmail.com', '(86) 3 2621-1505', '(86) 9 9970-7943', NULL, 
    '2025-07-25T15:48:41.089159+00:00', '2025-07-25T15:48:41.089159+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1149
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2135, 9, '015348-6', 'Antônio Luís DEOLINDO do Nascimento', 'DEOLINDO ', 
    '397.759.333-15', 'GIP 10.9352', '', '1969-12-26', 'M', 'COMP', 
    '1T', '1991-06-01', '2022-07-18', 'AT', 
    'bmdeolindo@ig.com.br', '(86) 8 8082-2892', '(86) 9 8808-2892', NULL, 
    '2025-07-25T15:48:49.288939+00:00', '2025-07-25T15:48:49.288939+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1157
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2158, 32, '014314-6', 'Antônio SEVERIANO da Silva Filho', 'SEVERIANO ', 
    '428.743.003-49', 'GIP 10.8196', '', '1966-07-18', 'M', 'COMP', 
    '1T', '1988-08-05', '2022-12-23', 'AT', 
    '', '(86) 9 5261-1302', '(86) 9 9526-1302', NULL, 
    '2025-07-25T15:49:12.657876+00:00', '2025-07-25T15:49:12.657876+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1180
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2133, 7, '014579-3', 'Antônio Valdeci MARREIRO de Sousa', 'MARREIRO ', 
    '411.672.363-00', 'GIP 10.8505', '', '1968-10-15', 'M', 'COMP', 
    '1T', '1989-08-01', '2022-07-18', 'AT', 
    'antonio.marreiros@cbm.pi.gov.br', '(86) 8 8213-3201', '', NULL, 
    '2025-07-25T15:48:47.151932+00:00', '2025-07-25T15:48:47.151932+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1155
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2129, 3, '108751-7', 'BEATRIZ Lustosa Alves', 'BEATRIZ ', 
    '951.807.883-15', 'GIP 10.12664', '', '1982-05-21', 'F', 'COMP', 
    '1T', '2000-12-01', '2022-07-18', 'AT', 
    'beatrizbm10@hotmail.com', '(89) 9 9413-4890', '(89) 9 9911-2939', NULL, 
    '2025-07-25T15:48:43.021129+00:00', '2025-07-25T15:48:43.021129+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1151
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2170, 44, '015443-1', 'Carlos ALBERTO Soares da Costa', 'C ALBERTO ', 
    '428.615.783-00', 'GIP 10.9448', '', '1970-08-18', 'M', 'COMP', 
    '1T', '1991-06-01', '2023-12-25', 'AT', 
    'betobm.1970@hotmail.com', '(86) 3 2143-3788', '(86) 9 8853-0888', NULL, 
    '2025-07-25T15:49:25.385471+00:00', '2025-07-25T15:49:25.385471+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1192
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2137, 11, '014103-8', 'CARLOS ANTONIO da Cruz Ferreira', 'CARLOS ANTONIO ', 
    '349.504.513-91', 'GIP 10.8065', '', '1962-02-01', 'M', 'COMP', 
    '1T', '1987-03-01', '2022-07-18', 'AT', 
    '', '(86) 9 9975-1619', '(86) 9 9915-6384', NULL, 
    '2025-07-25T15:48:51.359249+00:00', '2025-07-25T15:48:51.359249+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1159
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2143, 17, '333659-0', 'DAVID de Oliveira FREITAS Filho', 'DAVID FREITAS ', 
    '968.301.903-04', '10.317-08', '', '1981-07-18', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    'davidofilho@hotmail.com', '(86) 9 9966-1701', '(86) 9 9966-1701', NULL, 
    '2025-07-25T15:48:57.688755+00:00', '2025-07-25T15:48:57.688755+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1165
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2176, 50, '014318-9', 'ELISEU Gomes de Melo', 'ELISEU ', 
    '394.544.523-04', 'GIP 10.8206', '', '1969-11-24', 'M', 'COMP', 
    '1T', '1988-08-05', '2024-07-18', 'AT', 
    'eliseugomes46@hotmail.com', '(86) 3 2134-4449', '(86) 9 9421-8574', NULL, 
    '2025-07-25T15:49:31.237695+00:00', '2025-07-25T15:49:31.237695+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1198
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2128, 2, '085445-0', 'Eriberto ARCOVERDE Soares da Costa', 'ARCOVERDE ', 
    '515.346.653-15', 'GIP 10.11879', '', '1972-08-16', 'M', 'COMP', 
    '1T', '1994-04-01', '2022-07-18', 'AT', 
    'eriascosta@yahoo.com.br', '(86) 3 2116-6968', '(86) 9 9555-1144', NULL, 
    '2025-07-25T15:48:42.052033+00:00', '2025-07-25T15:48:42.052033+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1150
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2146, 20, '333662-0', 'FILIPE LIMA Martins', 'FILIPE LIMA ', 
    '003.576.613-11', '10.496-19', '', '1985-04-23', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    'filipemartins.adm@gmail.com', '(86) 3 2327-7366', '(86) 9 9979-9092', NULL, 
    '2025-07-25T15:49:00.787641+00:00', '2025-07-25T15:49:00.787641+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1168
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2134, 8, '015934-4', 'Francisco Carlos DA CRUZ Silva', 'DA CRUZ ', 
    '451.139.123-87', 'GIP 10.9837', '', '1973-09-06', 'M', 'COMP', 
    '1T', '1991-11-01', '2022-07-18', 'AT', 
    'sgtbmdacruzpi@hotmail.com', '(86) 3 3056-6522', '(86) 9 8809-2840', NULL, 
    '2025-07-25T15:48:48.236803+00:00', '2025-07-25T15:48:48.236803+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1156
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2149, 23, '014321-9', 'Francisco das Chagas ALVES da SILVA', 'ALVES SILVA', 
    '347.715.573-49', 'GIP 10.8212', '', '1969-02-28', 'M', 'COMP', 
    '1T', '1988-08-05', '2022-07-18', 'AT', 
    'socorrobranquinha@hotmail.com', '(86) 9 9565-3283', '', NULL, 
    '2025-07-25T15:49:03.807990+00:00', '2025-07-25T15:49:03.807990+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1171
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2168, 42, '351989-9', 'Francisco de Paula dos SANTOS', 'SANTOS ', 
    '004.238.763-92', '10.503-20', '', '1985-01-01', 'M', 'COMB', 
    '1T', '2020-07-14', '2023-12-23', 'AT', 
    '', '', '(86) 9 9957-1366', NULL, 
    '2025-07-25T15:49:23.417778+00:00', '2025-07-25T15:49:23.417778+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1190
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2164, 38, '079983-1', 'Francisco GILBERTO da Silva', 'GILBERTO ', 
    '398.298.553-68', 'GIP 10.10542', '', '1971-11-07', 'M', 'COMP', 
    '1T', '1992-12-01', '2023-07-18', 'AT', 
    'gilbertosilvabombeiro@gmail.com', '(86) 9 9939-0124', '(86) 9 9939-0124', NULL, 
    '2025-07-25T15:49:19.516313+00:00', '2025-07-25T15:49:19.516313+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1186
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2172, 46, '082783-5', 'Francisco GILBERTO PIRES Teixeira', 'GILBERTO ', 
    '470.070.443-87', 'GIP 10.10739', '', '1973-03-22', 'M', 'COMP', 
    '1T', '1993-09-01', '2024-07-18', 'AT', 
    'cbgilbertopires@yahoo.com.br', '(86) 3 2361-1665', '(86) 9 8807-5269', NULL, 
    '2025-07-25T15:49:27.324395+00:00', '2025-07-25T15:49:27.324395+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1194
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2163, 37, '082780-X', 'Francisco PIMENTEL dos Santos', 'PIMENTEL ', 
    '693.021.543-00', 'GIP 10.10732', '', '1974-07-24', 'M', 'COMP', 
    '1T', '1993-09-01', '2023-07-18', 'AT', 
    'pimentel.bm@hotmail.com', '(86) 9 9436-4159', '', NULL, 
    '2025-07-25T15:49:18.491661+00:00', '2025-07-25T15:49:18.491661+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1185
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2144, 18, '333660-3', 'GABRIEL MENDES Rezende', 'GABRIEL MENDES ', 
    '934.417.623-04', '10.494-19', '', '1982-06-25', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    'gabriel_rezende82@hotmail.com', '(86) 9 9981-8989', '', NULL, 
    '2025-07-25T15:48:58.684460+00:00', '2025-07-25T15:48:58.684460+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1166
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2139, 13, '085478-6', 'Gerardo Santos GASPAR', 'GASPAR ', 
    '504.605.363-20', 'GIP 10.11830', '', '1972-02-21', 'M', 'COMP', 
    '1T', '1994-02-01', '2022-07-18', 'AT', 
    'gesanpar@gmail.com', '(86) 3 2221-1084', '(86) 9 8801-1902', NULL, 
    '2025-07-25T15:48:53.635288+00:00', '2025-07-25T15:48:53.635288+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1161
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2175, 49, '047499-1', 'GILDETE Freire dos Santos Carvalho', 'GILDETE ', 
    '498.186.353-53', 'GIP 10.10242', '', '1973-02-13', 'F', 'COMP', 
    '1T', '1992-08-01', '2024-07-18', 'AT', 
    'gildetbm@hotmail.com', '(89) 9 4418-8171', '', NULL, 
    '2025-07-25T15:49:30.255011+00:00', '2025-07-25T15:49:30.255011+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1197
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2165, 39, '108741-0', 'GILDETH de Oliveira Viana', 'GILDETH ', 
    '833.732.253-53', 'GIP 10.12656', '', '1979-01-26', 'F', 'COMP', 
    '1T', '2000-12-01', '2023-07-18', 'AT', 
    'evita_515@hotmail.com', '(86) 3 2208-8343', '(86) 9 9951-5510', NULL, 
    '2025-07-25T15:49:20.505320+00:00', '2025-07-25T15:49:20.505320+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1187
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2132, 6, '108743-6', 'HAMYLTON Lemos e Silva', 'HAMYLTON ', 
    '863.320.154-20', 'GIP 10.12658', '', '1973-08-01', 'M', 'COMP', 
    '1T', '2000-12-01', '2022-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:46.106447+00:00', '2025-07-25T15:48:46.106447+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1154
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2156, 30, '108754-1', 'HÉLIDA Márcia Oliveira de Moraes', 'HÉLIDA ', 
    '848.009.923-20', 'GIP 10.12667', '', '1978-06-26', 'F', 'COMP', 
    '1T', '2000-12-01', '2022-07-18', 'AT', 
    'hmom16@hotmail.com', '(86) 8 8498-8876', '', NULL, 
    '2025-07-25T15:49:10.705574+00:00', '2025-07-25T15:49:10.705574+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1178
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2147, 21, '333663-8', 'HUMBERTO DOUGLAS Coutinho Oliveira', 'HUMBERTO DOUGLAS ', 
    '037.476.123-00', '10.497-19', '', '1987-06-23', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    '', '(86) 9 8810-4244', '', NULL, 
    '2025-07-25T15:49:01.834997+00:00', '2025-07-25T15:49:01.834997+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1169
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2145, 19, '333661-1', 'ISAÍAS Emanuel Alexandre Sales', 'ISAÍAS ', 
    '038.131.403-00', '10.495-19', '', '1989-04-01', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    '', '(86) 9 9832-1026', '(86) 9 3220-6474', NULL, 
    '2025-07-25T15:48:59.720272+00:00', '2025-07-25T15:48:59.720272+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1167
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2136, 10, '012528-8', 'JOÃO de Deus BORGES de Carvalho', 'JOÃO BORGES ', 
    '217.383.513-00', 'GIP 10.5761', '', '1962-08-15', 'M', 'COMP', 
    '1T', '1983-04-22', '2022-07-18', 'AT', 
    '', '(86) 3 2173-3290', '(86) 9 8855-4121', NULL, 
    '2025-07-25T15:48:50.318858+00:00', '2025-07-25T15:48:50.318858+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1158
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2153, 27, '014083-0', 'José AUGUSTO Soares da Cruz', 'AUGUSTO ', 
    '394.535.533-87', 'GIP 10.8020', '', '1967-09-30', 'M', 'COMP', 
    '1T', '1987-03-01', '2022-07-18', 'AT', 
    '', '(86) 3 2176-6603', '(86) 9 9525-7451', NULL, 
    '2025-07-25T15:49:07.768735+00:00', '2025-07-25T15:49:07.768735+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1175
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2154, 28, '013015-0', 'José de Ribamar Itapirema BRASIL', 'BRASIL ', 
    '288.056.903-68', 'GIP 10.7182', '', '1963-08-22', 'M', 'COMP', 
    '1T', '1985-04-30', '2022-07-18', 'AT', 
    '', '(86) 9 9809-2643', '', NULL, 
    '2025-07-25T15:49:08.765770+00:00', '2025-07-25T15:49:08.765770+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1176
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2157, 31, '014190-9', 'José dos Reis da Silva BRITO', 'BRITO ', 
    '349.839.453-34', '105.148.283-2', '', '1966-01-06', 'M', 'COMP', 
    '1T', '1987-10-15', '2022-12-23', 'AT', 
    'gyvago@bol.com.br', '(86) 9 4131-1815', '', NULL, 
    '2025-07-25T15:49:11.670684+00:00', '2025-07-25T15:49:11.670684+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1179
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2173, 47, '085429-8', 'Luís de Morais NUNES', 'NUNES ', 
    '780.362.833-87', 'GIP 10.11784', '', '1973-03-05', 'M', 'COMP', 
    '1T', '1994-03-01', '2024-07-18', 'AT', 
    'gyvago@bol.com.br', '(86) 9 8883-1340', '(86) 9 8883-1340', NULL, 
    '2025-07-25T15:49:28.288881+00:00', '2025-07-25T15:49:28.288881+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1195
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2150, 24, '014099-6', 'Luíz GONZAGA Nonato de Sousa', 'GONZAGA ', 
    '349.519.203-44', 'GIP 10.8061', '', '1966-10-18', 'M', 'COMP', 
    '1T', '1987-03-01', '2022-07-18', 'AT', 
    'luisgnonato@hotmail.com', '(86) 9 9965-6934', '(86) 9 9965-6934', NULL, 
    '2025-07-25T15:49:04.784042+00:00', '2025-07-25T15:49:04.784042+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1172
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2160, 34, '343824-4', 'Marcella PRADO Albuquerque', 'PRADO ', 
    '006.630.823-23', '10.499-19', '', '1986-03-22', 'F', 'COMB', 
    '1T', '2019-09-12', '2023-07-18', 'AT', 
    '', '(89) 9 9423-0966', '', NULL, 
    '2025-07-25T15:49:14.608955+00:00', '2025-07-25T15:49:14.608955+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1182
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2130, 4, '084816-6', 'MARCÍLIO Bezerra dos Santos', 'MARCÍLIO ', 
    '451.173.903-00', 'GIP 10.11508', '', '1972-09-04', 'M', 'COMP', 
    '1T', '1994-04-01', '2022-07-18', 'AT', 
    'ps8rbc@gmail.com', '(86) 3 2161-1264', '(86) 9 9958-8757', NULL, 
    '2025-07-25T15:48:44.040982+00:00', '2025-07-25T15:48:44.040982+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1152
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2169, 43, '108756-8', 'Maria DAS DORES Oliveira Rodrigues Damasceno', 'DAS DORES ', 
    '768.270.383-00', 'GIP 10.12668', '', '1975-09-17', 'F', 'COMP', 
    '1T', '2000-12-01', '2023-12-23', 'AT', 
    'dasdoresbm@hotmail.com', '(86) 3 2214-4298', '(86) 9 9992-3632', NULL, 
    '2025-07-25T15:49:24.408091+00:00', '2025-07-25T15:49:24.408091+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1191
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2138, 12, '015343-5', 'MILTON do Nascimento Castro', 'MILTON ', 
    '353.680.203-68', 'GIP 10.9347', '', '1969-05-08', 'M', 'COMP', 
    '1T', '1991-06-01', '2022-07-18', 'AT', 
    '', '(86) 9 5469-9132', '', NULL, 
    '2025-07-25T15:48:52.603974+00:00', '2025-07-25T15:48:52.603974+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1160
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2148, 22, '085807-2', 'ODAIR José da Silva Santos', 'ODAIR ', 
    '566.225.033-20', 'GIP 10.11903', '', '1974-01-24', 'M', 'COMP', 
    '1T', '1994-03-01', '2022-07-18', 'AT', 
    'odairsantos193@hotmail.com', '(86) 3 3153-3320', '(86) 9 9467-6301', NULL, 
    '2025-07-25T15:49:02.835452+00:00', '2025-07-25T15:49:02.835452+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1170
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2155, 29, '012479-6', 'ORLANDO de Sousa Silva', 'ORLANDO ', 
    '217.389.393-91', 'GIP 10.5645', '', '1961-12-28', 'M', 'COMP', 
    '1T', '1982-03-16', '2022-07-18', 'AT', 
    '', '(86) 9 9487-9219', '(86) 9 8852-3228', NULL, 
    '2025-07-25T15:49:09.740458+00:00', '2025-07-25T15:49:09.740458+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1177
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2151, 25, '014194-1', 'PAULO Henrique Araújo', 'PAULO ', 
    '474.196.523-68', '105.067.193-0', '', '1965-06-01', 'M', 'COMP', 
    '1T', '1987-10-15', '2022-07-18', 'AT', 
    '', '(89) 3 4223-3307', '(89) 9 9977-1085', NULL, 
    '2025-07-25T15:49:05.788324+00:00', '2025-07-25T15:49:05.788324+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1173
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2141, 15, '333657-3', 'PEDRO BENTO Bezerra Neto', 'PEDRO BENTO ', 
    '994.388.523-87', '10.492-19', '', '1986-06-10', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    '', '(86) 3 0853-3975', '(86) 9 9997-6122', NULL, 
    '2025-07-25T15:48:55.708950+00:00', '2025-07-25T15:48:55.708950+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1163
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2159, 33, '343628-4', 'Rafael MEDEIROS dos Reis ', 'MEDEIROS ', 
    '004.805.823-86', '10.498-19', '', '1986-05-15', 'M', 'COMB', 
    '1T', '2019-09-12', '2023-07-18', 'AT', 
    '', '(86) 9 9966-4449', '', NULL, 
    '2025-07-25T15:49:13.626813+00:00', '2025-07-25T15:49:13.626813+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1181
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2166, 40, '085392-5', 'RICARDO José dos Santos Filho', 'RICARDO ', 
    '744.280.633-34', 'GIP 10.11877', '', '1974-03-14', 'M', 'COMP', 
    '1T', '1994-03-01', '2023-07-18', 'AT', 
    'r18bm@hotmail.com', '(86) 3 2623-3676', '(86) 9 9428-9554', NULL, 
    '2025-07-25T15:49:21.476288+00:00', '2025-07-25T15:49:21.476288+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1188
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2162, 36, '343630-6', 'Rodollfo OLIVEIRA de Jesus', 'OLIVEIRA ', 
    '041.677.053-38', '10.501-19', '', '1990-10-15', 'M', 'COMB', 
    '1T', '2019-09-12', '2023-07-18', 'AT', 
    '', '(86) 9 9461-1090', '', NULL, 
    '2025-07-25T15:49:17.457642+00:00', '2025-07-25T15:49:17.457642+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1184
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2152, 26, '014102-0', 'SIDNEY Viana da Silva', 'SIDNEY ', 
    '287.262.513-53', 'GIP 10.8064', '', '1965-10-05', 'M', 'COMP', 
    '1T', '1987-03-01', '2022-07-18', 'AT', 
    'vianasilva1965@bol.com.br', '(86) 3 3057-7039', '(86) 9 9510-5050', NULL, 
    '2025-07-25T15:49:06.789480+00:00', '2025-07-25T15:49:06.789480+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1174
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2174, 48, '085373-9', 'SILVESTRE Pereira da Silva Neto', 'SILVESTRE ', 
    '504.201.863-87', 'GIP 10.11886', '', '1973-06-14', 'M', 'COMP', 
    '1T', '1994-03-01', '2024-07-18', 'AT', 
    'silperneto@hotmail.com', '', '(86) 9 9925-3732', NULL, 
    '2025-07-25T15:49:29.269623+00:00', '2025-07-25T15:49:29.269623+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1196
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2167, 41, '351988-X', 'THIAGO Lima CARVALHO', 'THIAGO CARVALHO ', 
    '030.029.673-86', '10.502-20', '', '1987-07-30', 'M', 'COMB', 
    '1T', '2020-07-14', '2023-12-23', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:49:22.439469+00:00', '2025-07-25T15:49:22.439469+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1189
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2142, 16, '333658-1', 'Vinícius EDUARDO Santos Martins', 'EDUARDO ', 
    '020.157.313-00', '10.493-19', '', '1986-02-18', 'M', 'COMB', 
    '1T', '2019-01-07', '2022-07-18', 'AT', 
    '', '(86) 9 9959-3930', '(86) 9 9984-9696', NULL, 
    '2025-07-25T15:48:56.705757+00:00', '2025-07-25T15:48:56.705757+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1164
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2291, 4, '270293-2', 'ALDERI de Melo Pereira', 'ALDERI ', 
    '007.277.693-59', '10.396-13', '', '1983-12-28', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'alderimelo@hotmail.com', '(89) 9 9247-7775', '(89) 9 9402-5364', NULL, 
    '2025-07-25T15:51:25.640930+00:00', '2025-07-25T15:51:25.640930+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1313
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2292, 5, '270294-X', 'ALEX Karol Carlos da Rocha', 'ALEX ', 
    '013.093.183-79', '10.403-13', '', '1985-04-13', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'alexkarolca@hotmail.com', '(89) 3 4851-1212', '(86) 9 9458-8084', NULL, 
    '2025-07-25T15:51:26.602637+00:00', '2025-07-25T15:51:26.602637+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1314
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2299, 12, '270295-9', 'BRUNO de Oliveira Lopes', 'BRUNO ', 
    '600.175.083-12', '10.401-13', '', '1988-07-20', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'bruno-llopes@hotmail.com', '(86) 3 3231-1345', '(86) 9 9541-6431', NULL, 
    '2025-07-25T15:51:33.269373+00:00', '2025-07-25T15:51:33.269373+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1321
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2288, 1, '270296-7', 'David Silva MAGALHÃES', 'MAGALHÃES ', 
    '018.194.153-84', '10.397-13', '', '1987-04-08', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'DAVIDSILVAMAGALHAES@HOTMAIL.COM', '(86) 3 2761-1628', '(86) 9 9994-8805', NULL, 
    '2025-07-25T15:51:22.766919+00:00', '2025-07-25T15:51:22.766919+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1310
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2290, 3, '270300-9', 'FELIPPE da Silva VIANA', 'FELIPPE VIANA ', 
    '017.059.513-76', '10.387-13', '', '1989-05-01', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'eusoufelippe@gmail.com', '(86) 9 9933-9817', '(86) 9 9933-9817', NULL, 
    '2025-07-25T15:51:24.692927+00:00', '2025-07-25T15:51:24.692927+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1312
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2295, 8, '270303-3', 'FRANCINALDO dos Reis Lima', 'FRANCINALDO ', 
    '000.767.353-11', '10.392-13', '', '1982-04-10', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'francinaldorlima@hotmail.com', '(86) 3 2349-9517', '(86) 9 9477-7673', NULL, 
    '2025-07-25T15:51:29.456767+00:00', '2025-07-25T15:51:29.456767+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1317
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2302, 15, '270304-1', 'Francisco das Chagas PABLO de Morais Leite', 'PABLO ', 
    '977.054.203-25', '10.389-13', '', '1982-11-07', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'bpablo.leite193@gmail.com', '(86) 9 9948-7556', '(86) 9 8801-8185', NULL, 
    '2025-07-25T15:51:36.106708+00:00', '2025-07-25T15:51:36.106708+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1324
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2301, 14, '270306-8', 'Georges Davis NORONHA de Menezes', 'NORONHA ', 
    '010.549.723-11', '10.394-13', '', '1986-09-08', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'georgedavys@hotmail.com', '(86) 9 9917-6350', '(86) 9 9917-6350', NULL, 
    '2025-07-25T15:51:35.168881+00:00', '2025-07-25T15:51:35.168881+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1323
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2300, 13, '271209-1', 'KAROLLINY Barbosa Silva', 'KAROLLINY ', 
    '009.984.473-74', '10.407-13', '', '1984-08-13', 'F', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'xkarolbarbosax@gmail.com', '(86) 3 2131-1814', '(86) 9 8801-7565', NULL, 
    '2025-07-25T15:51:34.224176+00:00', '2025-07-25T15:51:34.224176+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1322
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2303, 16, '207490-7', 'LUCIANA Lís de Souza e Santos', 'LUCIANA ', 
    '026.918.693-00', '10.343-08', '', '1987-08-19', 'F', 'PRACAS', 
    '2S', '2008-03-27', '2024-12-25', 'AT', 
    'lis-luciana@hotmail.com', '(86) 8 8262-2082', '', NULL, 
    '2025-07-25T15:51:37.041884+00:00', '2025-07-25T15:51:37.041884+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1325
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2294, 7, '270313-X', 'MARCOS AUGUSTO Lima Soares', 'MARCOS AUGUSTO ', 
    '007.259.093-90', '10.391-13', '', '1986-02-22', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:51:28.508871+00:00', '2025-07-25T15:51:28.508871+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1316
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2297, 10, '270326-2', 'MICKAEL da Silva Nascimento', 'MICKAEL ', 
    '041.063.073-08', '10.400-13', '', '1988-07-20', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'mickael.nascimento@hotmail.com', '(86) 3 2765-5682', '(86) 9 9967-0247', NULL, 
    '2025-07-25T15:51:31.373138+00:00', '2025-07-25T15:51:31.373138+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1319
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2298, 11, '270327-X', 'Rafael ESCORCIO Pinheiro', 'ESCORCIO ', 
    '002.424.453-81', '10.404-13', '', '1983-07-13', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'rafaelescorcio13@hotmail.com', '(86) 3 2761-1154', '(86) 9 9803-0042', NULL, 
    '2025-07-25T15:51:32.317516+00:00', '2025-07-25T15:51:32.317516+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1320
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2293, 6, '270317-3', 'RILDO Kelson da Cruz Gonçalves', 'RILDO ', 
    '021.723.533-61', '10.405-13', '', '1985-05-10', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'kelson.geo11@gmail.com', '(86) 3 2326-6787', '(86) 9 9860-8163', NULL, 
    '2025-07-25T15:51:27.541264+00:00', '2025-07-25T15:51:27.541264+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1315
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2289, 2, '270319-0', 'Thiago ARCANJO Pires Oliveira', 'ARCANJO ', 
    '027.689.703-01', '10.398-13', '', '1990-01-16', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'th-phb@hotmail.com', '(86) 3 3223-3741', '(86) 9 9432-2255', NULL, 
    '2025-07-25T15:51:23.707524+00:00', '2025-07-25T15:51:23.707524+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1311
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2296, 9, '270320-3', 'Vagner Alves VIANA', 'VIANA ', 
    '025.533.383-84', '10.390-13', '', '1986-06-04', 'M', 'PRACAS', 
    '2S', '2013-05-08', '2024-07-18', 'AT', 
    'vagnerviana007@hotmail.com', '(86) 3 2768-8022', '(86) 9 9937-4759', NULL, 
    '2025-07-25T15:51:30.415377+00:00', '2025-07-25T15:51:30.415377+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1318
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2188, 11, '085327-5', 'Charles FRANCO de Oliveira Lopes', 'FRANCO ', 
    '700.134.383-87', 'GIP 10.11941', '', '1975-05-02', 'M', 'COMP', 
    '2T', '1994-03-01', '2022-07-18', 'AT', 
    'franco.charles@hotmail.com', '(86) 3 2144-4496', '(86) 9 9438-1520', NULL, 
    '2025-07-25T15:49:42.985717+00:00', '2025-07-25T15:49:42.985717+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1210
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2185, 8, '085413-1', 'CLÁCIO Alves da Silva', 'CLÁCIO ', 
    '474.366.033-53', 'GIP 10.11880', '', '1972-02-29', 'M', 'COMP', 
    '2T', '1994-03-01', '2022-07-18', 'AT', 
    '', '(86) 3 2175-5537', '(86) 9 8126-1278', NULL, 
    '2025-07-25T15:49:40.077167+00:00', '2025-07-25T15:49:40.077167+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1207
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2204, 27, '082772-0', 'CLÉBIO Araújo de Queiroz', 'CLÉBIO ', 
    '470.817.753-49', 'GIP 10.10735', '', '1972-06-03', 'M', 'COMP', 
    '2T', '1993-09-01', '2023-07-18', 'AT', 
    '', '(86) 3 2279-9309', '(86) 9 9988-4319', NULL, 
    '2025-07-25T15:49:58.889072+00:00', '2025-07-25T15:49:58.889072+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1226
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2193, 16, '015349-4', 'DÁRIO Nascimento', 'DÁRIO ', 
    '439.723.573-20', 'GIP 10.9353', '', '1972-01-02', 'M', 'COMP', 
    '2T', '1991-06-01', '2022-07-18', 'AT', 
    'gyvago@bol.com.br', '(86) 8 8057-7092', '(86) 9 9906-6592', NULL, 
    '2025-07-25T15:49:47.820452+00:00', '2025-07-25T15:49:47.820452+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1215
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2201, 24, '079685-9', 'DEOCLÉCIO dos Santos Caldas', 'DEOCLÉCIO ', 
    '553.563.033-00', 'GIP 10.10402', '', '1970-02-11', 'M', 'COMP', 
    '2T', '1992-02-01', '2023-07-18', 'AT', 
    '', '(86) 9 8852-6486', '(86) 9 8852-6486', NULL, 
    '2025-07-25T15:49:55.970442+00:00', '2025-07-25T15:49:55.970442+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1223
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2192, 15, '015344-3', 'Edivan CONRADO da Silva', 'CONRADO ', 
    '397.868.893-04', 'GIP 10.9378', '', '1971-11-18', 'M', 'COMP', 
    '2T', '1991-06-01', '2022-07-18', 'AT', 
    'econrado1@hotmail.com', '(86) 9 9364-4110', '(86) 9 9436-9489', NULL, 
    '2025-07-25T15:49:46.852412+00:00', '2025-07-25T15:49:46.852412+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1214
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2206, 29, '015345-1', 'EIRES dos Santos Lima', 'EIRES ', 
    '407.943.503-72', 'GIP 10.9349', '', '1971-09-24', 'M', 'COMP', 
    '2T', '1991-06-01', '2023-07-18', 'AT', 
    '', '(86) 3 2252-2715', '(86) 9 9900-0112', NULL, 
    '2025-07-25T15:50:00.823506+00:00', '2025-07-25T15:50:00.823506+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1228
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2181, 4, '015322-2', 'FLÁVIO Gomes de Oliveira', 'FLÁVIO', 
    '412.317.753-00', 'GIP 10.9325', '', '1969-09-14', 'M', 'COMP', 
    '2T', '1991-06-01', '2022-07-18', 'AT', 
    'flavio---gomes@hotmail.com', '(86) 9 8808-6345', '(86) 9 8879-0768', NULL, 
    '2025-07-25T15:49:36.171889+00:00', '2025-07-25T15:49:36.171889+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1203
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2178, 1, '085838-2', 'Francisco Carlos Mendes FRAZÃO', 'FRAZÃO ', 
    '498.575.923-68', 'GIP 10.11905', '', '1972-10-10', 'M', 'COMP', 
    '2T', '1994-03-01', '2022-07-18', 'AT', 
    'frazaobm@gmail.com', '(86) 3 2143-3788', '(86) 9 9463-3086', NULL, 
    '2025-07-25T15:49:33.223093+00:00', '2025-07-25T15:49:33.223093+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1200
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2187, 10, '083489-X', 'Francisco da Cruz CARNEIRO', 'CARNEIRO ', 
    '536.280.553-34', 'GIP 10.11081', '', '1974-09-14', 'M', 'COMP', 
    '2T', '1993-12-01', '2022-07-18', 'AT', 
    'karneirobombeiros@hotmail.com', '(86) 3 2143-3788', '(86) 9 9413-1754', NULL, 
    '2025-07-25T15:49:42.015567+00:00', '2025-07-25T15:49:42.015567+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1209
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2184, 7, '015961-1', 'Francisco da Silva RIBEIRO', 'RIBEIRO ', 
    '504.534.163-49', 'GIP 10.9867', '', '1970-07-13', 'M', 'COMP', 
    '2T', '1991-11-01', '2022-07-18', 'AT', 
    'ribeirogse@hotmail.com', '(86) 9 8847-2051', '(86) 9 3226-3672', NULL, 
    '2025-07-25T15:49:39.103348+00:00', '2025-07-25T15:49:39.103348+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1206
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2198, 21, '015352-4', 'Francisco das Chagas DE MELO SANTOS', 'MELO SANTOS ', 
    '490.191.123-68', 'GIP 10.9356', '', '1971-07-24', 'M', 'COMP', 
    '2T', '1991-06-01', '2023-07-18', 'AT', 
    'milrosardes@hotmail.com', '(86) 3 3153-3320', '(86) 9 9451-7276', NULL, 
    '2025-07-25T15:49:53.017618+00:00', '2025-07-25T15:49:53.017618+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1220
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2182, 5, '085848-0', 'Francisco VALTER Pereira', 'VALTER ', 
    '730.553.363-72', 'GIP 10.11909', '', '1975-11-26', 'M', 'COMP', 
    '2T', '1994-03-01', '2022-07-18', 'AT', 
    'franciscovalterp@gmail.com', '(86) 3 2368-8169', '(86) 9 9562-5444', NULL, 
    '2025-07-25T15:49:37.156751+00:00', '2025-07-25T15:49:37.156751+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1204
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2205, 28, '014625-X', 'Genival ARAÚJO da Silva', 'G ARAÚJO ', 
    '361.420.853-20', 'GIP 10.8529', '', '1969-08-15', 'M', 'COMP', 
    '2T', '1989-09-01', '2023-07-18', 'AT', 
    '', '(86) 3 2226-6714', '(86) 9 9866-8785', NULL, 
    '2025-07-25T15:49:59.853353+00:00', '2025-07-25T15:49:59.853353+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1227
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2190, 13, '085790-4', 'GIVALDO Oliveira de Sousa ', 'GIVALDO ', 
    '151.329.258-71', 'GIP 10.11908', '', '1971-08-13', 'M', 'COMP', 
    '2T', '1994-03-01', '2022-07-18', 'AT', 
    '', '(86) 9 9956-6077', '', NULL, 
    '2025-07-25T15:49:44.925462+00:00', '2025-07-25T15:49:44.925462+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1212
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2194, 17, '108748-7', 'JAIRO Oliveira Figueiredo', 'JAIRO ', 
    '854.831.683-72', 'GIP 10.12663', '', '1980-03-19', 'M', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'viverbem.residence@hotmail.com', '(86) 8 8025-5973', '(86) 9 9530-2164', NULL, 
    '2025-07-25T15:49:48.852249+00:00', '2025-07-25T15:49:48.852249+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1216
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2183, 6, '015011-8', 'JOSÉ LUIZ Amaranes dos Santos', 'JOSÉ LUIZ ', 
    '428.759.003-15', 'GIP 10.8894', '', '1971-02-19', 'M', 'COMP', 
    '2T', '1990-07-01', '2022-07-18', 'AT', 
    'vivobem@hotmail.com', '(86) 3 2352-2194', '(86) 9 9559-3291', NULL, 
    '2025-07-25T15:49:38.137240+00:00', '2025-07-25T15:49:38.137240+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1205
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2203, 26, '108761-4', 'José Wilson Vieira RAMOS', 'RAMOS ', 
    '678.315.323-15', 'GIP 10.12673', '', '1974-09-07', 'M', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'valderice31@hotmail.com', '(89) 9 4352-2443', '(89) 9 9939-8362', NULL, 
    '2025-07-25T15:49:57.914774+00:00', '2025-07-25T15:49:57.914774+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1225
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2179, 2, '082761-4', 'Juscelino MAGALHÃES', 'MAGALHÃES ', 
    '577.899.243-20', 'GIP 10.10734', '', '1974-06-08', 'M', 'COMP', 
    '2T', '1993-09-01', '2022-07-18', 'AT', 
    'juscelinomago@gmail.com', '(86) 9 5539-9298', '(86) 9 9920-9120', NULL, 
    '2025-07-25T15:49:34.214169+00:00', '2025-07-25T15:49:34.214169+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1201
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2180, 3, '085792-X', 'MARCONE Costa Alves', 'MARCONE ', 
    '696.826.403-00', 'GIP 10.11901', '', '1975-05-02', 'M', 'COMP', 
    '2T', '1994-03-01', '2022-07-18', 'AT', 
    'marconeresgate@yahoo.com.br', '(86) 9 9496-5535', '(86) 9 8838-4702', NULL, 
    '2025-07-25T15:49:35.186174+00:00', '2025-07-25T15:49:35.186174+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1202
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2202, 25, '013927-X', 'Raimundo Nonato DE CARVALHO', 'DE CARVALHO ', 
    '349.302.303-06', 'GIP 10.7885', '', '1967-03-15', 'M', 'COMP', 
    '2T', '1986-11-01', '2023-07-18', 'AT', 
    '', '(86) 9 9961-1249', '(86) 9 9996-1249', NULL, 
    '2025-07-25T15:49:56.934645+00:00', '2025-07-25T15:49:56.934645+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1224
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2191, 14, '084356-3', 'Raimundo RODRIGUES Neto', 'RODRIGUES ', 
    '451.738.933-20', 'GIP 10.11259', '', '1971-12-24', 'M', 'COMP', 
    '2T', '1994-01-01', '2022-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:49:45.888240+00:00', '2025-07-25T15:49:45.888240+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1213
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2186, 9, '014580-7', 'ROBERT Costa Santos', 'ROBERT ', 
    '411.639.233-20', 'GIP 10.8506', '', '1969-10-27', 'M', 'COMP', 
    '2T', '1989-08-01', '2022-07-18', 'AT', 
    'robertsgtbm@hotmal.com', '(86) 9 4737-7920', '(86) 9 9473-7920', NULL, 
    '2025-07-25T15:49:41.042800+00:00', '2025-07-25T15:49:41.042800+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1208
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2200, 23, '108799-1', 'Ronielton Marques do AMARAL', 'AMARAL ', 
    '864.044.581-87', 'GIP 10.12689', '', '1979-08-12', 'M', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'cbamaral2009@hotmail.com', '(86) 3 2182-2422', '(86) 9 8843-4713', NULL, 
    '2025-07-25T15:49:55.003817+00:00', '2025-07-25T15:49:55.003817+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1222
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2197, 20, '108765-7', 'ROSIMAR do Nascimento Granja', 'ROSIMAR ', 
    '628.052.073-00', 'GIP 10.12678', '', '1978-05-16', 'F', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'florbilica@hotmail.com', '(86) 3 2267-7007', '(86) 9 9986-5556', NULL, 
    '2025-07-25T15:49:52.007940+00:00', '2025-07-25T15:49:52.007940+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1219
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2189, 12, '015083-5', 'SEBASTIÃO Vieira Rodrigues', 'SEBASTIÃO ', 
    '429.186.423-04', 'GIP 10.8990', '', '1970-11-26', 'M', 'COMP', 
    '2T', '1990-07-01', '2022-07-18', 'AT', 
    'sgtbm.sebastiao@hotmail.com', '(86) 3 2374-4959', '(86) 9 8823-1668', NULL, 
    '2025-07-25T15:49:43.951772+00:00', '2025-07-25T15:49:43.951772+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1211
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2196, 19, '108760-6', 'STANLEY Azevedo Fernando', 'STANLEY ', 
    '845.203.373-72', 'GIP 10.12674', '', '1980-10-08', 'M', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'stanley_gbs@hotmail.com', '(86) 9 8845-1770', '(86) 9 8845-1770', NULL, 
    '2025-07-25T15:49:50.857231+00:00', '2025-07-25T15:49:50.857231+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1218
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2195, 18, '108747-9', 'TUPINAMBA Messias da Silva', 'TUPINAMBA ', 
    '767.713.853-53', 'GIP 10.12662', '', '1977-11-11', 'M', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'tupinambamessias@hotmail.com', '(86) 9 9532-2346', '(86) 9 9953-2346', NULL, 
    '2025-07-25T15:49:49.877977+00:00', '2025-07-25T15:49:49.877977+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1217
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2199, 22, '108742-8', 'VIRLANE Mendes Gama', 'VIRLANE ', 
    '535.859.253-91', 'GIP 10.12657', '', '1974-01-26', 'F', 'COMP', 
    '2T', '2000-12-01', '2023-07-18', 'AT', 
    'semprelutadora@hotmail.com', '(86) 3 2271-1401', '(86) 9 8825-8669', NULL, 
    '2025-07-25T15:49:53.996919+00:00', '2025-07-25T15:49:53.996919+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1221
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2308, 5, '292164-2', 'EDUARDO Lira de Oliveira', 'EDUARDO Lira ', 
    '024.261.813-89', '10.414/15', '', '1988-06-23', 'M', 'PRACAS', 
    '3S', '2015-06-15', '2023-07-18', 'AT', 
    '', '(86) 9 4150-0646', '(86) 9 9415-0646', NULL, 
    '2025-07-25T15:51:41.983573+00:00', '2025-07-25T15:51:41.983573+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1330
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2306, 3, '270299-1', 'Felipe Santiago MONTEIRO Neto', 'MONTEIRO ', 
    '001.455.443-70', '10.411-13', '', '1982-12-08', 'M', 'PRACAS', 
    '3S', '2014-07-07', '2023-07-18', 'AT', 
    'felipetotal@hotmail.com', '(86) 8 8227-7911', '(86) 9 8822-7911', NULL, 
    '2025-07-25T15:51:40.007850+00:00', '2025-07-25T15:51:40.007850+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1328
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2311, 8, '270305-0', 'Francisco dos SANTOS de Sousa Batista', 'SANTOS ', 
    '658.429.363-72', '10.399-13', '', '1979-11-01', 'M', 'PRACAS', 
    '3S', '2013-05-08', '2023-07-18', 'AT', 
    '', '(86) 3 2182-2189', '(86) 9 9992-9955', NULL, 
    '2025-07-25T15:51:44.902724+00:00', '2025-07-25T15:51:44.902724+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1333
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2310, 7, '244858-X', 'Gustavo FELIPE de Brito Lopes', 'FELIPE ', 
    '015.868.303-09', '10.416-15', '', '1986-11-13', 'M', 'PRACAS', 
    '3S', '2015-01-29', '2023-07-18', 'AT', 
    'gusttavobritto.13@hotmail.com', '(86) 9 9402-2606', '(86) 9 9402-2606', NULL, 
    '2025-07-25T15:51:43.942304+00:00', '2025-07-25T15:51:43.942304+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1332
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2309, 6, '270309-2', 'JESIFIEL Arnout Silva Sobrinho', 'JESIFIEL ', 
    '998.643.473-49', '10.413-14', '', '1984-05-23', 'M', 'PRACAS', 
    '3S', '2014-07-07', '2023-07-18', 'AT', 
    'jesifiel@gmail.com', '(86) 3 3236-6912', '(86) 9 9442-6505', NULL, 
    '2025-07-25T15:51:42.963512+00:00', '2025-07-25T15:51:42.963512+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1331
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2307, 4, '244862-9', 'João Bezerra NOVAES Neto', 'NOVAES ', 
    '997.842.973-53', '10.354-11', '', '1990-09-15', 'M', 'PRACAS', 
    '3S', '2011-06-16', '2023-07-18', 'AT', 
    'joaonbneto@hotmail.com', '(86) 3 2144-4398', '(86) 9 9998-1107', NULL, 
    '2025-07-25T15:51:41.017501+00:00', '2025-07-25T15:51:41.017501+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1329
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2313, 10, '270321-1', 'Josué FELICIANO de Melo', 'FELICIANO ', 
    '652.939.833-34', '10.409-14', '', '1980-08-26', 'M', 'PRACAS', 
    '3S', '2014-07-07', '2024-12-25', 'AT', 
    'joshuahenry8@hotmail.com', '(86) 9 8822-7225', '(86) 9 8822-7225', NULL, 
    '2025-07-25T15:51:46.829613+00:00', '2025-07-25T15:51:46.829613+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1335
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2305, 2, '270312-2', 'Manoel Antonio de FRANÇA JÚNIOR', 'FRANÇA JÚNIOR ', 
    '909.497.813-04', '10.406-13', '', '1980-05-27', 'M', 'PRACAS', 
    '3S', '2013-05-08', '2023-07-18', 'AT', 
    'manoeljj3@hotmail.com', '(89) 3 4653-3148', '(89) 9 9997-9875', NULL, 
    '2025-07-25T15:51:38.934035+00:00', '2025-07-25T15:51:38.934035+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1327
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2304, 1, '270314-9', 'RAMON Thiago Pereira da Costa', 'RAMON ', 
    '035.972.603-81', '10.412-14', '', '1990-08-19', 'M', 'PRACAS', 
    '3S', '2014-07-07', '2023-07-18', 'AT', 
    'ramonthiago00@hotmail.com', '(86) 9 9950-9486', '(86) 9 8822-1520', NULL, 
    '2025-07-25T15:51:37.991251+00:00', '2025-07-25T15:51:37.991251+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1326
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2312, 9, '270315-7', 'RENATA Pereira dos Santos Silveira', 'RENATA ', 
    '007.660.793-33', '10.408-13', '', '1984-08-23', 'F', 'PRACAS', 
    '3S', '2013-05-08', '2024-12-25', 'AT', 
    'nanaka23@hotmail.com', '(86) 9 8840-1833', '(86) 9 9850-1566', NULL, 
    '2025-07-25T15:51:45.859893+00:00', '2025-07-25T15:51:45.859893+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1334
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2351, 38, '332422-2', 'Albert Moreira de MENDONÇA', 'MENDONÇA ', 
    '045.001.653-63', '10.442-18', '', '1991-09-02', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9930-3548', '', NULL, 
    '2025-07-25T15:52:24.375327+00:00', '2025-07-25T15:52:24.375327+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1373
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2350, 37, '332431-1', 'Alcenir Augusto Barbosa DORNEL', 'DORNEL ', 
    '057.998.853-84', '10.451-18', '', '1993-05-03', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    'alcenirdornel@hotmail.com', '(86) 9 9440-6759', '(86) 9 9825-5992', NULL, 
    '2025-07-25T15:52:23.396577+00:00', '2025-07-25T15:52:23.396577+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1372
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2333, 20, '332412-5', 'Antonio BARROS Leal Neto', 'BARROS ', 
    '039.392.803-99', '10.458-18', '', '1992-01-10', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9922-1006', '', NULL, 
    '2025-07-25T15:52:06.173682+00:00', '2025-07-25T15:52:06.173682+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1355
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2339, 26, '332399-4', 'APARISA Maria Coêlho dos Santos', 'APARISA ', 
    '014.440.613-64', '10.479-18', '', '1987-07-16', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9998-0160', '', NULL, 
    '2025-07-25T15:52:12.008014+00:00', '2025-07-25T15:52:12.008014+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1361
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2327, 14, '332424-9', 'Bruno GONÇALVES Costa', 'GONÇALVES ', 
    '059.739.813-55', '10.444-18', '', '1996-01-24', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 8830-9342', '', NULL, 
    '2025-07-25T15:52:00.131058+00:00', '2025-07-25T15:52:00.131058+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1349
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2352, 39, '332443-5', 'DANYELLE Ribeiro da Silva', 'DANYELLE ', 
    '053.860.743-26', '10.437-18', '', '1992-04-01', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:25.331314+00:00', '2025-07-25T15:52:25.331314+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1374
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2330, 17, '332428-1', 'DARLAN Cunha Lima Filho', 'DARLAN ', 
    '055.022.463-70', '10.448-18', '', '1993-02-05', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9986-6449', '', NULL, 
    '2025-07-25T15:52:02.991165+00:00', '2025-07-25T15:52:02.991165+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1352
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2364, 51, '332404-4', 'DICLEYSON Pereira da Rocha ', 'DICLEYSON ', 
    '029.871.483-30', '10.485-18', '', '1987-03-31', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '(86) 3 2205-5816', '(86) 9 9961-1784', NULL, 
    '2025-07-25T15:52:37.203231+00:00', '2025-07-25T15:52:37.203231+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1386
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2340, 27, '332442-7', 'DOUGLAS Teixeira Ferro', 'DOUGLAS ', 
    '024.341.673-30', '10.436-18', '', '1991-05-03', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    'douglastf91@hotmail.com', '(89) 8 828--2820', '(89) 9 9929-0265', NULL, 
    '2025-07-25T15:52:12.947695+00:00', '2025-07-25T15:52:12.947695+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1362
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2348, 35, '332451-6', 'Erida THAYNARA Assunção Araújo da Silva', 'THAYNARA ', 
    '060.967.643-12', '10.472-18', '', '1995-10-16', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:21.503048+00:00', '2025-07-25T15:52:21.503048+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1370
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2314, 1, '332464-8', 'FÁBIO de SOUSA da Silva', 'FÁBIO ', 
    '026.384.463-35', '10.439-18', '', '1987-06-01', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    'fabiosousa.adm@outlook.com', '(86) 9 9829-1221', '(86) 9 9829-1221', NULL, 
    '2025-07-25T15:51:47.787013+00:00', '2025-07-25T15:51:47.787013+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1336
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2344, 31, '332420-6', 'Fabrício de MOURA Medeiros ', 'MOURA ', 
    '054.978.363-64', '10.440-18', '', '1993-08-02', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9959-1848', '', NULL, 
    '2025-07-25T15:52:16.704231+00:00', '2025-07-25T15:52:16.704231+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1366
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2361, 48, '332456-7', 'Fagner Jairo Fernandes de MEDEIROS ', 'MEDEIROS ', 
    '074.226.404-13', '10.490-18', '', '1988-06-11', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:33.904174+00:00', '2025-07-25T15:52:33.904174+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1383
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2359, 46, '332402-8', 'Francisco CARLOS da Silva Borges ', 'CARLOS ', 
    '044.295.433-64', '10.483-18', '', '1990-08-25', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '(86) 8 8872-2461', '(86) 9 9812-6575', NULL, 
    '2025-07-25T15:52:32.073209+00:00', '2025-07-25T15:52:32.073209+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1381
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2358, 45, '332400-1', 'Francisco Eduardo Alves RIOS ', 'RIOS ', 
    '061.914.993-02', '10.481-18', '', '1996-02-22', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:31.152127+00:00', '2025-07-25T15:52:31.152127+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1380
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2321, 8, '332436-2', 'Francisco MARQUES Brito Neto', 'MARQUES ', 
    '016.750.333-23', '10.430-18', '', '1986-10-11', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 8811-3058', '', NULL, 
    '2025-07-25T15:51:54.476700+00:00', '2025-07-25T15:51:54.476700+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1343
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2349, 36, '332433-8', 'Giovanni PIO Viana', 'PIO ', 
    '025.219.633-30', '10.427-18', '', '1987-02-25', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:22.441134+00:00', '2025-07-25T15:52:22.441134+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1371
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2353, 40, '332454-X', 'GUSTAVO Marques da Silva Alves ', 'GUSTAVO ', 
    '023.245.813-88', '10.475-18', '', '1988-04-05', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9503-1093', '(86) 9 9474-0244', NULL, 
    '2025-07-25T15:52:26.274835+00:00', '2025-07-25T15:52:26.274835+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1375
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2317, 4, '332425-7', 'IGOR Araujo Ferreira', 'IGOR ', 
    '066.039.991-10', '10.445-18', '', '1998-08-21', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:51:50.640900+00:00', '2025-07-25T15:51:50.640900+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1339
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2342, 29, '332430-3', 'JACKSON da Silva Bezerra', 'JACKSON ', 
    '052.159.653-07', '10.450-18', '', '1994-02-04', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9426-6618', '', NULL, 
    '2025-07-25T15:52:14.822055+00:00', '2025-07-25T15:52:14.822055+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1364
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2336, 23, '332398-6', 'Jackson de Melo SALES', 'SALES ', 
    '048.815.953-93', '10.478-18', '', '1991-07-18', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9800-5380', '', NULL, 
    '2025-07-25T15:52:09.139741+00:00', '2025-07-25T15:52:09.139741+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1358
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2356, 43, '332455-9', 'James Rodrigues de FRANÇA ', 'FRANÇA ', 
    '042.487.853-40', '10.489-18', '', '1988-11-28', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '(89) 9 9383-0855', '', NULL, 
    '2025-07-25T15:52:29.184044+00:00', '2025-07-25T15:52:29.184044+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1378
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2341, 28, '270308-4', 'JARDEL Carlos Santana Abreu', 'JARDEL ', 
    '010.622.353-47', '10.410-14', '', '1986-07-04', 'M', 'PRACAS', 
    'CAB', '2014-07-07', '2023-12-25', 'AT', 
    '', '(86) 9 8827-0952', '(86) 9 9475-0946', NULL, 
    '2025-07-25T15:52:13.879109+00:00', '2025-07-25T15:52:13.879109+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1363
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2338, 25, '332434-6', 'JESSÉ dos Santos Ribeiro', 'JESSÉ ', 
    '061.597.803-79', '10.428-18', '', '1993-09-09', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9902-3857', '(86) 9 8863-0293', NULL, 
    '2025-07-25T15:52:11.069377+00:00', '2025-07-25T15:52:11.069377+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1360
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2316, 3, '332439-7', 'Josiel AFONSO dos Santos', 'AFONSO ', 
    '061.496.833-03', '10.433-18', '', '1995-03-29', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9454-8821', '(89) 9 8128-6933', NULL, 
    '2025-07-25T15:51:49.691813+00:00', '2025-07-25T15:51:49.691813+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1338
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2346, 33, '332472-9', 'KLAUS Henrique Martins de Morais', 'KLAUS', 
    '039.914.773-00', '10.480-18', '', '1992-09-20', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9413-5382', '', NULL, 
    '2025-07-25T15:52:19.422315+00:00', '2025-07-25T15:52:19.422315+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1368
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2354, 41, '332415-0', 'Laécio WILSON Cordato Pereira', 'WILSON ', 
    '041.458.843-61', '10.462-18', '', '1989-03-04', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9401-7272', '', NULL, 
    '2025-07-25T15:52:27.189847+00:00', '2025-07-25T15:52:27.189847+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1376
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2347, 34, '332452-4', 'Leandro DO VALE Teixeira Cunha ', 'DO VALE ', 
    '026.964.093-23', '10.473-18', '', '1987-11-30', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9974-4939', '(86) 9 9473-3397', NULL, 
    '2025-07-25T15:52:20.573939+00:00', '2025-07-25T15:52:20.573939+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1369
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2325, 12, '332413-3', 'Leonardo Alexandre MACIEL Deodato', 'MACIEL ', 
    '071.212.353-90', '10.459-18', '', '1996-03-27', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9590-3560', '', NULL, 
    '2025-07-25T15:51:58.233560+00:00', '2025-07-25T15:51:58.233560+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1347
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2315, 2, '332426-5', 'LEONARDO Moreira Gomes Alves Rufino', 'LEONARDO ', 
    '048.440.493-80', '10.446-18', '', '1993-03-15', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9968-6411', '(86) 9 3223-4140', NULL, 
    '2025-07-25T15:51:48.740155+00:00', '2025-07-25T15:51:48.740155+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1337
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2355, 42, '332448-6', 'LUCAS Ribeiro Cardoso', 'LUCAS ', 
    '045.509.971-50', '10.469-18', '', '1994-03-11', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9412-0349', '(86) 9 9427-0579', NULL, 
    '2025-07-25T15:52:28.131403+00:00', '2025-07-25T15:52:28.131403+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1377
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2328, 15, '332453-2', 'Luis Henrique de ALBUQUERQUE Lustosa', 'ALBUQUERQUE ', 
    '036.953.903-60', '10.474-18', '', '1992-06-21', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:01.073778+00:00', '2025-07-25T15:52:01.073778+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1350
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2323, 10, '332419-2', 'Luiz Silva CASTRO', 'CASTRO ', 
    '032.538.933-08', '10.466-18', '', '1990-12-16', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9909-7634', '(86) 9 9904-1033', NULL, 
    '2025-07-25T15:51:56.347155+00:00', '2025-07-25T15:51:56.347155+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1345
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2326, 13, '332396-0', 'Marcos FERNANDES da Silva Rocha', 'FERNANDES ', 
    '061.168.693-78', '10.476-18', '', '1996-07-08', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9446-8888', '', NULL, 
    '2025-07-25T15:51:59.182110+00:00', '2025-07-25T15:51:59.182110+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1348
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2360, 47, '332447-8', 'MYSSHELEN Ribeiro Cardoso ', 'MYSSHELEN ', 
    '060.470.083-05', '10.488-18', '', '1996-04-05', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '(86) 9 8826-9575', '(86) 9 9936-3154', NULL, 
    '2025-07-25T15:52:32.988306+00:00', '2025-07-25T15:52:32.988306+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1382
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2334, 21, '332450-8', 'NATALY Cristina Silva Carvalho Costa', 'NATALY ', 
    '021.737.893-50', '10.471-18', '', '1989-05-16', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9985-0231', '', NULL, 
    '2025-07-25T15:52:07.208430+00:00', '2025-07-25T15:52:07.208430+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1356
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2319, 6, '332414-1', 'NAYARA de Araujo Luz', 'NAYARA ', 
    '021.629.313-89', '10.461-18', '', '1987-05-19', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9983-6290', '', NULL, 
    '2025-07-25T15:51:52.587002+00:00', '2025-07-25T15:51:52.587002+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1341
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2322, 9, '332397-8', 'NAYRON Isack Oliveira Melo ', 'NAYRON ', 
    '025.384.183-64', '10.477-18', '', '1987-10-02', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9257-7408', '', NULL, 
    '2025-07-25T15:51:55.432629+00:00', '2025-07-25T15:51:55.432629+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1344
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2318, 5, '332444-3', 'Paulo Santiago Lima Dantas BRANDÃO', 'BRANDÃO ', 
    '054.982.513-43', '10.438-18', '', '1992-10-25', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9544-6582', '', NULL, 
    '2025-07-25T15:51:51.620319+00:00', '2025-07-25T15:51:51.620319+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1340
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2343, 30, '332408-7', 'Paulo Thiago de Jesus BANDEIRA', 'BANDEIRA ', 
    '032.029.673-39', '10.454-18', '', '1992-11-16', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:15.773024+00:00', '2025-07-25T15:52:15.773024+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1365
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2362, 49, '332403-6', 'Pedro Henrigue Carvalho de OLIVEIRA', 'OLIVEIRA ', 
    '023.996.613-97', '10.484-18', '', '1990-04-01', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    'pedrohenrique@hotmail.com', '', '(86) 9 9803-5675', NULL, 
    '2025-07-25T15:52:34.851592+00:00', '2025-07-25T15:52:34.851592+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1384
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2331, 18, '332410-9', 'Raphael Rubens de Sousa CAMPELO', 'CAMPELO ', 
    '037.964.253-05', '10.456-18', '', '1988-06-17', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9915-2174', '', NULL, 
    '2025-07-25T15:52:04.157832+00:00', '2025-07-25T15:52:04.157832+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1353
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2357, 44, '332421-4', 'Ricardo DA SILVA Batista ', 'DA SILVA ', 
    '052.931.763-07', '10.441-18', '', '1992-07-21', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '(86) 9 9572-2778', '', NULL, 
    '2025-07-25T15:52:30.229169+00:00', '2025-07-25T15:52:30.229169+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1379
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2345, 32, '332401-0', 'Rildo de Sousa Araújo JÚNIOR', 'JUNIOR', 
    '045.773.123-01', '10.482-18', '', '1993-12-06', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    'reldojunior@icloud.com', '(86) 9 839--1276', '(86) 9 9839-1276', NULL, 
    '2025-07-25T15:52:17.623433+00:00', '2025-07-25T15:52:17.623433+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1367
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2320, 7, '332437-X', 'RÔMULO Castelo Branco Bezerra Filho', 'RÔMULO ', 
    '047.517.863-77', '10.431-18', '', '1993-03-18', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9985-3063', '(86) 9 9922-5885', NULL, 
    '2025-07-25T15:51:53.530053+00:00', '2025-07-25T15:51:53.530053+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1342
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2324, 11, '332435-4', 'Ronand Santos Ferreira DANTAS', 'DANTAS ', 
    '021.650.103-22', '10.429-18', '', '1989-07-05', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(89) 9 9924-2520', '', NULL, 
    '2025-07-25T15:51:57.293189+00:00', '2025-07-25T15:51:57.293189+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1346
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2337, 24, '332409-5', 'TÁCITTO Pimentel Albuquerque', 'TÁCITTO ', 
    '024.166.513-23', '10.455-18', '', '1992-11-23', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 3 2291-1093', '(86) 9 9902-1535', NULL, 
    '2025-07-25T15:52:10.107457+00:00', '2025-07-25T15:52:10.107457+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1359
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2335, 22, '332427-3', 'TALYSSON Aguiar Alves de Oliveira', 'TALYSSON ', 
    '051.636.663-71', '10.447-18', '', '1990-12-24', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9847-2851', '', NULL, 
    '2025-07-25T15:52:08.191409+00:00', '2025-07-25T15:52:08.191409+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1357
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2332, 19, '332411-7', 'TAMIRES Silva Santos', 'TAMIRES ', 
    '055.046.203-17', '10.457-18', '', '1995-08-24', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 9 9458-5588', '', NULL, 
    '2025-07-25T15:52:05.124897+00:00', '2025-07-25T15:52:05.124897+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1354
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2363, 50, '332405-2', 'VÍTOR de Araújo Brito ', 'VÍTOR ', 
    '013.543.711-35', '10.486-18', '', '1996-12-01', 'M', 'PRACAS', 
    'CAB', '2018-12-26', '2024-07-18', 'AT', 
    '', '(86) 9 9983-9639', '', NULL, 
    '2025-07-25T15:52:35.836204+00:00', '2025-07-25T15:52:35.836204+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1385
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2329, 16, '332438-9', 'WEILLA da Silva Araujo', 'WEILLA ', 
    '043.563.933-17', '10.432-18', '', '1990-01-14', 'F', 'PRACAS', 
    'CAB', '2018-12-26', '2023-12-25', 'AT', 
    '', '(86) 3 2184-4733', '(86) 9 9991-7159', NULL, 
    '2025-07-25T15:52:02.032256+00:00', '2025-07-25T15:52:02.032256+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1351
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2070, 2, '015241-2', 'CLEMILTON Aquino Almeida', 'CLEMILTON', 
    '361.367.943-49', 'GIP 10.9131', 'CBMEPI', '1967-03-18', 'M', 'COMB', 
    'CB', '1991-02-01', '2022-07-18', 'AT', 
    'clemiltonalmeida@hotmail.com', '(86) 32241-1646', '(86) 98875-4265', NULL, 
    '2025-07-25T15:47:44.069029+00:00', '2025-07-28T11:31:37.487709+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1092
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2072, 5, '084167-6', 'EGÍDIO Nóbrega de Carvalho LEITE', 'EGÍDIO LEITE ', 
    '681.781.823-00', 'GIP 10.11133', '', '1974-12-24', 'M', 'COMB', 
    'CB', '1994-01-01', '2024-07-18', 'AT', 
    'egidioncl@gmail.com', '(86) 3 2161-1263', '(86) 9 9945-2507', NULL, 
    '2025-07-25T15:47:46.085103+00:00', '2025-07-25T15:47:46.085103+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1094
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2069, 1, '015242-X', 'EMÍDIO José Medeiros de Oliveira', 'EMÍDIO', 
    '436.982.393-53', 'GIP 10.9132', 'CBMEPI', '1970-09-25', 'M', 'COMB', 
    'CB', '1991-02-01', '2020-07-18', 'AT', 
    'emidiomedeiros@hotmail.com', '(86) 32271-1884', '(86) 99803-2777', NULL, 
    '2025-07-25T15:47:43.025021+00:00', '2025-07-28T11:30:20.815284+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1091
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2068, 3, '080735-4', 'José VELOSO Soares', 'VELOSO', 
    '351.104.653-04', 'GIP 10.10576', 'CBMEPI', '1969-07-04', 'M', 'COMB', 
    'CB', '1993-02-01', '2022-07-18', 'AT', 
    'josevellloso@yahoo.com.br', '(86) 32292-2543', '(86) 99902-0602', NULL, 
    '2025-07-25T15:47:41.931498+00:00', '2025-07-28T11:31:24.249415+00:00', NULL, 
    true, true, 
    false, NULL, false, 
    false, true, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1090
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2073, 6, '084166-8', 'Josué Clementino de MOURA', 'MOURA ', 
    '590.364.273-04', 'GIP 10.11134', '', '1972-04-15', 'M', 'COMB', 
    'CB', '1994-01-01', '2024-07-18', 'AT', 
    '', '(86) 3 2162-2622', '(86) 9 9986-4377', NULL, 
    '2025-07-25T15:47:47.070255+00:00', '2025-07-25T15:47:47.070255+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1095
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2071, 4, '084168-4', 'Vinicius de CARVALHO LEAL', 'CARVALHO LEAL ', 
    '700.904.593-34', 'GIP 10.11132', '', '1975-06-25', 'M', 'COMB', 
    'CB', '1994-01-01', '2023-07-18', 'AT', 
    'viniciusbombeiro@hotmail.com', '(86) 3 2227-7282', '(86) 9 9982-3615', NULL, 
    '2025-07-25T15:47:45.070455+00:00', '2025-07-25T15:47:45.070455+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1093
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2103, 10, '014177-1', 'AGNALDO Pinheiro dos Santos', 'AGNALDO ', 
    '343.139.403-59', '105.150.673-9', '', '1967-09-28', 'M', 'COMP', 
    'CP', '1987-10-15', '2022-07-18', 'AT', 
    'agnaldogula@hotmail.com', '(86) 3 2264-4028', '(86) 9 8884-4091', NULL, 
    '2025-07-25T15:48:17.534630+00:00', '2025-07-25T15:48:17.534630+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1125
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2111, 18, '323173-9', 'Allisson RANGEL Moura Muniz Martins', 'RANGEL ', 
    '035.901.553-02', '10.417-18', '', '1988-12-06', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:25.360301+00:00', '2025-07-25T15:48:25.360301+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1133
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2123, 31, '014175-5', 'Antonio Carlos da Silva LIRA', 'LIRA ', 
    '306.361.753-91', '105.110.853-6', '', '1966-11-13', 'M', 'COMP', 
    'CP', '1987-10-15', '2023-07-18', 'AT', 
    '', '(86) 9 4780-0636', '', NULL, 
    '2025-07-25T15:48:37.186633+00:00', '2025-07-25T15:48:37.186633+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1145
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2122, 29, '015794-5', 'Antônio CARLOS do NASCIMENTO', 'CARLOS NASCIMENTO ', 
    '327.364.793-00', '105.150.803-2', '', '1967-08-16', 'M', 'COMP', 
    'CP', '1991-10-01', '2023-07-18', 'AT', 
    'tenentecarlosnascimento@gmail.com', '(86) 9 9417-4799', '(86) 9 8893-4453', NULL, 
    '2025-07-25T15:48:36.185362+00:00', '2025-07-25T15:48:36.185362+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1144
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2125, 33, '082787-8', 'Antônio LINHARES de Sousa Filho', 'LINHARES ', 
    '470.983.503-97', 'GIP 10.10729', '', '1973-10-18', 'M', 'COMP', 
    'CP', '1993-09-01', '2024-07-18', 'AT', 
    'tenentelinhares@hotmail.com', '(86) 9 8848-9258', '(86) 9 9405-9661', NULL, 
    '2025-07-25T15:48:39.138119+00:00', '2025-07-25T15:48:39.138119+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1147
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2096, 3, '013022-2', 'Arias PINHO Lima ', 'PINHO ', 
    '350.163.373-49', 'GIP 10.7200', '', '1963-01-03', 'M', 'COMP', 
    'CP', '1985-04-30', '2022-07-18', 'AT', 
    'sargentopinhobm@hotmail.com', '(86) 9 9448-3721', '(86) 9 9448-3721', NULL, 
    '2025-07-25T15:48:09.834268+00:00', '2025-07-25T15:48:09.834268+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1118
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2114, 21, '323176-3', 'ARLINDO Rodrigues de Mesquita Júnior', 'ARLINDO ', 
    '008.469.853-57', '10.419-18', '', '1990-03-01', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:28.503646+00:00', '2025-07-25T15:48:28.503646+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1136
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2100, 7, '082790-8', 'ARNALDO Pereira de Vasconcelos', 'ARNALDO ', 
    '714.333.413-87', 'GIP 10.10719', '', '1973-11-06', 'M', 'COMP', 
    'CP', '1993-09-01', '2022-07-18', 'AT', 
    'arnaldovasconcelos2011@hotmail.com', '(86) 3 2221-1084', '(86) 9 8838-9625', NULL, 
    '2025-07-25T15:48:13.694539+00:00', '2025-07-25T15:48:13.694539+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1122
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2113, 20, '323175-5', 'Augusto CÉSAR Pontes Coelho', 'CÉSAR ', 
    '600.319.703-03', '10.418-18 ', '', '1987-11-20', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    '', '', '(86) 9 9901-2471', NULL, 
    '2025-07-25T15:48:27.441850+00:00', '2025-07-25T15:48:27.441850+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1135
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2097, 4, '015020-7', 'DIÔGO Martins Fonseca Neto', 'DIÔGO ', 
    '421.275.213-15', 'GIP 10.8903', '', '1970-08-09', 'M', 'COMP', 
    'CP', '1990-07-01', '2022-07-18', 'AT', 
    'diogo.martinsfonsecaneto193@gmail.com', '(86) 9 9432-6043', '(86) 9 9432-6043', NULL, 
    '2025-07-25T15:48:10.809276+00:00', '2025-07-25T15:48:10.809276+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1119
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2098, 5, '014095-3', 'EVARISTO Francisco Rodrigues', 'EVARISTO ', 
    '343.088.733-04', 'GIP 10.8050', '', '1966-01-05', 'M', 'COMP', 
    'CP', '1987-03-01', '2022-07-18', 'AT', 
    '', '(86) 9 8877-0788', '(86) 9 9539-4105', NULL, 
    '2025-07-25T15:48:11.773002+00:00', '2025-07-25T15:48:11.773002+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1120
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2117, 24, '323169-X', 'EVERTON Almeida da Silva', 'EVERTON ', 
    '024.953.003-16', '10.369-11', '', '1989-01-25', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    'evertonbmpi@gmail.com', '(86) 9 9451-4584', '', NULL, 
    '2025-07-25T15:48:31.370934+00:00', '2025-07-25T15:48:31.370934+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1139
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2104, 11, '013009-5', 'Francisco Nonato SANTOS SILVA ', 'SANTOS SILVA ', 
    '340.067.963-15', 'GIP 10.7168', '', '1962-08-17', 'M', 'COMP', 
    'CP', '1985-04-30', '2022-07-18', 'AT', 
    '', '(86) 9 9424-9634', '(86) 9 8848-3222', NULL, 
    '2025-07-25T15:48:18.596590+00:00', '2025-07-25T15:48:18.596590+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1126
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2118, 25, '323170-4', 'IVAN Ribeiro Feitosa', 'IVAN ', 
    '003.196.073-13', '10.422-18', '', '1983-10-01', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    'ivannessa@hotmail.com', '(86) 3 2971-1382', '(86) 9 9938-2295', NULL, 
    '2025-07-25T15:48:32.340166+00:00', '2025-07-25T15:48:32.340166+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1140
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2095, 2, '013600-0', 'José EPITÁCIO da Silva Filho ', 'EPITÁCIO ', 
    '421.649.234-72', 'GIP 10.7743', '', '1964-06-18', 'M', 'COMP', 
    'CP', '1986-05-30', '2022-07-18', 'AT', 
    '', '(86) 3 2131-1627', '(86) 9 8811-7326', NULL, 
    '2025-07-25T15:48:08.873998+00:00', '2025-07-25T15:48:08.873998+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1117
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2110, 17, '014325-1', 'José Francisco Alves da VERA CRUZ', 'VERA CRUZ ', 
    '227.776.793-04', 'GIP 10.8226', '', '1964-11-26', 'M', 'COMP', 
    'CP', '1988-08-05', '2022-12-23', 'AT', 
    '', '(86) 9 4121-1521', '(86) 9 9911-3089', NULL, 
    '2025-07-25T15:48:24.390427+00:00', '2025-07-25T15:48:24.390427+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1132
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2105, 12, '013030-3', 'JOSÉ GOMES de Oliveira', 'JOSÉ GOMES ', 
    '327.910.543-91', 'GIP 10.7213', '', '1965-03-27', 'M', 'COMP', 
    'CP', '1985-04-30', '2022-07-18', 'AT', 
    'tenentegomesoliveira@gmail.com', '(86) 9 9986-5556', '(86) 9 9928-1909', NULL, 
    '2025-07-25T15:48:19.541916+00:00', '2025-07-25T15:48:19.541916+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1127
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2106, 13, '014048-1', 'José LIMA FILHO', 'LIMA ', 
    '240.972.173-72', '105.065.983-6', '', '1964-07-21', 'M', 'COMP', 
    'CP', '1987-01-29', '2022-07-18', 'AT', 
    'limafilhobombeiro@hotmail.com', '(86) 3 3153-3300', '(86) 9 9400-1011', NULL, 
    '2025-07-25T15:48:20.516259+00:00', '2025-07-25T15:48:20.516259+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1128
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2101, 8, '014188-7', 'José NILTON da Costa', 'NILTON ', 
    '327.579.483-34', '105.149.153-6', '', '1967-07-18', 'M', 'COMP', 
    'CP', '1987-01-15', '2022-07-18', 'AT', 
    '', '(86) 9 8846-4059', '(86) 9 9994-0712', NULL, 
    '2025-07-25T15:48:14.658639+00:00', '2025-07-25T15:48:14.658639+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1123
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2116, 23, '323168-2', 'JUAREZ José  de Sousa Júnior', 'JUAREZ ', 
    '006.957.613-07', '10.421-18 ', '', '1984-04-03', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    'juarezjunior003@gmail.com', '(86) 8 8072-2266', '(86) 9 8807-2266', NULL, 
    '2025-07-25T15:48:30.424347+00:00', '2025-07-25T15:48:30.424347+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1138
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2112, 19, '323174-7', 'LUCAS XAVIER Vieira Lopes', 'LUCAS XAVIER ', 
    '026.787.963-61', '10.314-08', '', '1988-08-20', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    'lucasxavierbm@hotmail.com', '(86) 3 3221-1743', '(86) 9 9853-8858', NULL, 
    '2025-07-25T15:48:26.339061+00:00', '2025-07-25T15:48:26.339061+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1134
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2108, 15, '298731-7', 'MARCOS PAULO de Arêa Lira', 'MARCOS PAULO ', 
    '008.696.843-29', '10.425-16', '', '1984-10-02', 'M', 'ENG', 
    'CP', '2015-12-21', '2022-12-23', 'AT', 
    '', '(86) 9 9998-0286', '(86) 9 3231-7244', NULL, 
    '2025-07-25T15:48:22.443122+00:00', '2025-07-25T15:48:22.443122+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1130
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2099, 6, '014193-3', 'MIGUEL Rodrigues de Sousa', 'MIGUEL ', 
    '327.348.673-20', '105.147.523-2', '', '1966-09-29', 'M', 'COMP', 
    'CP', '1987-10-15', '2022-07-18', 'AT', 
    '', '(86) 9 9496-8028', '(86) 9 9496-8028', NULL, 
    '2025-07-25T15:48:12.721622+00:00', '2025-07-25T15:48:12.721622+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1121
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2102, 9, '013021-4', 'Pedro CARDOSO da Silva Neto', 'CARDOSO ', 
    '350.163.293-20', 'GIP 10.7199', '', '1964-02-02', 'M', 'COMP', 
    'CP', '1985-04-30', '2022-07-18', 'AT', 
    '', '(86) 3 2113-3708', '(86) 9 9487-3820', NULL, 
    '2025-07-25T15:48:16.259806+00:00', '2025-07-25T15:48:16.259806+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1124
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2120, 27, '323172-X', 'PRYCILLA Oliveira Garcia', 'PRYCILLA ', 
    '024.038.323-08', '10.424-18', '', '1988-08-04', 'F', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:34.242319+00:00', '2025-07-25T15:48:34.242319+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1142
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2124, 32, '014570-0', 'Raimundo DIAS da Silva Filho', 'DIAS ', 
    '327.361.343-20', 'GIP 10.8489', '', '1968-10-18', 'M', 'COMP', 
    'CP', '1989-08-01', '2024-07-18', 'AT', 
    'gyvago@bol.com.br', '(86) 3 2294-4232', '(86) 9 9495-0297', NULL, 
    '2025-07-25T15:48:38.169308+00:00', '2025-07-25T15:48:38.169308+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1146
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2107, 14, '014195-0', 'Raimundo Nonato Mendes BATISTA', 'BATISTA ', 
    '240.950.603-87', '105.064.953-0', '', '1965-02-25', 'M', 'COMP', 
    'CP', '1987-10-15', '2022-07-18', 'AT', 
    '', '(86) 3 2117-7568', '(86) 9 9972-3692', NULL, 
    '2025-07-25T15:48:21.484908+00:00', '2025-07-25T15:48:21.484908+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1129
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2126, 34, '015016-9', 'Sebastião DOMINGOS de Carvalho Filho', 'DOMINGOS ', 
    '444.228.903-44', 'GIP 10.8899', '', '1970-12-04', 'M', 'COMP', 
    'CP', '1990-07-01', '2024-07-18', 'AT', 
    '', '(86) 3 2374-4941', '(86) 9 8802-8636', NULL, 
    '2025-07-25T15:48:40.122849+00:00', '2025-07-25T15:48:40.122849+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1148
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2109, 16, '298348-6', 'Sérgio Henrique Reis de ARAGÃO', 'ARAGÃO ', 
    '018.092.843-09', '10.426-16', '', '1986-08-07', 'M', 'ENG', 
    'CP', '2015-12-21', '2022-12-23', 'AT', 
    '', '(86) 9 8854-4050', '', NULL, 
    '2025-07-25T15:48:23.407265+00:00', '2025-07-25T15:48:23.407265+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1131
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2115, 22, '323177-1', 'Thompsom THAUZER Rodrigues de Araújo', 'THAUZER ', 
    '013.636.413-60', '10.420-18', '', '1987-12-18', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:29.456592+00:00', '2025-07-25T15:48:29.456592+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1137
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2119, 26, '323171-2', 'WALBER Meireles Pessoa Júnior', 'WALBER ', 
    '447.024.773-15', '10.423-18', '', '1985-02-27', 'M', 'COMB', 
    'CP', '2018-01-18', '2023-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:33.288228+00:00', '2025-07-25T15:48:33.288228+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1141
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2094, 1, '082771-1', 'WILLIAM Borgéa Lima                       ', 'WILLIAM ', 
    '361.617.993-91', 'GIP 10.10714', '', '1969-11-13', 'M', 'COMP', 
    'CP', '1993-09-01', '2021-12-23', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:48:07.923513+00:00', '2025-07-25T15:48:07.923513+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1116
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2121, 28, '014197-6', 'WILSON Alves Cardoso', 'WILSON ', 
    '421.273.353-68', '105.153.213-1', '', '1967-07-10', 'M', 'COMP', 
    'CP', '1987-10-15', '2023-07-18', 'AT', 
    '', '(86) 3 2255-5426', '(86) 9 9993-7684', NULL, 
    '2025-07-25T15:48:35.227743+00:00', '2025-07-25T15:48:35.227743+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1143
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2091, 5, '014578-5', 'Chaga MACHADO de Araújo', 'MACHADO ', 
    '304.924.913-72', 'GIP 10.8503', '', '1967-06-11', 'M', 'COMP', 
    'MJ', '1989-08-01', '2023-07-18', 'AT', 
    'machado2019@hotmail.com', '(86) 9 9246-6870', '(86) 9 9927-5042', NULL, 
    '2025-07-25T15:48:05.026166+00:00', '2025-07-25T15:48:05.026166+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1113
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2090, 4, '082908-X', 'FLAUBERT Rocha Vieira', 'FLAUBERT ', 
    '453.425.803-82', 'GIP 10.10953', '', '1972-12-09', 'M', 'COMP', 
    'MJ', '1993-09-01', '2023-07-18', 'AT', 
    'sgtflaubert@gmail.com', '(86) 8 8094-4098', '(86) 9 8174-1919', NULL, 
    '2025-07-25T15:48:04.068959+00:00', '2025-07-25T15:48:04.068959+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1112
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2087, 1, '013100-8', 'Francisco das Chagas TAVARES de Sousa', 'TAVARES ', 
    '342.306.373-49', 'GIP 10.7318', '', '1962-10-04', 'M', 'COMP', 
    'MJ', '1985-07-01', '2022-07-18', 'AT', 
    'thavarys@hotmail.com', '(86) 9 8155-5852', '(86) 9 9971-8526', NULL, 
    '2025-07-25T15:48:01.208799+00:00', '2025-07-25T15:48:01.208799+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1109
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2092, 6, '013023-X', 'Francisco de Assis COSTA SILVA', 'COSTA SILVA ', 
    '342.595.973-53', 'GIP 10.7201', '', '1962-04-04', 'M', 'COMP', 
    'MJ', '1985-04-30', '2023-12-25', 'AT', 
    'sgtcostabm@hotmail.com', '(86) 3 3217-7721', '(86) 9 9531-3145', NULL, 
    '2025-07-25T15:48:05.986406+00:00', '2025-07-25T15:48:05.986406+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1114
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2088, 2, '085367-4', 'José ERISMAN de Sousa', 'ERISMAN', 
    '490.083.823-34', 'GIP 10.11732', 'CBMEPI', '1975-04-17', 'M', 'COMP', 
    'MJ', '1994-03-01', '2022-12-23', 'AT', 
    'majorbmrerisman@gmail.com', '(86) 32111-1117', '(86) 98849-0120', 'fotos_militares/erisman.jpg', 
    '2025-07-25T15:48:02.159814+00:00', '2025-07-28T13:30:34.953755+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1110
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2089, 3, '014086-4', 'NÉLIO de Oliveira Cordeiro', 'NÉLIO ', 
    '306.996.493-15', 'GIP 10.8026', '', '1965-04-27', 'M', 'COMP', 
    'MJ', '1987-03-01', '2023-07-18', 'AT', 
    'neliooc@outlook.com', '(86) 9 9111-1158', '(86) 9 9911-1158', NULL, 
    '2025-07-25T15:48:03.117350+00:00', '2025-07-25T15:48:03.117350+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1111
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2410, 47, '416708-2', 'ABIMAEL HONÓRIO CORREIA JÚNIOR', 'ABIMAEL', 
    '031.910.963-10', '10.505-24', '', '1991-03-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9403-2200', NULL, 
    '2025-07-25T15:53:25.650183+00:00', '2025-07-25T15:53:25.650183+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1432
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2499, 136, '416904-2', 'ADRIANO AMARANES DOS SANTOS', 'AMARANES', 
    '038.590.893-82', '10.506-24', '', '1990-10-28', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 0000-0000', NULL, 
    '2025-07-25T15:54:56.625370+00:00', '2025-07-25T15:54:56.625370+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1521
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2460, 97, '416707-4', 'AFONSO AMORIM DE SOUSA FILHO', 'FILHO', 
    '065.241.623-31', '10.507-24', '', '1999-04-12', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9262-2630', '(86) 9 0000-0000', NULL, 
    '2025-07-25T15:54:15.130304+00:00', '2025-07-25T15:54:15.130304+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1482
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2458, 95, '416709-X', 'AIRTON PEREIRA DE SOUSA', 'AIRTON', 
    '072.086.943-97', '10.508-24', '', '1999-01-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 0000-0000', NULL, 
    '2025-07-25T15:54:13.033564+00:00', '2025-07-25T15:54:13.033564+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1480
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2381, 18, '416711-2', 'ALEXSIONE COSTA SOUSA', 'ALEXSIONE', 
    '039.932.003-22', '10.510-24', '', '1992-03-01', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 0000-0000', NULL, 
    '2025-07-25T15:52:56.401439+00:00', '2025-07-25T15:52:56.401439+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1403
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2393, 30, '416712-X', 'ALIELSON FERNANDO DA SILVA SOUSA', 'ALIELSON', 
    '071.136.913-58', '10.511-24', '', '2001-11-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 0000-0000', NULL, 
    '2025-07-25T15:53:08.263120+00:00', '2025-07-25T15:53:08.263120+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1415
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2545, 182, '416715-5', 'ALISON RIBEIRO BONFIM', 'BONFIM', 
    '611.010.813-84', '10.514-24', '', '1996-02-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(99) 9 8140-3901', NULL, 
    '2025-07-25T15:55:43.896300+00:00', '2025-07-25T15:55:43.896300+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1567
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2427, 64, '416716-3', 'ALLAN GARDSON SILVA SALAZAR', 'GARDSON', 
    '044.721.833-66', '10.515-24', '', '1989-10-11', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(99) 9 8213-6854', NULL, 
    '2025-07-25T15:53:41.683187+00:00', '2025-07-25T15:53:41.683187+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1449
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2391, 28, '416718-0', 'ALYNNE LARA DA SILVA ARAUJO', 'LARA', 
    '070.282.063-60', '10.517-24', '', '1998-07-01', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9485-2448', NULL, 
    '2025-07-25T15:53:06.366494+00:00', '2025-07-25T15:53:06.366494+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1413
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2469, 106, '416719-8', 'ALYSSON JORDAN DA SILVA SAMPAIO', 'JORDAN', 
    '074.635.223-93', '10.518-24', '', '1997-10-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9518-5254', NULL, 
    '2025-07-25T15:54:26.205268+00:00', '2025-07-25T15:54:26.205268+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1491
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2386, 23, '416905-X', 'AMARO LUÍS RODRIGUES DE ARAÚJO', 'AMARO', 
    '064.750.683-14', '10.520-24', '', '1996-09-28', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9930-8471', NULL, 
    '2025-07-25T15:53:01.581591+00:00', '2025-07-25T15:53:01.581591+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1408
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2420, 57, '416720-1', 'AMAURY MARTINS CUNHA', 'AMAURY', 
    '054.043.523-61', '10.521-24', '', '1993-01-14', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(83) 9 9639-9048', '(86) 9 9639-9048', NULL, 
    '2025-07-25T15:53:35.199286+00:00', '2025-07-25T15:53:35.199286+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1442
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2411, 48, '416721-0', 'ANA PAULA DOS SANTOS PINHEIRO MARTINS', 'ANA PAULA', 
    '032.250.593-31', '10.522-24', '', '1993-01-03', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9986-5603', NULL, 
    '2025-07-25T15:53:26.615643+00:00', '2025-07-25T15:53:26.615643+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1433
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2430, 67, '417809-2', 'ANDERSON BARROS PEREIRA', 'BARROS', 
    '095.379.814-36', '10.523-24', '', '1991-04-07', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(81) 9 9236-6956', NULL, 
    '2025-07-25T15:53:44.597196+00:00', '2025-07-25T15:53:44.597196+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1452
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2394, 31, '416906-9', 'ANDRÉ FELIPE DO AMARAL OLIVEIRA', 'AMARAL', 
    '057.243.893-12', '10.524-24', '', '1999-01-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8621-0399', NULL, 
    '2025-07-25T15:53:09.211179+00:00', '2025-07-25T15:53:09.211179+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1416
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2432, 69, '416722-8', 'ANDRE LUIS DA COSTA', 'LUÍS COSTA', 
    '072.989.403-76', '10.525-24', '', '1996-05-14', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8827-2075', NULL, 
    '2025-07-25T15:53:46.809551+00:00', '2025-07-25T15:53:46.809551+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1454
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2558, 195, '433915-X', 'ANGELO JOSÉ FONTENELE DOS ANJOS ', 'DOS ANJOS', 
    '009.324.843-10', '10.711-25', '', '1986-05-06', 'M', 'PRACAS', 
    'SD', '2025-04-29', '2025-04-29', 'AT', 
    '', '(86) 9 9973-8515', '(86) 9 9997-3851', NULL, 
    '2025-07-25T15:55:56.434295+00:00', '2025-07-25T15:55:56.434295+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1580
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2375, 12, '416724-4', 'ANTONIA KAROLINE DE OLIVEIRA SOUSA', 'ANTONIA', 
    '048.618.433-16', '10.526-24', '', '1991-07-28', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(99) 9 8197-6803', NULL, 
    '2025-07-25T15:52:48.101506+00:00', '2025-07-25T15:52:48.101506+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1397
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2492, 129, '416723-6', 'ANTONIO MARCOS VIANA FILHO', 'VIANA FILHO', 
    '081.209.393-36', '10.527-24', '', '2001-04-18', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9554-2671', '(86) 9 9554-2671', NULL, 
    '2025-07-25T15:54:48.949932+00:00', '2025-07-25T15:54:48.949932+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1514
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2404, 41, '416725-2', 'ANTONIO SOARES DE MELO NETO', 'ANTÔNIO MELO', 
    '068.006.573-36', '10.528-24', '', '1998-01-09', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:53:18.849708+00:00', '2025-07-25T15:53:18.849708+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1426
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2417, 54, '416726-X', 'ARLLEI MARTINS MUNIZ', 'MUNIZ', 
    '032.684.883-58', '10.529-24', '', '1990-12-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9406-9013', NULL, 
    '2025-07-25T15:53:32.331059+00:00', '2025-07-25T15:53:32.331059+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1439
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2434, 71, '416727-9', 'ARTHUR VALENTE SOARES', 'VALENTE', 
    '044.680.163-10', '10.530-24', '', '1994-11-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 8140-9228', NULL, 
    '2025-07-25T15:53:48.916718+00:00', '2025-07-25T15:53:48.916718+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1456
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2472, 109, '416728-7', 'BERNARDO LUCAS RODRIGUES DO NASCIMENTO', 'BERNARDO', 
    '066.736.293-20', '10.531-24', '', '1998-06-30', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 8840-3803', '(86) 9 8840-3803', NULL, 
    '2025-07-25T15:54:29.098193+00:00', '2025-07-25T15:54:29.098193+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1494
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2431, 68, '416730-9', 'BRUNO HENRIQUE VIEIRA LIMA', 'BRUNO LIMA', 
    '076.208.764-13', '10.533-24', '', '1990-10-16', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(83) 9 9623-0050', NULL, 
    '2025-07-25T15:53:45.701882+00:00', '2025-07-25T15:53:45.701882+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1453
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2535, 172, '416731-7', 'CARLOS EDUARDO ALVES DA SILVA', 'ALVES', 
    '059.606.743-78', '10.534-24', '', '1994-05-02', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9466-7224', NULL, 
    '2025-07-25T15:55:33.168579+00:00', '2025-07-25T15:55:33.168579+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1557
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2380, 17, '416732-5', 'CARLOS EDUARDO PIMENTEL SALUSTIANO', 'CARLOS PIMENTEL', 
    '065.403.713-22', '10.535-24', '', '1995-01-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:52:55.335285+00:00', '2025-07-25T15:52:55.335285+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1402
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2424, 61, '416733-3', 'CAROLINE MERCES DE SOUSA SANTOS', 'MERCÊS', 
    '072.248.163-29', '10.536-24', '', '1998-09-24', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9941-4774', NULL, 
    '2025-07-25T15:53:38.900113+00:00', '2025-07-25T15:53:38.900113+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1446
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2409, 46, '416734-1', 'CRISTO JUNIOR DE CARVALHO SOARES', 'CRISTO JUNIOR', 
    '055.670.473-80', '10.537-24', '', '1993-05-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9425-9141', NULL, 
    '2025-07-25T15:53:24.656398+00:00', '2025-07-25T15:53:24.656398+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1431
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2516, 153, '416735-0', 'DANIEL MARKUS GUIMARÃES MIRANDA', 'MIRANDA', 
    '025.054.983-26', '10.538-24', '', '1998-06-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9410-2515', '(86) 9 9569-3334', NULL, 
    '2025-07-25T15:55:12.753025+00:00', '2025-07-25T15:55:12.753025+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1538
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2519, 156, '417810-6', 'DANIEL VICTOR CARVALHO', 'DANIEL', 
    '034.904.743-09', '10.539-24', '', '1989-10-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8101-8381', NULL, 
    '2025-07-25T15:55:15.527710+00:00', '2025-07-25T15:55:15.527710+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1541
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2511, 148, '416736-8', 'DÁRIO GUILHERME ALVES DE SOUSA', 'DÁRIO', 
    '069.996.403-27', '10.540-24', '', '1998-10-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9521-8384', NULL, 
    '2025-07-25T15:55:08.136242+00:00', '2025-07-25T15:55:08.136242+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1533
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2510, 147, '416737-6', 'DEISON KYLLER VAL MORAES', 'DEISON KYLLER', 
    '024.858.313-19', '10.541-24', '', '1989-10-06', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9939-1020', NULL, 
    '2025-07-25T15:55:07.201868+00:00', '2025-07-25T15:55:07.201868+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1532
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2376, 13, '416738-4', 'DENISE CLARA DE ARAUJO SILVA', 'DENISE', 
    '056.561.153-48', '10.542-24', '', '1994-06-25', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9930-7612', '(86) 9 9930-7612', NULL, 
    '2025-07-25T15:52:49.132278+00:00', '2025-07-25T15:52:49.132278+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1398
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2441, 78, '416739-2', 'DEYVISON DE SOUSA GOMES', 'DEYVISON', 
    '049.635.373-03', '10.543-24', '', '1992-02-10', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:53:56.254862+00:00', '2025-07-25T15:53:56.254862+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1463
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2477, 114, '416740-6', 'DIEGO DE SOUSA BEZERRA', 'BEZERRA', 
    '057.264.863-40', '10.544-24', '', '1994-01-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9830-0462', '(86) 9 9830-4622', NULL, 
    '2025-07-25T15:54:33.968052+00:00', '2025-07-25T15:54:33.968052+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1499
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2538, 175, '416741-4', 'DOUGLAS CARDOSO GUEDES DA SILVA', 'GUEDES', 
    '054.008.293-76', '10.545-24', '', '1991-03-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9473-1194', NULL, 
    '2025-07-25T15:55:36.167793+00:00', '2025-07-25T15:55:36.167793+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1560
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2369, 6, '416742-2', 'DOUGLAS PIRES MENDES', 'PIRES', 
    '060.718.943-60', '10.546-24', '', '1999-08-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9413-3250', '(86) 9 9413-3250', NULL, 
    '2025-07-25T15:52:42.266943+00:00', '2025-07-25T15:52:42.266943+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1391
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2528, 165, '416743-X', 'EDER OLIVEIRA DE SOUSA', 'EDER', 
    '031.258.433-40', '10.547-24', '', '1988-11-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9413-3250', NULL, 
    '2025-07-25T15:55:26.331984+00:00', '2025-07-25T15:55:26.331984+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1550
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2422, 59, '416744-9', 'EDER SANTOS DE MORAES', 'MORAES', 
    '048.549.683-62', '10.548-24', '', '1991-04-11', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9904-5210', '', NULL, 
    '2025-07-25T15:53:37.046760+00:00', '2025-07-25T15:53:37.046760+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1444
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2522, 159, '416745-7', 'EDIEMERSON SOUSA BRITO', 'EDIEMERSON', 
    '070.359.083-90', '10.549-24', '', '1998-03-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:55:18.354897+00:00', '2025-07-25T15:55:18.354897+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1544
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2453, 90, '416746-5', 'EDSON FRANÇA SILVA DE SOUSA', 'EDSON', 
    '062.159.083-55', '10.550-24', '', '1994-06-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9919-2938', NULL, 
    '2025-07-25T15:54:08.001816+00:00', '2025-07-25T15:54:08.001816+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1475
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2532, 169, '416747-3', 'EDUARDO MOURA DA SILVA', 'MOURA', 
    '058.116.293-54', '10.551-24', '', '1994-05-09', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9544-0802', '(86) 9 9544-0802', NULL, 
    '2025-07-25T15:55:30.235507+00:00', '2025-07-25T15:55:30.235507+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1554
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2491, 128, '416748-1', 'ELIESIO ALVES MENDES JUNIOR', 'ELIESIO', 
    '065.372.093-90', '10.552-24', '', '1996-06-03', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 0000-0000', NULL, 
    '2025-07-25T15:54:47.965186+00:00', '2025-07-25T15:54:47.965186+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1513
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2449, 86, '416749-0', 'ELIVELTON DO NASCIMENTO SILVA', 'ELIVELTON', 
    '057.825.603-71', '10.553-24', '', '1993-08-11', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(88) 9 9706-0631', NULL, 
    '2025-07-25T15:54:03.929996+00:00', '2025-07-25T15:54:03.929996+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1471
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2500, 137, '416750-3', 'ELYDA RAVENNE RODRIGUES E SILVA', 'RAVENNE', 
    '067.924.023-38', '10.554-24', '', '1996-01-21', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:57.598936+00:00', '2025-07-25T15:54:57.598936+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1522
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2456, 93, '416751-1', 'EMIELSON DE SOUSA AMÂNCIO', 'EMIELSON', 
    '014.120.453-20', '10.555-24', '', '1987-07-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:10.950865+00:00', '2025-07-25T15:54:10.950865+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1478
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2526, 163, '416898-4', 'EMILIANO MARQUES FARIAS DE ARAÚJO', 'EMILIANO', 
    '037.318.923-08', '10.556-24', '', '1988-09-14', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:55:24.366367+00:00', '2025-07-25T15:55:24.366367+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1548
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2529, 166, '416752-0', 'ERIC FELIPE RODRIGUES DA SILVA', 'RODRIGUES', 
    '067.986.463-60', '10.557-24', '', '1999-05-30', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 8145-5278', '(86) 9 8145-8782', NULL, 
    '2025-07-25T15:55:27.269323+00:00', '2025-07-25T15:55:27.269323+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1551
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2507, 144, '416753-8', 'ÉRIKA FERREIRA E LIRA OLIVEIRA', 'ÉRIKA', 
    '043.462.583-36', '10.558-24', '', '1990-09-01', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:55:04.396498+00:00', '2025-07-25T15:55:04.396498+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1529
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2548, 185, '416754-6', 'ERISVALDO DE CARVALHO FERNANDO', 'ERISVALDO', 
    '041.758.433-45', '10.559-24', '', '1989-04-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9864-5423', '(86) 9 9864-5423', NULL, 
    '2025-07-25T15:55:46.769531+00:00', '2025-07-25T15:55:46.769531+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1570
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2539, 176, '416756-2', 'ESMERALDINO SOARES GODINHO FILHO', 'ESMERALDINO', 
    '046.467.433-61', '10.561-24', '', '1994-05-07', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8896-6818', NULL, 
    '2025-07-25T15:55:37.532622+00:00', '2025-07-25T15:55:37.532622+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1561
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2462, 99, '416757-X', 'EVARISTO DE BARROS ROCHA SEGUNDO', 'SEGUNDO', 
    '047.940.643-06', '10.562-24', '', '1990-05-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9998-8470', '(86) 9 9998-8470', NULL, 
    '2025-07-25T15:54:17.269909+00:00', '2025-07-25T15:54:17.269909+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1484
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2387, 24, '416758-9', 'EZEQUIAS RODRIGUES CAMÊLO', 'EZEQUIAS', 
    '056.633.283-35', '10.563-24', '', '1995-06-12', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9679-2480', NULL, 
    '2025-07-25T15:53:02.527929+00:00', '2025-07-25T15:53:02.527929+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1409
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2459, 96, '416759-7', 'FABIO DE SOUZA CLEMENTINO', 'CLEMENTINO', 
    '600.093.463-76', '10.564-24', '', '1987-07-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8127-9010', NULL, 
    '2025-07-25T15:54:14.093926+00:00', '2025-07-25T15:54:14.093926+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1481
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2446, 83, '416760-X', 'FELIPE AUGUSTO PESSOA SILVEIRA', 'PESSOA', 
    '600.473.003-37', '10.565-24', '', '1990-05-09', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9512-7471', NULL, 
    '2025-07-25T15:54:01.134432+00:00', '2025-07-25T15:54:01.134432+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1468
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2416, 53, '416761-9', 'FELIPE AURÉLIO NUNES DE SOUSA', 'AURÉLIO', 
    '038.979.933-50', '10.566-24', '', '1992-02-14', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9292-4798', NULL, 
    '2025-07-25T15:53:31.396639+00:00', '2025-07-25T15:53:31.396639+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1438
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2527, 164, '416762-7', 'FELIPE DA SILVA VILELA', 'VILELA', 
    '070.789.923-00', '10.567-24', '', '2000-08-01', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9928-9640', NULL, 
    '2025-07-25T15:55:25.362019+00:00', '2025-07-25T15:55:25.362019+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1549
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2503, 140, '416763-5', 'FELIPE DE OLIVEIRA MATOS', 'OLIVEIRA MATOS', 
    '049.599.743-97', '10.568-24', '', '1993-03-03', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9909-9089', NULL, 
    '2025-07-25T15:55:00.619174+00:00', '2025-07-25T15:55:00.619174+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1525
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2383, 20, '416764-3', 'FELIPE RAFAEL DA SILVA', 'FELIPE RAFAEL', 
    '077.265.533-24', '10.569-24', '', '2000-03-31', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9917-3141', NULL, 
    '2025-07-25T15:52:58.681065+00:00', '2025-07-25T15:52:58.681065+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1405
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2473, 110, '416765-1', 'FERNANDO DE OLIVEIRA SILVA', 'FERNANDO', 
    '004.636.623-77', '10.570-24', '', '1988-02-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9812-5027', NULL, 
    '2025-07-25T15:54:30.112937+00:00', '2025-07-25T15:54:30.112937+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1495
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2436, 73, '416896-8', 'FILIPE MELO DE SOUSA', 'MELO SOUSA', 
    '021.423.233-67', '10.571-24', '', '1989-07-06', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:53:50.986121+00:00', '2025-07-25T15:53:50.986121+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1458
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2413, 50, '416766-0', 'FILIPE MOUSINHO LIMA', 'MOUSINHO', 
    '054.681.823-43', '10.572-24', '', '1993-05-26', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9956-6879', '', NULL, 
    '2025-07-25T15:53:28.577529+00:00', '2025-07-25T15:53:28.577529+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1435
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2398, 35, '416767-8', 'FRANCISCO EDUARDO SOUZA SANTOS', 'EDUARDO', 
    '077.965.623-73', '10.573-24', '', '1998-12-14', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9564-6733', NULL, 
    '2025-07-25T15:53:12.982436+00:00', '2025-07-25T15:53:12.982436+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1420
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2556, 193, '416768-6', 'FRANCISCO FLÁVIO CABRAL LEÃO', 'CABRAL', 
    '046.015.923-21', '10.574-24', '', '1990-02-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9475-6329', NULL, 
    '2025-07-25T15:55:54.369649+00:00', '2025-07-25T15:55:54.369649+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1578
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2402, 39, '416769-4', 'FRANCISCO LUCAS DE ASSIS NASCIMENTO ARAÚJO', 'ASSIS', 
    '063.882.783-37', '10.575-24', '', '1998-01-16', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8833-1914', NULL, 
    '2025-07-25T15:53:16.752101+00:00', '2025-07-25T15:53:16.752101+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1424
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2450, 87, '416770-8', 'FRANCISCO MARLON LIMA BARBOSA', 'BARBOSA', 
    '081.724.583-98', '10.576-24', '', '2001-11-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:04.882578+00:00', '2025-07-25T15:54:04.882578+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1472
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2374, 11, '416771-6', 'FRANCISCO SANTHIAGO HOLANDA FRANÇA SILVA', 'HOLANDA', 
    '015.489.193-22', '10.577-24', '', '1987-06-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8166-8159', NULL, 
    '2025-07-25T15:52:47.127033+00:00', '2025-07-25T15:52:47.127033+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1396
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2550, 187, '416772-4', 'GABRIEL SIMPLICIO DE ARAUJO SILVA', 'SIMPLÍCIO', 
    '041.075.913-95', '10.578-24', '', '1997-03-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9999-9999', NULL, 
    '2025-07-25T15:55:48.661459+00:00', '2025-07-25T15:55:48.661459+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1572
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2377, 14, '416773-2', 'GIOVANI AUGUSTO ARAÚJO COSTA', 'ARAÚJO', 
    '060.421.543-62', '10.579-24', '', '1996-08-26', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8881-6734', NULL, 
    '2025-07-25T15:52:50.143108+00:00', '2025-07-25T15:52:50.143108+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1399
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2484, 121, '416899-2', 'GUILHERME FERNANDES DE SENA SILVA', 'SENA', 
    '054.637.743-23', '10.580-24', '', '1993-09-27', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9443-3355', '', NULL, 
    '2025-07-25T15:54:40.934375+00:00', '2025-07-25T15:54:40.934375+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1506
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2405, 42, '417811-4', 'GUSTAVO AUGUSTO ARAÚJO COSTA', 'AUGUSTO', 
    '051.705.483-38', '10.581-24', '', '1994-09-05', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9542-7885', NULL, 
    '2025-07-25T15:53:20.481146+00:00', '2025-07-25T15:53:20.481146+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1427
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2479, 116, '416774-X', 'GUSTAVO NUNES DE MOURA', 'NUNES', 
    '043.025.653-14', '10.582-24', '', '1995-09-28', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9920-9902', NULL, 
    '2025-07-25T15:54:35.860706+00:00', '2025-07-25T15:54:35.860706+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1501
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2486, 123, '416775-9', 'HARLLEY RAMOS DE SÁ', 'HARLLEY', 
    '047.236.553-36', '10.583-24', '', '1995-07-27', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 967--0329', NULL, 
    '2025-07-25T15:54:43.130818+00:00', '2025-07-25T15:54:43.130818+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1508
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2495, 132, '416776-7', 'HITALO DA SILVA FREIRE', 'HITALO FREIRE', 
    '029.711.083-76', '10.584-24', '', '1990-03-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9476-4219', NULL, 
    '2025-07-25T15:54:52.745162+00:00', '2025-07-25T15:54:52.745162+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1517
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2433, 70, '416777-5', 'HYGO JOSÉ MACHADO DE SOUZA', 'HYGO', 
    '060.590.733-10', '10.585-24', '', '1997-08-07', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 3 2134-4054', '(86) 9 9532-3230', NULL, 
    '2025-07-25T15:53:47.763683+00:00', '2025-07-25T15:53:47.763683+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1455
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2370, 7, '416778-3', 'IAGGO RAMONN FERNANDO FEITOSA DA SILVA', 'IAGGO', 
    '066.340.703-69', '10.586-24', '', '2000-04-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 8868-1071', '(86) 9 8863-3177', NULL, 
    '2025-07-25T15:52:43.231321+00:00', '2025-07-25T15:52:43.231321+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1392
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2555, 192, '416779-1', 'IAGOR DE ÍCARO SOUSA MACHADO', 'ÍCARO', 
    '062.169.993-46', '10.587-24', '', '1994-03-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:55:53.394659+00:00', '2025-07-25T15:55:53.394659+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1577
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2497, 134, '416780-5', 'ISAIAS SILVA CANABRAVA', 'CANABRAVA', 
    '070.314.613-08', '10.588-24', '', '2000-01-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:54.666600+00:00', '2025-07-25T15:54:54.666600+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1519
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2514, 151, '416900-0', 'ISLAIRAN SANTOS DA SILVA', 'ISLAIRAN', 
    '052.017.313-92', '10.589-24', '', '1996-08-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9964-2308', NULL, 
    '2025-07-25T15:55:10.917779+00:00', '2025-07-25T15:55:10.917779+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1536
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2382, 19, '416781-3', 'ÍTALLO FERREIRA DE ARAUJO', 'ÍTALLO ARAUJO', 
    '053.687.893-51', '10.590-24', '', '1993-10-28', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9905-8881', NULL, 
    '2025-07-25T15:52:57.526748+00:00', '2025-07-25T15:52:57.526748+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1404
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2554, 191, '418122-X', 'JACIEL JOSE DA SILVA', 'JACIEL', 
    '076.692.984-13', '10.591-24', '', '1987-12-03', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(81) 9 9195-0672', '(81) 9 9195-0672', NULL, 
    '2025-07-25T15:55:52.447329+00:00', '2025-07-25T15:55:52.447329+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1576
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2553, 190, '416782-1', 'JÂNIO DA SILVA LIMA', 'JÂNIO', 
    '983.850.893-49', '10.592-24', '', '1988-04-30', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9844-4663', NULL, 
    '2025-07-25T15:55:51.496477+00:00', '2025-07-25T15:55:51.496477+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1575
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2525, 162, '416783-0', 'JEFERSON DE OLIVEIRA LIMA', 'LIMA', 
    '062.222.643-60', '10.593-24', '', '1994-10-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:55:23.150752+00:00', '2025-07-25T15:55:23.150752+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1547
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2483, 120, '416784-8', 'JEFFERSON OLIVEIRA DE SOUSA', 'JEFFERSON', 
    '066.203.353-14', '10.594-24', '', '1996-09-12', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9521-0094', NULL, 
    '2025-07-25T15:54:39.892816+00:00', '2025-07-25T15:54:39.892816+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1505
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2423, 60, '416785-6', 'JÉSSICA LAISA LEITE MENDES', 'LAISA', 
    '036.345.923-54', '10.595-24', '', '1990-02-19', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 8837-7473', '(86) 9 8837-4732', NULL, 
    '2025-07-25T15:53:37.977660+00:00', '2025-07-25T15:53:37.977660+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1445
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2373, 10, '416786-4', 'JHONAS PAULA DA SILVA', 'JHONAS', 
    '055.287.463-96', '10.596-24', '', '1998-03-05', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(21) 9 6893-9551', NULL, 
    '2025-07-25T15:52:46.149982+00:00', '2025-07-25T15:52:46.149982+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1395
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2468, 105, '416787-2', 'JOABE ALMEIDA SOUSA', 'JOABE', 
    '072.803.293-73', '10.597-24', '', '2000-10-09', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9432-1919', NULL, 
    '2025-07-25T15:54:25.234065+00:00', '2025-07-25T15:54:25.234065+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1490
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2438, 75, '416788-X', 'JOÃO MANOEL PINTO ANDRADE', 'MANOEL', 
    '052.305.163-80', '10.598-24', '', '1993-10-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9416-8519', NULL, 
    '2025-07-25T15:53:53.044130+00:00', '2025-07-25T15:53:53.044130+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1460
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2389, 26, '416789-9', 'JOÃO MARCOS DE ARAÚJO ESCÓRCIO', 'JOÃO MARCOS', 
    '049.364.133-56', '10.599-24', '', '1996-12-18', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9998-8881', NULL, 
    '2025-07-25T15:53:04.450802+00:00', '2025-07-25T15:53:04.450802+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1411
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2471, 108, '416790-2', 'JOÃO PEDRO SILVA ROCHA', 'PEDRO SILVA', 
    '086.257.773-09', '10.600-24', '', '2002-07-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9460-7948', NULL, 
    '2025-07-25T15:54:28.146933+00:00', '2025-07-25T15:54:28.146933+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1493
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2531, 168, '416791-X', 'JOÃO VICTOR MARANHÃO NASCIMENTO', 'MARANHÃO', 
    '130.198.394-24', '10.601-24', '', '1999-12-03', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(87) 9 9203-1864', NULL, 
    '2025-07-25T15:55:29.196651+00:00', '2025-07-25T15:55:29.196651+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1553
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2533, 170, '416792-9', 'JOAQUIM ISIDIO DE MOURA', 'ISIDIO MOURA', 
    '069.949.693-47', '10.602-24', '', '1998-04-28', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(89) 9 4159-9250', '(89) 9 9415-9250', NULL, 
    '2025-07-25T15:55:31.212858+00:00', '2025-07-25T15:55:31.212858+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1555
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2504, 141, '416793-7', 'JOIANA NARA FELIX GRAMOSA DOS SANTOS', 'GRAMOSA', 
    '073.324.733-48', '10.603-24', '', '1999-08-19', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9454-4011', '(86) 9 9454-0114', NULL, 
    '2025-07-25T15:55:01.569245+00:00', '2025-07-25T15:55:01.569245+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1526
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2443, 80, '417812-2', 'JONATHAN MURIEL DA COSTA', 'MURIEL', 
    '391.262.208-65', '10.604-24', '', '1989-04-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9823-9859', NULL, 
    '2025-07-25T15:53:58.261932+00:00', '2025-07-25T15:53:58.261932+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1465
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2508, 145, '416794-5', 'JORGE LUIZ DE MELO ARAUJO', 'JORGE', 
    '029.186.963-74', '10.605-24', '', '1988-08-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(11) 9 9589-9244', NULL, 
    '2025-07-25T15:55:05.329409+00:00', '2025-07-25T15:55:05.329409+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1530
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2506, 143, '416795-3', 'JORGE LUIZ SOARES AZEVEDO', 'SOARES', 
    '003.034.593-60', '10.606-24', '', '1993-08-24', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9587-3953', NULL, 
    '2025-07-25T15:55:03.440834+00:00', '2025-07-25T15:55:03.440834+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1528
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2552, 189, '416796-1', 'JOSÉ EUCLIDES DE SOUSA NETO', 'EUCLIDES', 
    '019.644.953-77', '10.607-24', '', '1991-08-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9810-7448', NULL, 
    '2025-07-25T15:55:50.535603+00:00', '2025-07-25T15:55:50.535603+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1574
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2392, 29, '416797-0', 'JOSÉ EVANILSON DE SOUSA BARROS', 'EVANILSON', 
    '045.344.143-23', '10.608-24', '', '1998-08-04', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(89) 9 9436-6414', '(89) 9 9436-4140', NULL, 
    '2025-07-25T15:53:07.312384+00:00', '2025-07-25T15:53:07.312384+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1414
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2448, 85, '418118-2', 'JOSÉ FELIPE ALVES SAMPAIO', 'SAMPAIO', 
    '056.812.573-80', '10.609-24', '', '1994-04-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9200-0201', NULL, 
    '2025-07-25T15:54:02.983062+00:00', '2025-07-25T15:54:02.983062+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1470
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2444, 81, '416798-8', 'JOSÉ GUILHERME ALMENDRA NEVES', 'NEVES', 
    '054.418.063-11', '10.610-24', '', '1995-04-20', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9451-5522', NULL, 
    '2025-07-25T15:53:59.226232+00:00', '2025-07-25T15:53:59.226232+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1466
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2502, 139, '416800-3', 'JOSE WANDERSON DE MENESES MORAIS', 'WANDERSON', 
    '060.993.253-52', '10.612-24', '', '1998-08-27', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8839-6077', NULL, 
    '2025-07-25T15:54:59.539483+00:00', '2025-07-25T15:54:59.539483+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1524
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2543, 180, '416804-6', 'JOSUÉ AMORIM DANTAS', 'AMORIM', 
    '074.821.383-07', '10.616-24', '', '2003-02-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9919-5359', NULL, 
    '2025-07-25T15:55:41.937473+00:00', '2025-07-25T15:55:41.937473+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1565
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2482, 119, '416805-4', 'JOSUE DOS SANTOS OLIVEIRA', 'JOSUÉ', 
    '044.276.573-89', '10.617-24', '', '1992-06-18', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:38.913026+00:00', '2025-07-25T15:54:38.913026+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1504
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2421, 58, '416806-2', 'JOSUÉ MARCELO SOARES LEAL', 'MARCELO LEAL', 
    '035.900.813-50', '10.618-24', '', '1989-06-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9918-4763', NULL, 
    '2025-07-25T15:53:36.117235+00:00', '2025-07-25T15:53:36.117235+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1443
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2451, 88, '416807-X', 'JULIO RODRIGUES JULIO', 'JULIO', 
    '049.051.203-81', '10.619-24', '', '1999-03-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9995-4713', NULL, 
    '2025-07-25T15:54:05.831787+00:00', '2025-07-25T15:54:05.831787+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1473
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2426, 63, '416808-9', 'KAROLINA RIBEIRO DE OLIVEIRA', 'KAROLINA', 
    '042.430.573-97', '10.620-24', '', '1990-02-23', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:53:40.746009+00:00', '2025-07-25T15:53:40.746009+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1448
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2512, 149, '416809-7', 'KAWAN MACHADO DE ARAÚJO', 'KAWAN', 
    '075.685.223-42', '10.621-24', '', '2003-04-05', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9998-6374', NULL, 
    '2025-07-25T15:55:09.060683+00:00', '2025-07-25T15:55:09.060683+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1534
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2467, 104, '416810-X', 'KAYO HESDRAS PINHEIRO SILVA', 'HESDRAS', 
    '057.472.993-36', '10.622-24', '', '1996-03-01', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9839-9388', NULL, 
    '2025-07-25T15:54:24.228894+00:00', '2025-07-25T15:54:24.228894+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1489
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2407, 44, '416811-9', 'KAYRON EDUARDO PEREIRA DA SILVA FONTINELES', 'FONTINELES', 
    '067.630.673-05', '10.623-24', '', '1999-03-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9470-9511', '(86) 9 8125-3595', NULL, 
    '2025-07-25T15:53:22.622854+00:00', '2025-07-25T15:53:22.622854+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1429
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2517, 154, '416812-7', 'LAERTH DE JESUS ABADE', 'LAERTH', 
    '043.026.293-04', '10.624-24', '', '1990-09-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9466-5401', NULL, 
    '2025-07-25T15:55:13.678717+00:00', '2025-07-25T15:55:13.678717+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1539
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2542, 179, '417813-X', 'LEANDRO SILVA BITTENCOURT', 'BITTENCOURT', 
    '054.885.893-41', '10.625-24', '', '1994-08-11', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9597-8698', NULL, 
    '2025-07-25T15:55:40.967455+00:00', '2025-07-25T15:55:40.967455+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1564
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2488, 125, '416813-5', 'LEONARDO RODRIGUES GOMES', 'LEONARDO GOMES', 
    '070.682.753-89', '10.626-24', '', '1998-08-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9402-2830', NULL, 
    '2025-07-25T15:54:45.009966+00:00', '2025-07-25T15:54:45.010948+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1510
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2464, 101, '416814-3', 'LEVI BARROS NERY', 'LEVI', 
    '608.961.853-54', '10.627-24', '', '1995-10-30', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(85) 9 9722-7799', NULL, 
    '2025-07-25T15:54:19.868813+00:00', '2025-07-25T15:54:19.868813+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1486
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2461, 98, '416815-1', 'LHANA LETTÍCIA ARAUJO DA SILVA PEREIRA', 'LHANA LETTÍCIA', 
    '026.289.243-07', '10.628-24', '', '1997-02-19', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9452-0117', NULL, 
    '2025-07-25T15:54:16.152336+00:00', '2025-07-25T15:54:16.152336+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1483
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2365, 1, '332432-0', 'Lucas BORGES Leal', 'BORGES', 
    '048.346.993-90', '10.452-18', '', '1991-07-31', 'M', 'PRACAS', 
    'SD', '2018-12-26', '2018-12-26', 'AT', 
    '', '(86) 9 9978-8900', '', NULL, 
    '2025-07-25T15:52:38.266410+00:00', '2025-07-25T15:52:38.266410+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1387
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2496, 133, '416816-0', 'LUCAS DE OLIVEIRA SOUSA', 'SOUSA', 
    '606.631.273-19', '10.629-24', '', '1996-01-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(89) 9 9404-6643', '(89) 9 9404-6634', NULL, 
    '2025-07-25T15:54:53.703386+00:00', '2025-07-25T15:54:53.703386+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1518
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2401, 38, '416817-8', 'LUCAS GOMES DE CARVALHO', 'GOMES', 
    '065.959.083-28', '10.630-24', '', '1996-05-04', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9803-1081', '', NULL, 
    '2025-07-25T15:53:15.816886+00:00', '2025-07-25T15:53:15.816886+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1423
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2481, 118, '416818-6', 'LUCAS GUIMARÃES DE ALMEIDA ROCHA', 'ROCHA', 
    '032.594.493-88', '10.631-24', '', '1999-12-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:37.881309+00:00', '2025-07-25T15:54:37.881309+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1503
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2454, 91, '418114-0', 'LUIS CELSO DA COSTA FERREIRA JUNIOR', 'LUÍS CELSO', 
    '073.926.433-80', '10.632-24', '', '2000-04-27', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9867-3879', '(86) 9 9541-2425', NULL, 
    '2025-07-25T15:54:09.019451+00:00', '2025-07-25T15:54:09.019451+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1476
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2378, 15, '416819-4', 'LUIS GUSTHAVO NORONHA SOUSA', 'LUIS NORONHA', 
    '081.550.653-83', '10.633-24', '', '2000-10-16', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9561-5999', NULL, 
    '2025-07-25T15:52:52.518892+00:00', '2025-07-25T15:52:52.518892+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1400
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2541, 178, '416901-8', 'MAICON HENRIQUE MARQUES BATISTA', 'BATISTA ', 
    '039.500.903-04', '10.634-24', '', '1993-03-03', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9827-9007', NULL, 
    '2025-07-25T15:55:39.758875+00:00', '2025-07-25T15:55:39.758875+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1563
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2419, 56, '416820-8', 'MAIRON ARAUJO DE OLIVEIRA PINHEIRO', 'PINHEIRO', 
    '038.994.393-25', '10.635-24', '', '2003-05-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9418-9286', NULL, 
    '2025-07-25T15:53:34.268644+00:00', '2025-07-25T15:53:34.268644+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1441
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2501, 138, '416821-6', 'MARÇANIO ALVES MARQUES', 'MARÇANIO', 
    '067.797.563-50', '10.636-24', '', '1997-12-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8122-7736', NULL, 
    '2025-07-25T15:54:58.535286+00:00', '2025-07-25T15:54:58.535286+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1523
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2455, 92, '416822-4', 'MARCÍLIO MADSON DOS SANTOS SOUSA', 'MADSON', 
    '620.060.293-04', '10.637-24', '', '1991-04-26', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9818-1173', NULL, 
    '2025-07-25T15:54:09.978902+00:00', '2025-07-25T15:54:09.978902+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1477
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2475, 112, '416824-X', 'MARCIO MENDES DANTAS', 'MÁRCIO', 
    '019.779.963-96', '10.638-24', '', '1989-03-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8824-8576', NULL, 
    '2025-07-25T15:54:31.995317+00:00', '2025-07-25T15:54:31.995317+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1497
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2399, 36, '416823-2', 'MARCOS ANDRÉ DE SOUSA LIRA', 'ANDRÉ', 
    '061.425.343-88', '10.639-24', '', '1999-11-12', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8841-8787', NULL, 
    '2025-07-25T15:53:13.949253+00:00', '2025-07-25T15:53:13.949253+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1421
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2544, 181, '416825-9', 'MARCOS ANTONIO CARVALHO DE OLIVEIRA', 'CARVALHO', 
    '066.696.513-76', '10.640-24', '', '1995-06-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9594-5518', NULL, 
    '2025-07-25T15:55:42.913134+00:00', '2025-07-25T15:55:42.913134+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1566
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2509, 146, '416827-5', 'MARCOS GOMES DO NASCIMENTO FILHO', 'NASCIMENTO', 
    '113.764.074-00', '10.642-24', '', '2000-11-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(87) 9 9826-1889', NULL, 
    '2025-07-25T15:55:06.270458+00:00', '2025-07-25T15:55:06.270458+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1531
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2445, 82, '416829-1', 'MARCOS VINICIUS COSTA DE ALENCAR OLIVEIRA', 'ALENCAR', 
    '059.423.693-21', '10.644-24', '', '1999-03-18', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9825-3651', NULL, 
    '2025-07-25T15:54:00.186824+00:00', '2025-07-25T15:54:00.186824+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1467
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2489, 126, '416828-3', 'MARCOS VINICIUS PACHECO SOUSA', 'PACHECO', 
    '051.774.333-74', '10.643-24', '', '1999-05-16', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9969-4219', NULL, 
    '2025-07-25T15:54:46.080622+00:00', '2025-07-25T15:54:46.080622+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1511
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2429, 66, '416830-5', 'MARCUS VINICIUS DA SILVA SOUSA', 'MARCUS SILVA', 
    '050.887.543-96', '10.645-24', '', '1998-05-12', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9852-2953', NULL, 
    '2025-07-25T15:53:43.684869+00:00', '2025-07-25T15:53:43.684869+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1451
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2521, 158, '416831-3', 'MARCUS VINICIUS SILVA MOURA', 'MARCUS VINÍCIUS', 
    '054.984.023-09', '10.646-24', '', '1992-07-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9420-1001', NULL, 
    '2025-07-25T15:55:17.403723+00:00', '2025-07-25T15:55:17.403723+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1543
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2406, 43, '416832-1', 'MARIA CAMILA LEAL DE MOURA', 'CAMILA LEAL', 
    '048.293.763-76', '10.647-24', '', '1997-08-19', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8852-5325', NULL, 
    '2025-07-25T15:53:21.500543+00:00', '2025-07-25T15:53:21.500543+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1428
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2395, 32, '416833-0', 'MARIA CLARA ALENCAR CARVALHO BORGES', 'CLARA ALENCAR', 
    '072.794.273-59', '10.648-24', '', '1998-03-10', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:53:10.180958+00:00', '2025-07-25T15:53:10.180958+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1417
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2388, 25, '416834-8', 'MARIA FRANCISCA DA SILVA PACHECO', 'FRANCISCA', 
    '060.381.593-63', '10.649-24', '', '1997-05-02', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9439-1411', NULL, 
    '2025-07-25T15:53:03.476207+00:00', '2025-07-25T15:53:03.476207+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1410
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2397, 34, '416835-6', 'MARIA GABRIELA RODRIGUES RAMOS', 'GABRIELA', 
    '109.825.624-70', '10.650-24', '', '1996-04-01', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(87) 9 9120-3447', NULL, 
    '2025-07-25T15:53:12.037385+00:00', '2025-07-25T15:53:12.037385+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1419
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2414, 51, '416836-4', 'MARINA RODRIGUES MOREIRA', 'MARINA', 
    '040.114.053-96', '10.651-24', '', '1992-12-21', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(89) 9 9981-3402', '(89) 9 9981-3402', NULL, 
    '2025-07-25T15:53:29.513845+00:00', '2025-07-25T15:53:29.513845+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1436
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2493, 130, '416837-2', 'MARIO PEREIRA DA SILVA', 'MÁRIO', 
    '081.025.003-95', '10.652-24', '', '2001-02-16', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8117-2739', NULL, 
    '2025-07-25T15:54:50.103514+00:00', '2025-07-25T15:54:50.103514+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1515
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2478, 115, '416839-9', 'MARLON ARAUJO DE OLIVEIRA PINHEIRO', 'MARLON PINHEIRO', 
    '038.994.403-31', '10.653-24', '', '2003-05-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9449-1627', NULL, 
    '2025-07-25T15:54:34.936219+00:00', '2025-07-25T15:54:34.936219+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1500
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2480, 117, '416838-X', 'MÁRNIER BEZERRA ROCHA', 'MÁRNIER', 
    '962.439.373-72', '10.654-24', '', '1994-10-31', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9838-9251', NULL, 
    '2025-07-25T15:54:36.830825+00:00', '2025-07-25T15:54:36.830825+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1502
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2418, 55, '416840-2', 'MATEUS BORBA NEVES', 'BORBA', 
    '074.532.763-06', '10.655-24', '', '2000-05-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:53:33.263995+00:00', '2025-07-25T15:53:33.263995+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1440
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2452, 89, '416841-X', 'MATEUS CAVALCANTE DE MOURA', 'CAVALCANTE', 
    '067.971.383-29', '10.656-24', '', '1998-03-04', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 3 3422-6102', NULL, 
    '2025-07-25T15:54:06.839296+00:00', '2025-07-25T15:54:06.839296+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1474
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2536, 173, '416843-7', 'MATHEUS CARDOSO COUTINHO', 'CARDOSO', 
    '061.991.403-38', '10.658-24', '', '1997-02-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8825-2560', NULL, 
    '2025-07-25T15:55:34.146692+00:00', '2025-07-25T15:55:34.146692+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1558
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2400, 37, '416844-5', 'MATHEUS CHRISTIAN SILVA MARINHO DE CASTRO', 'MARINHO', 
    '076.188.153-05', '10.659-24', '', '2000-09-04', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9937-9806', NULL, 
    '2025-07-25T15:53:14.882153+00:00', '2025-07-25T15:53:14.882153+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1422
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2470, 107, '416845-3', 'MATHEUS ROMÉRIO SOUZA DOS SANTOS', 'MATHEUS', 
    '069.818.853-52', '10.660-24', '', '1998-07-06', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9445-4483', NULL, 
    '2025-07-25T15:54:27.215877+00:00', '2025-07-25T15:54:27.215877+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1492
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2474, 111, '416846-1', 'MAURO GUSTAVO GONZALEZ SAMPAIO FILHO', 'GONZALEZ', 
    '069.659.053-01', '10.661-24', '', '1997-11-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 3 3402-7361', NULL, 
    '2025-07-25T15:54:31.066438+00:00', '2025-07-25T15:54:31.066438+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1496
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2476, 113, '416847-0', 'MIGUEL ALVORES LIMA NETO', 'ALVORES', 
    '078.183.183-05', '10.662-24', '', '2000-02-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9450-7265', NULL, 
    '2025-07-25T15:54:32.967709+00:00', '2025-07-25T15:54:32.967709+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1498
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2435, 72, '416848-8', 'MIGUEL CAMPOS DA ROCHA', 'CAMPOS', 
    '066.770.943-67', '10.663-24', '', '1996-08-01', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9511-7614', NULL, 
    '2025-07-25T15:53:50.008387+00:00', '2025-07-25T15:53:50.008387+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1457
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2485, 122, '416849-6', 'MIGUEL DOS SANTOS ARAÚJO', 'MIGUEL', 
    '067.882.733-83', '10.664-24', '', '1993-09-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9460-8526', '(86) 9 9960-8526', NULL, 
    '2025-07-25T15:54:42.033724+00:00', '2025-07-25T15:54:42.033724+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1507
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2547, 184, '416850-0', 'MOISÉS JOSÉ DE ANDRADE FILHO', 'ANDRADE FILHO', 
    '018.803.473-00', '10.665-24', '', '1990-07-10', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9461-7969', NULL, 
    '2025-07-25T15:55:45.812712+00:00', '2025-07-25T15:55:45.812712+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1569
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2384, 21, '416852-6', 'MURILO DE SOUZA LINHARES', 'MURILO', 
    '073.983.403-70', '10.667-24', '', '2000-08-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9539-1519', NULL, 
    '2025-07-25T15:52:59.663178+00:00', '2025-07-25T15:52:59.663178+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1406
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2440, 77, '416853-4', 'NAOMI LUZ MARTINS E SILVA', 'NAOMI LUZ', 
    '315.011.188-97', '10.668-24', '', '1997-04-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 8127-7470', NULL, 
    '2025-07-25T15:53:55.293786+00:00', '2025-07-25T15:53:55.293786+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1462
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2515, 152, '416854-2', 'NILO LEONARDO DOS SANTOS CRUZ', 'NILO', 
    '039.566.623-69', '10.669-24', '', '1992-05-24', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9428-1921', NULL, 
    '2025-07-25T15:55:11.835289+00:00', '2025-07-25T15:55:11.835289+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1537
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2498, 135, '416855-X', 'OZIAS GONÇALVES LIMA JÚNIOR', 'OZIAS', 
    '050.551.433-80', '10.670-24', '', '1992-11-11', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9902-8020', NULL, 
    '2025-07-25T15:54:55.601577+00:00', '2025-07-25T15:54:55.601577+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1520
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2371, 8, '416856-9', 'PATRICK HYAN COSTA AYRES', 'PATRICK', 
    '606.658.673-44', '10.671-24', '', '1999-02-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(99) 9 8823-1172', NULL, 
    '2025-07-25T15:52:44.207418+00:00', '2025-07-25T15:52:44.207418+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1393
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2466, 103, '416857-7', 'PATRICK SANTOS BRAGA', 'BRAGA', 
    '063.612.133-07', '10.672-24', '', '1998-05-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9915-0149', NULL, 
    '2025-07-25T15:54:23.133268+00:00', '2025-07-25T15:54:23.133268+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1488
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2551, 188, '416858-5', 'PATRIK ANDERSON MENEZES RIOS', 'ANDERSON', 
    '058.829.873-50', '10.673-24', '', '1994-09-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9854-8921', NULL, 
    '2025-07-25T15:55:49.583330+00:00', '2025-07-25T15:55:49.583330+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1573
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2463, 100, '416859-3', 'PAULO HENRIQUE DA CUNHA COUTINHO', 'COUTINHO', 
    '019.920.563-90', '10.674-24', '', '1988-09-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9818-2800', NULL, 
    '2025-07-25T15:54:18.317107+00:00', '2025-07-25T15:54:18.317107+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1485
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2457, 94, '416860-7', 'PEDRO BARBOSA DE CARVALHO NETO', 'NETO', 
    '044.533.353-77', '10.675-24', '', '1998-04-03', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9418-8663', '', NULL, 
    '2025-07-25T15:54:12.062834+00:00', '2025-07-25T15:54:12.062834+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1479
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2366, 2, '408199-4', 'PEDRO GERALDO FILHO', 'GERALDO', 
    '032.767.983-28', '10.504-24', '', '1989-12-04', 'M', 'PRACAS', 
    'SD', '2024-03-04', '2024-03-04', 'AT', 
    '', '', '(86) 9 8180-7913', NULL, 
    '2025-07-25T15:52:39.331954+00:00', '2025-07-25T15:52:39.331954+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1388
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2546, 183, '416861-5', 'PEDRO HENRIQUE BORGES DA SILVA', 'HENRIQUE', 
    '024.137.163-51', '10.676-24', '', '1988-04-21', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9979-3794', NULL, 
    '2025-07-25T15:55:44.853633+00:00', '2025-07-25T15:55:44.853633+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1568
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2385, 22, '416863-1', 'PEDRO LUCAS MILANÊS DE SOUSA', 'MILANÊS', 
    '071.930.073-86', '10.677-24', '', '1997-04-16', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8900-7915', NULL, 
    '2025-07-25T15:53:00.634637+00:00', '2025-07-25T15:53:00.634637+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1407
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2368, 5, '416862-3', 'PEDRO RENAN DE SOUZA LIMA DA SILVEIRA', 'PEDRO RENAN', 
    '060.756.273-08', '10.678-24', '', '1995-12-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9505-3337', NULL, 
    '2025-07-25T15:52:41.314391+00:00', '2025-07-25T15:52:41.314391+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1390
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2396, 33, '416864-0', 'PEDRO RODRIGUES DE OLIVEIRA', 'OLIVEIRA', 
    '065.479.533-94', '10.679-24', '', '1998-04-02', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9955-3516', NULL, 
    '2025-07-25T15:53:11.113094+00:00', '2025-07-25T15:53:11.113094+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1418
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2520, 157, '418120-4', 'RAFAEL LOPES HOZANO', 'HOZANO', 
    '072.156.964-13', '10.680-24', '', '1987-05-08', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(84) 9 9920-2243', NULL, 
    '2025-07-25T15:55:16.448028+00:00', '2025-07-25T15:55:16.448028+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1542
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2523, 160, '416865-8', 'RAFAEL NONATO DE SOUSA', 'RAFAEL', 
    '081.408.213-06', '10.681-24', '', '2001-12-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9901-5681', NULL, 
    '2025-07-25T15:55:19.420591+00:00', '2025-07-25T15:55:19.420591+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1545
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2537, 174, '416866-6', 'RAFAEL SOARES DA CRUZ', 'CRUZ', 
    '019.996.313-40', '10.682-24', '', '1989-07-19', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9949-9084', '(86) 9 9949-0846', NULL, 
    '2025-07-25T15:55:35.167353+00:00', '2025-07-25T15:55:35.167353+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1559
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2425, 62, '416867-4', 'RAIZA LORENA RODRIGUES DE AGUIAR CARVALHO', 'RAÍZA', 
    '010.264.503-57', '10.683-24', '', '1990-10-17', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8872-1742', NULL, 
    '2025-07-25T15:53:39.831819+00:00', '2025-07-25T15:53:39.831819+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1447
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2524, 161, '416868-2', 'RANIERY SANTANA DA SILVA', 'SANTANA', 
    '043.340.413-29', '10.684-24', '', '1992-05-18', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(89) 9 9302-2561', '(89) 9 9930-2561', NULL, 
    '2025-07-25T15:55:20.748674+00:00', '2025-07-25T15:55:20.748674+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1546
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2534, 171, '416869-X', 'REGINALDO LOPES MORAES JUNIOR', 'REGINALDO', 
    '032.323.003-24', '10.685-24', '', '1988-06-06', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9473-3276', NULL, 
    '2025-07-25T15:55:32.201409+00:00', '2025-07-25T15:55:32.201409+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1556
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2415, 52, '416870-4', 'REHIMUNDY WRIKI SANTOS DA SILVA', 'WRIKI', 
    '061.687.073-60', '10.686-24', '', '1999-12-15', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9418-2202', NULL, 
    '2025-07-25T15:53:30.451161+00:00', '2025-07-25T15:53:30.451161+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1437
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2437, 74, '416871-2', 'REINALDO MELO DA SILVA', 'MELO', 
    '060.553.193-57', '10.687-24', '', '1996-04-26', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9901-4545', NULL, 
    '2025-07-25T15:53:52.014740+00:00', '2025-07-25T15:53:52.014740+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1459
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2513, 150, '416872-X', 'RENATO ALVES SOUSA', 'ALVES SOUSA', 
    '062.437.223-50', '10.688-24', '', '1994-01-02', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9416-6559', '(86) 9 9416-5659', NULL, 
    '2025-07-25T15:55:09.985888+00:00', '2025-07-25T15:55:09.985888+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1535
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2518, 155, '416873-9', 'RICARDO ALEXANDER VIANA SILVA', 'ALEXANDER', 
    '054.929.083-40', '10.689-24', '', '1997-05-22', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9565-3555', '(86) 9 3219-1741', NULL, 
    '2025-07-25T15:55:14.597874+00:00', '2025-07-25T15:55:14.597874+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1540
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2549, 186, '416874-7', 'RIVALDINO DE LIMA OTAVIO', 'OTÁVIO', 
    '031.585.633-55', '10.690-24', '', '1988-03-29', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9432-7200', NULL, 
    '2025-07-25T15:55:47.718596+00:00', '2025-07-25T15:55:47.718596+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1571
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2367, 4, '416875-5', 'RODRIGO FERREIRA DE CARVALHO', 'RODRIGO', 
    '045.491.503-94', '10.691-24', '', '1991-07-24', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9942-3411', NULL, 
    '2025-07-25T15:52:40.319065+00:00', '2025-07-25T15:52:40.319065+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1389
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2403, 40, '416876-3', 'ROGÉRIO AGUIAR SOARES', 'AGUIAR', 
    '061.617.763-16', '10.692-24', '', '1996-05-23', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9407-0560', NULL, 
    '2025-07-25T15:53:17.671928+00:00', '2025-07-25T15:53:17.672931+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1425
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2390, 27, '416877-1', 'ROMÁRIO VIEIRA RODRIGUES', 'ROMÁRIO', 
    '029.337.203-96', '10.693-24', '', '1993-10-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9426-2052', NULL, 
    '2025-07-25T15:53:05.413119+00:00', '2025-07-25T15:53:05.413119+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1412
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2379, 16, '416878-0', 'RONY DOS SANTOS ARAUJO', 'RONY', 
    '055.951.873-01', '10.694-24', '', '1993-08-10', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9463-8829', NULL, 
    '2025-07-25T15:52:54.201599+00:00', '2025-07-25T15:52:54.201599+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1401
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2487, 124, '416879-8', 'SAMUEL MARQUES FERREIRA', 'FERREIRA', 
    '070.267.433-84', '10.695-24', '', '1998-08-14', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 8127-4487', '(86) 9 8127-4487', NULL, 
    '2025-07-25T15:54:44.068848+00:00', '2025-07-25T15:54:44.068848+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1509
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2428, 65, '416880-1', 'SAMUEL MOURA DUARTE', 'SAMUEL', 
    '065.058.693-01', '10.696-24', '', '1994-12-31', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8843-3100', NULL, 
    '2025-07-25T15:53:42.717515+00:00', '2025-07-25T15:53:42.717515+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1450
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2408, 45, '416881-0', 'SANDINO AVELAR HILL COSTA', 'SANDINO HILL', 
    '070.352.913-77', '10.697-24', '', '1996-09-12', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8892-7830', NULL, 
    '2025-07-25T15:53:23.629262+00:00', '2025-07-25T15:53:23.629262+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1430
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2447, 84, '416882-8', 'SERGIO MATOS FRANCO', 'SERGIO', 
    '042.847.743-79', '10.698-24', '', '1993-01-25', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:54:02.044508+00:00', '2025-07-25T15:54:02.044508+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1469
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2490, 127, '416883-6', 'TAMIRES SANTOS BARBOSA DOURADO', 'DOURADO', 
    '059.888.093-32', '10.699-24', '', '1994-08-11', 'F', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9593-3463', NULL, 
    '2025-07-25T15:54:47.050884+00:00', '2025-07-25T15:54:47.050884+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1512
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2505, 142, '416884-4', 'THELIO MENDES DE CARVALHO', 'THELIO', 
    '068.254.883-92', '10.700-24', '', '1997-02-02', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8105-6139', NULL, 
    '2025-07-25T15:55:02.495135+00:00', '2025-07-25T15:55:02.495135+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1527
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2540, 177, '416885-2', 'THERCIO ANTONIO DOS SANTOS ROCHA', 'THERCIO', 
    '042.998.553-37', '10.701-24', '', '1992-07-28', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9515-3297', NULL, 
    '2025-07-25T15:55:38.802866+00:00', '2025-07-25T15:55:38.802866+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1562
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2494, 131, '416886-X', 'THYAGO LUIZ DOS SANTOS SOUSA', 'THYAGO', 
    '034.351.913-50', '10.702-24', '', '1990-09-17', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(89) 9 9423-4684', NULL, 
    '2025-07-25T15:54:51.385740+00:00', '2025-07-25T15:54:51.385740+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1516
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2439, 76, '416887-9', 'VALMÁRIO SOUSA ANDRADE', 'VALMÁRIO', 
    '051.400.673-07', '10.703-24', '', '1993-05-13', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9950-9633', NULL, 
    '2025-07-25T15:53:54.246831+00:00', '2025-07-25T15:53:54.246831+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1461
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2372, 9, '416889-5', 'WALLESON CLÁUDIO DOS SANTOS ROCHA', 'WALLESON', 
    '058.895.123-40', '10.705-24', '', '1995-01-15', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8119-7990', NULL, 
    '2025-07-25T15:52:45.180146+00:00', '2025-07-25T15:52:45.180146+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1394
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2412, 49, '416890-9', 'WESLEY KELTON PEREIRA DA SILVA', 'KELTON', 
    '042.908.553-26', '10.706-24', '', '1991-05-20', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '(86) 9 9818-1808', '(86) 9 9818-0874', NULL, 
    '2025-07-25T15:53:27.597268+00:00', '2025-07-25T15:53:27.597268+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1434
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2465, 102, '416891-7', 'WESLEY RESENDE DOS SANTOS', 'WESLEY', 
    '048.817.043-54', '10.707-24', '', '1994-06-07', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9579-6983', NULL, 
    '2025-07-25T15:54:22.032345+00:00', '2025-07-25T15:54:22.032345+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1487
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2557, 194, '418089-5', 'WILK RICARDO RESENDE FEITOSA', 'WILK', 
    '030.432.783-21', '10.710-24', '', '1987-10-29', 'M', 'PRACAS', 
    'SD', '2024-08-13', '2024-08-13', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:55:55.434743+00:00', '2025-07-25T15:55:55.434743+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1579
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2530, 167, '416892-5', 'WILLIAN SANTOS DE CARVALHO', 'WILLIAN', 
    '055.874.193-20', '10.708-24', '', '1993-05-02', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 8806-7192', NULL, 
    '2025-07-25T15:55:28.234039+00:00', '2025-07-25T15:55:28.234039+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1552
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2442, 79, '416893-3', 'YTALLO ENNOS DE JESUS SOUSA', 'ENNOS', 
    '042.243.993-26', '10.709-24', '', '1991-10-26', 'M', 'PRACAS', 
    'SD', '2024-07-22', '2024-07-22', 'AT', 
    '', '', '(86) 9 9933-7605', NULL, 
    '2025-07-25T15:53:57.250618+00:00', '2025-07-25T15:53:57.250618+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1464
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2243, 37, '207480-0', 'ALEXANDRE Torres Brito', 'ALEXANDRE ', 
    '002.628.603-33', '10.332-08', '', '1985-11-07', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'alexandre_piaui@hotmail.com', '(89) 3 5224-4472', '(89) 9 9907-3525', NULL, 
    '2025-07-25T15:50:38.474070+00:00', '2025-07-25T15:50:38.474070+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1265
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2261, 55, '207644-6', 'Antonio CARLOS da SILVA', 'CARLOS SILVA ', 
    '884.016.343-34', '10.334-08', '', '1981-05-27', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-12-25', 'AT', 
    'carlosmthl@hotmail.com', '(86) 9 9452-2989', '(86) 9 9496-9650', NULL, 
    '2025-07-25T15:50:56.091703+00:00', '2025-07-25T15:50:56.091703+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1283
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2220, 14, '015331-1', 'ANTÔNIO CARLOS de Sousa Santos', 'ANTÔNIO CARLOS ', 
    '439.499.833-68', 'GIP 10.9335', '', '1971-08-10', 'M', 'PRACAS', 
    'ST', '1991-06-01', '2022-07-18', 'AT', 
    '', '(86) 3 2204-4766', '(86) 9 8874-6055', NULL, 
    '2025-07-25T15:50:15.035391+00:00', '2025-07-25T15:50:15.035391+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1242
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2257, 51, '207495-8', 'Antonio MARCELINO Ribeiro Junior', 'MARCELINO ', 
    '016.747.613-09', '10.335-08', '', '1985-04-27', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-07-18', 'AT', 
    'marcelinobmpi@gmail.com', '(86) 3 3234-4590', '(86) 9 9455-4621', NULL, 
    '2025-07-25T15:50:52.164145+00:00', '2025-07-25T15:50:52.164145+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1279
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2216, 10, '108753-3', 'AVA DANYELLA Macedo Silva', 'AVA DANYELLA ', 
    '801.600.263-34', 'GIP 10.12666', '', '1978-06-03', 'F', 'PRACAS', 
    'ST', '2000-12-01', '2020-12-25', 'AT', 
    'avadan3678@gmail.com', '(86) 3 2161-1263', '(86) 9 9851-4871', NULL, 
    '2025-07-25T15:50:11.190344+00:00', '2025-07-25T15:50:11.190344+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1238
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2262, 56, '207487-7', 'BRENO Bandeira de Alencar', 'BRENO ', 
    '919.007.513.72', '10.328-08', '', '1981-08-02', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-12-25', 'AT', 
    'breno_ce_ara@hotmail.com', '(89) 3 4223-3307', '(86) 9 9906-5209', NULL, 
    '2025-07-25T15:50:57.076405+00:00', '2025-07-25T15:50:57.076405+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1284
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2213, 7, '082779-7', 'Carlos Alberto da COSTA', 'COSTA ', 
    '462.624.073-91', 'GIP 10.10740', '', '1972-05-15', 'M', 'PRACAS', 
    'ST', '1993-09-01', '2019-12-25', 'AT', 
    'carloscosta579@gmail.com', '(86) 9 9485-9870', '(86) 9 9485-9870', NULL, 
    '2025-07-25T15:50:07.914446+00:00', '2025-07-25T15:50:07.914446+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1235
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2214, 8, '015039-8', 'Carlos Alberto da SILVA', 'SILVA ', 
    '343.049.163-00', 'GIP 10.8930', '', '1966-11-02', 'M', 'PRACAS', 
    'ST', '1990-07-02', '2019-12-25', 'AT', 
    '', '(86) 9 8826-3809', '(86) 9 8826-3809', NULL, 
    '2025-07-25T15:50:09.120279+00:00', '2025-07-25T15:50:09.120279+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1236
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2251, 45, '207503-2', 'Carlos Alberto Pereira OLEGÁRIO', 'OLEGÁRIO ', 
    '748.603.053-53', '10.326-08', '', '1977-02-09', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'bmolegario@hotmail.com', '(86) 3 2356-6660', '(86) 9 8886-7853', NULL, 
    '2025-07-25T15:50:46.320836+00:00', '2025-07-25T15:50:46.320836+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1273
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2229, 23, '180433-2', 'CÉSAR Augusto Madeira Monteiro Junior', 'CÉSAR ', 
    '747.211.003-53', '10.301-06', '', '1977-04-10', 'M', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'juniortriballes@hotmail.com', '(99) 3 2123-3108', '(86) 9 9911-0101', NULL, 
    '2025-07-25T15:50:24.840476+00:00', '2025-07-25T15:50:24.840476+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1251
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2208, 2, '085394-1', 'CLÁUDIO Rodrigues MATOS', 'CLÁUDIO MATOS ', 
    '515.341.503-15', 'GIP 10.11928', '', '1970-09-19', 'M', 'PRACAS', 
    'ST', '1994-03-01', '2018-07-18', 'AT', 
    '', '(86) 3 2143-3788', '(86) 9 9516-2002', NULL, 
    '2025-07-25T15:50:02.757715+00:00', '2025-07-25T15:50:02.757715+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1230
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2241, 35, '207482-6', 'Dâmaro STÊNIO Melo Viana', 'STÊNIO ', 
    '024.868.473-67', '10.319-08', '', '1988-05-21', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'steniobm48@hotmail.com', '(86) 3 2762-2134', '(86) 9 9968-1927', NULL, 
    '2025-07-25T15:50:36.480311+00:00', '2025-07-25T15:50:36.480311+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1263
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2242, 36, '207502-4', 'DANIEL Nepomuceno de Sousa ABREU', 'DANIEL ABREU ', 
    '839.154.433-87', '10.322-08', '', '1978-06-15', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'bmdanielfire@hotmail.com', '(86) 3 2273-3592', '(86) 9 9413-3716', NULL, 
    '2025-07-25T15:50:37.500528+00:00', '2025-07-25T15:50:37.500528+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1264
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2209, 3, '084885-9', 'Derivaldo Alves dos SANTOS', 'D SANTOS ', 
    '481.956.183-91', 'GIP 10.11460', '', '1973-02-22', 'M', 'PRACAS', 
    'ST', '1994-02-01', '2018-12-25', 'AT', 
    'cbdsantosbombeiro@hotmail.com', '(86) 9 4446-6366', '(86) 9 9444-6366', NULL, 
    '2025-07-25T15:50:03.715593+00:00', '2025-07-25T15:50:03.716628+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1231
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2211, 5, '079853-3', 'DEUSIVAN Sousa Silva', 'DEUSIVAN ', 
    '490.358.513-15', 'GIP 10.10498', '', '1970-01-22', 'M', 'PRACAS', 
    'ST', '1993-12-20', '2019-07-18', 'AT', 
    '', '(86) 9 9816-7924', '(86) 9 9446-5432', NULL, 
    '2025-07-25T15:50:05.675534+00:00', '2025-07-25T15:50:05.675534+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1233
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2227, 21, '083458-X', 'Edmilson de AZEVEDO do Nascimento', 'AZEVEDO ', 
    '287.354.473-20', 'GIP 10.8590', '', '1966-06-25', 'M', 'PRACAS', 
    'ST', '1993-12-01', '2022-07-18', 'AT', 
    '', '(86) 9 4390-0613', '(86) 9 9439-0613', NULL, 
    '2025-07-25T15:50:22.837817+00:00', '2025-07-25T15:50:22.837817+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1249
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2232, 26, '180436-7', 'ELDEAN Silva Lima', 'ELDEAN ', 
    '918.133.953-49', '10.299-06', '', '1981-07-30', 'M', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'eldeanlima@hotmail.com', '(99) 3 5211-1181', '(86) 9 9910-1963', NULL, 
    '2025-07-25T15:50:27.783175+00:00', '2025-07-25T15:50:27.783175+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1254
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2240, 34, '207499-X', 'ÉRICO Vinícius Mendes da Silva', 'ÉRICO ', 
    '007.552.173-30', '10.325-08', '', '1985-02-28', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'ericovinnis@yahoo.com.br', '(86) 9 8804-6563', '(86) 9 9943-9676', NULL, 
    '2025-07-25T15:50:35.506644+00:00', '2025-07-25T15:50:35.506644+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1262
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2230, 24, '180437-5', 'FÁBIO dos Santos Costa', 'FÁBIO ', 
    '001.775.873-42', '10.295-06', '', '1983-05-26', 'M', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'sdbmflavio@hotmail.com', '(89) 9 8809-8961', '(89) 9 9433-0146', NULL, 
    '2025-07-25T15:50:25.824636+00:00', '2025-07-25T15:50:25.824636+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1252
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2256, 50, '207481-8', 'FABRÍCIO Bacelar Salles', 'FABRÍCIO ', 
    '914.363.703-53', '10.315-08', '', '1980-10-27', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-07-18', 'AT', 
    'fabriciobepe@hotmail.com', '(86) 3 2124-4226', '(86) 9 9908-0322', NULL, 
    '2025-07-25T15:50:51.150082+00:00', '2025-07-25T15:50:51.150082+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1278
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2212, 6, '014638-2', 'Francisco CARLOS Carvalho Pereira', 'F CARLOS', 
    '352.834.403-20', 'GIP 10.8547', '', '1969-07-30', 'M', 'PRACAS', 
    'ST', '1989-09-01', '2019-12-25', 'AT', 
    '', '(86) 3 2143-3788', '(86) 9 9948-5021', NULL, 
    '2025-07-25T15:50:06.721268+00:00', '2025-07-25T15:50:06.721268+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1234
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2255, 49, '207508-3', 'Francisco das Chagas Carvalho dos SANTOS FILHO', 'SANTOS FILHO ', 
    '769.190.993-49', ' 10.305-08', '', '1978-11-20', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-07-18', 'AT', 
    'franciscoiza@hotmail.com', '(86) 3 3228-8067', '(86) 9 9474-8624', NULL, 
    '2025-07-25T15:50:50.176098+00:00', '2025-07-25T15:50:50.176098+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1277
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2260, 54, '207479-6', 'Francisco das Chagas da ROCHA Praça', 'ROCHA ', 
    '017.326.453-02', '10.313-08', '', '1987-02-13', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-12-25', 'AT', 
    '', '(89) 3 4621-1195', '(89) 9 9409-9098', NULL, 
    '2025-07-25T15:50:55.113845+00:00', '2025-07-25T15:50:55.113845+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1282
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2223, 17, '110409-8', 'Francisco das Chagas LIMA', 'F LIMA ', 
    '443.873.181-04', 'GIP 10.8047', '', '1967-11-14', 'M', 'PRACAS', 
    'ST', '1987-03-01', '2022-07-18', 'AT', 
    'amilazid@hotmail.com', '(86) 9 4255-5000', '(86) 9 9414-0061', NULL, 
    '2025-07-25T15:50:18.854315+00:00', '2025-07-25T15:50:18.854315+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1245
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2215, 9, '015015-X', 'FRANCISCO MARQUES de Oliveira', 'FRANCISCO MARQUES ', 
    '115.945.808-12', 'GIP 10.8898', '', '1969-03-05', 'M', 'PRACAS', 
    'ST', '1990-07-01', '2020-07-18', 'AT', 
    'marques1237@hotmail.com', '(86) 9 8380-0523', '(86) 9 9423-2119', NULL, 
    '2025-07-25T15:50:10.220527+00:00', '2025-07-25T15:50:10.220527+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1237
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2239, 33, '207483-4', 'Francisco SOUSA JÚNIOR', 'SOUSA JÚNIOR ', 
    '958.253.123-15', '10.327-08', '', '1982-09-25', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'sousajunior-historia@hotmail.com', '(89) 3 4223-3307', '(89) 9 9972-8297', NULL, 
    '2025-07-25T15:50:34.525997+00:00', '2025-07-25T15:50:34.525997+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1261
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2217, 11, '108745-2', 'GEAN Carlos Barbosa Furtado', 'GEAN ', 
    '788.344.903-63', 'GIP 10.12660', '', '1976-05-04', 'M', 'PRACAS', 
    'ST', '2000-12-01', '2021-07-18', 'AT', 
    'sdbmgean@yahoo.com.br', '(86) 3 2118-8107', '(86) 9 9412-1501', NULL, 
    '2025-07-25T15:50:12.153182+00:00', '2025-07-25T15:50:12.153182+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1239
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2233, 27, '180448-X', 'GENILTON Wellington de Sousa', 'GENILTON ', 
    '652.256.003.87', '10.300-06', '', '1979-08-01', 'M', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'gntsousa@hotmail.com', '(86) 3 2200-0827', '(86) 9 9525-3136', NULL, 
    '2025-07-25T15:50:28.736861+00:00', '2025-07-25T15:50:28.736861+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1255
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2221, 15, '015145-9', 'GILMAR Feitosa de Sousa', 'GILMAR ', 
    '446.328.863-00', 'GIP 10.9043', '', '1969-10-26', 'M', 'PRACAS', 
    'ST', '1990-08-01', '2022-07-18', 'AT', 
    '', '(86) 3 2143-3788', '(86) 9 9425-7153', NULL, 
    '2025-07-25T15:50:16.002487+00:00', '2025-07-25T15:50:16.002487+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1243
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2252, 46, '207473-7', 'GYVAGO Lira Moreira', 'GYVAGO ', 
    '852.319.083-04', '10.341-08', '', '1980-04-14', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'gyvago@bol.com.br', '(86) 3 2181-1690', '(86) 9 8882-1690', NULL, 
    '2025-07-25T15:50:47.289513+00:00', '2025-07-25T15:50:47.289513+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1274
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2207, 1, '014148-8', 'HÉLIO Antônio de Sousa Lima', 'HÉLIO ', 
    '349.298.783-49', '105.150.023-0', '', '1967-12-23', 'M', 'PRACAS', 
    'ST', '1987-09-04', '2014-12-25', 'AT', 
    '', '(86) 9 9453-4188', '(86) 9 9416-0852', NULL, 
    '2025-07-25T15:50:01.791050+00:00', '2025-07-25T15:50:01.791050+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1229
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2247, 41, '207645-4', 'Helio Marcio FONTENELE Filho', 'FONTENELE ', 
    '600.445.493-18', '10.331-08', '', '1988-09-13', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'firemanfontenele@hotmail.com', '(86) 3 3228-8067', '(86) 9 9451-8481', NULL, 
    '2025-07-25T15:50:42.420965+00:00', '2025-07-25T15:50:42.420965+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1269
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2245, 39, '207472-9', 'ITALO Vieira Lima', 'ITALO ', 
    '010.891.163-22', '10.330-08', '', '1985-01-18', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'ythalolima@gmail.com', '(86) 9 9994-9401', '(86) 9 9994-9101', NULL, 
    '2025-07-25T15:50:40.426306+00:00', '2025-07-25T15:50:40.426306+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1267
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2226, 20, '108758-4', 'JERRYSON Martins dos Santos', 'JERRYSON ', 
    '735.165.703-34', 'GIP 10.12671', '', '1975-12-26', 'M', 'PRACAS', 
    'ST', '2000-12-01', '2022-07-18', 'AT', 
    'jerrysonbidfilhos@gmail.com', '(86) 3 2225-5799', '(86) 9 9534-6527', NULL, 
    '2025-07-25T15:50:21.839216+00:00', '2025-07-25T15:50:21.839216+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1248
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2218, 12, '015336-2', 'João Batista NERY de Sousa', 'NERY ', 
    '421.235.693-72', 'GIP 10.9340', '', '1969-06-24', 'M', 'PRACAS', 
    'ST', '1991-06-01', '2021-12-25', 'AT', 
    'bmnery@hotmail.com', '(86) 9 8816-7409', '(86) 9 9913-1676', NULL, 
    '2025-07-25T15:50:13.107019+00:00', '2025-07-25T15:50:13.107019+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1240
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2237, 31, '015030-4', 'João de SOUSA Monteiro NETO', 'NETO ', 
    '428.593.603-87', 'GIP 10.8918', '', '1968-12-09', 'M', 'PRACAS', 
    'ST', '1990-07-01', '2022-07-18', 'AT', 
    '', '(86) 8 8249-9112', '(86) 9 3213-4208', NULL, 
    '2025-07-25T15:50:32.592371+00:00', '2025-07-25T15:50:32.592371+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1259
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2259, 53, '160541-X', 'José Francisco de ARAÚJO Silva ', 'ARAÚJO ', 
    '009.268.563-32', '10.304-08', '', '1983-09-30', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-12-25', 'AT', 
    'jfaraujo6@hotmail.com', '(89) 3 4441-1411', '(89) 9 8801-3532', NULL, 
    '2025-07-25T15:50:54.109047+00:00', '2025-07-25T15:50:54.109047+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1281
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2222, 16, '082860-2', 'José FRAZÃO de Moura Filho', 'J FRAZÃO ', 
    '481.550.473-34', 'GIP 10.11001', '', '1970-04-25', 'M', 'PRACAS', 
    'ST', '1993-09-01', '2022-07-18', 'AT', 
    '', '(86) 9 8656-6265', '(70) 9 9494-5770', NULL, 
    '2025-07-25T15:50:17.600171+00:00', '2025-07-25T15:50:17.600171+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1244
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2231, 25, '180449-9', 'KÁCIA Lígia Silveira Linhares', 'KÁCIA ', 
    '026.109.703-23', '10.291-06', '', '1986-04-16', 'F', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'kcialinhares@gmail.com', '(86) 9 5350-0351', '(86) 9 9535-0351', NULL, 
    '2025-07-25T15:50:26.818400+00:00', '2025-07-25T15:50:26.818400+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1253
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2236, 30, '180442-1', 'LUANA Coutinho de Oliveira Caldas', 'LUANA ', 
    '003.598.813-43', '10.302-06', '', '1984-05-05', 'F', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'luanacoutinho.oliveira@gmail.com', '(86) 9 9921-7917', '(86) 9 8812-2065', NULL, 
    '2025-07-25T15:50:31.640026+00:00', '2025-07-25T15:50:31.640026+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1258
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2219, 13, '085862-5', 'Luíz Alves da Vera CRUZ', 'V CRUZ ', 
    '578.441.273-68', 'GIP 10.11713', '', '1973-08-02', 'M', 'PRACAS', 
    'ST', '1994-03-01', '2022-07-18', 'AT', 
    '', '(86) 9 4954-4619', '(86) 9 9495-4619', NULL, 
    '2025-07-25T15:50:14.059287+00:00', '2025-07-25T15:50:14.059287+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1241
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2234, 28, '180444-8', 'LUIZ Ramos RIBEIRO', 'LUIZ RIBEIRO ', 
    '001.750.283-70', '10.292-06', '', '1983-03-09', 'M', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'luizramosribeiro@hotmail.com', '(89) 9 9213-3331', '(89) 9 9921-3331', NULL, 
    '2025-07-25T15:50:29.698950+00:00', '2025-07-25T15:50:29.698950+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1256
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2235, 29, '108749-5', 'Márcia SANDRA Rego de Sousa', 'SANDRA ', 
    '805.612.923-53', 'GIP 10.12679', '', '1976-03-21', 'F', 'PRACAS', 
    'ST', '2000-12-01', '2022-07-18', 'AT', 
    '', '', '', NULL, 
    '2025-07-25T15:50:30.672824+00:00', '2025-07-25T15:50:30.672824+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1257
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2253, 47, '207642-0', 'MARCIO Rogério Bernardes da Rocha', 'MARCIO ', 
    '002.552.673-12', '10.337-08', '', '1982-07-10', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'marciorocha6@hotmail.com', '(89) 3 5211-1474', '(89) 9 9443-8010', NULL, 
    '2025-07-25T15:50:48.251887+00:00', '2025-07-25T15:50:48.251887+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1275
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2224, 18, '014568-8', 'Marcos Antonio Lima Gonçalves MINEU', 'MINEU ', 
    '353.187.593-00', 'GIP 10.8484', '', '1968-05-09', 'M', 'PRACAS', 
    'ST', '1989-08-01', '2022-07-18', 'AT', 
    '', '(86) 9 4967-7682', '', NULL, 
    '2025-07-25T15:50:19.872309+00:00', '2025-07-25T15:50:19.872309+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1246
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2248, 42, '207646-2', 'Marcus VINICIUS Bernardes da Rocha', 'VINICIUS ', 
    '848.112.343-91', '10.348-08', '', '1980-03-01', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'marcus.25@bol.com.br', '(89) 3 5211-1474', '(89) 9 9978-4691', NULL, 
    '2025-07-25T15:50:43.392989+00:00', '2025-07-25T15:50:43.392989+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1270
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2246, 40, '207494-0', 'NATHANAEL Araújo da Silva', 'NATHANAEL ', 
    '029.329.123-30', '10.308-08', '', '1989-02-02', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'naelterrier@gmail.com', '(86) 9 4846-6786', '', NULL, 
    '2025-07-25T15:50:41.409268+00:00', '2025-07-25T15:50:41.409268+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1268
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2258, 52, '207488-5', 'NELSON Pires Sadalla Júnior', 'NELSON ', 
    '998.177.133-34', '10.347-08', '', '1988-07-30', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-07-18', 'AT', 
    '', '(86) 9 9501-4251', '(86) 9 9963-3058', NULL, 
    '2025-07-25T15:50:53.126569+00:00', '2025-07-25T15:50:53.126569+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1280
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2210, 4, '015983-2', 'OSMAR Avelino de Sousa', 'OSMAR ', 
    '387.200.603-78', 'GIP 10.9891', '', '1968-09-04', 'M', 'PRACAS', 
    'ST', '1991-11-01', '2019-07-18', 'AT', 
    'osmarbm2009@hotmail.com', '(86) 8 8414-4385', '(86) 9 8841-4385', NULL, 
    '2025-07-25T15:50:04.701123+00:00', '2025-07-25T15:50:04.701123+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1232
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2238, 32, '207484-2', 'Paulo BEZERRA de Sousa', 'BEZERRA ', 
    '021.736.843-37', '10.316-08', '', '1988-02-18', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'paulobsousa@outlook.com', '(89) 3 4291-1159', '(89) 9 8802-0048', NULL, 
    '2025-07-25T15:50:33.557941+00:00', '2025-07-25T15:50:33.557941+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1260
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2244, 38, '207491-5', 'Pedro Augusto RAFAEL Bezerra Neto', 'RAFAEL ', 
    '031.991.624-36', '10.306-08', '', '1980-05-11', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'rafael.pedroaugusto@yahoo.com.br', '(86) 9 9330-0944', '(86) 9 8861-4614', NULL, 
    '2025-07-25T15:50:39.451027+00:00', '2025-07-25T15:50:39.451027+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1266
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2225, 19, '015031-2', 'Raimundo NONATO Barbosa dos Santos', 'NONATO ', 
    '362.077.483-87', 'GIP 10.8919', '', '1968-02-14', 'M', 'PRACAS', 
    'ST', '1990-07-01', '2022-07-18', 'AT', 
    'nonatopanteracb@hotmail.com', '(86) 3 2252-2715', '(86) 9 8834-9197', NULL, 
    '2025-07-25T15:50:20.852015+00:00', '2025-07-25T15:50:20.852015+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1247
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2250, 44, '207470-2', 'Renato Oliveira SANTIAGO', 'SANTIAGO ', 
    '650.867.243-68', '10.338-08', '', '1982-07-22', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'presizao@yahoo.com.br', '(86) 3 2204-4424', '(86) 9 9404-3465', NULL, 
    '2025-07-25T15:50:45.367754+00:00', '2025-07-25T15:50:45.367754+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1272
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2254, 48, '207478-8', 'RONIERE Alves de Azevedo', 'RONIERE ', 
    '787.970.713-15', '10.320-08', '', '1977-02-07', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2024-07-18', 'AT', 
    'roniereazevedo@gmail.com', '(86) 3 2272-2207', '(86) 9 9998-0047', NULL, 
    '2025-07-25T15:50:49.224143+00:00', '2025-07-25T15:50:49.224143+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1276
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2249, 43, '207492-3', 'WILMAYKOM Sousa Fontenele', 'WILMAYKOM ', 
    '024.176.553-65', '10.344-08', '', '1988-06-22', 'M', 'PRACAS', 
    'ST', '2008-03-27', '2023-12-25', 'AT', 
    'wilmaykom@hotmail.com', '(86) 3 3224-4725', '(86) 9 9405-1573', NULL, 
    '2025-07-25T15:50:44.364326+00:00', '2025-07-25T15:50:44.364326+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1271
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2228, 22, '180447-2', 'YONESKO do Brasil Marques Carvalho', 'YONESKO ', 
    '938.094.843-34', '10.293-06', '', '1982-08-19', 'M', 'PRACAS', 
    'ST', '2006-09-01', '2022-07-18', 'AT', 
    'yonesko@hotmail.com', '(86) 8 8698-8494', '(86) 9 8869-8494', NULL, 
    '2025-07-25T15:50:23.847450+00:00', '2025-07-25T15:50:23.847450+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1250
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2080, 7, '088912-1', 'Airton SANSÃO Sousa', 'SANSÃO ', 
    '432.560.073-68', 'GIP 10.12117', '', '1971-11-04', 'M', 'COMB', 
    'TC', '1995-02-01', '2022-07-18', 'AT', 
    'airtonsansao@hotmail.com', '(86) 3 2227-7869', '(86) 9 8816-9669', NULL, 
    '2025-07-25T15:47:54.335618+00:00', '2025-07-25T15:47:54.335618+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1102
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2086, 13, '084753-4', 'ANA CLÉIA  Diniz dos Santos', 'ANA CLÉIA ', 
    '704.171.213-34', 'GIP 10.11391', '', '1974-12-29', 'F', 'COMB', 
    'TC', '1994-02-01', '2022-07-18', 'AT', 
    'cleia2006@hotmail.com', '(89) 9 9988-7776', '(89) 9 9988-7776', NULL, 
    '2025-07-25T15:48:00.230114+00:00', '2025-07-25T15:48:00.230114+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1108
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2085, 12, '127134-2', 'EDILSON Soares Lima', 'EDILSON ', 
    '931.043.833-91', 'GIP 10.12805', '', '1980-06-28', 'M', 'COMB', 
    'TC', '2002-04-02', '2022-07-18', 'AT', 
    'edilsonmil@yahoo.com.br', '(89) 3 5212-2807', '(86) 9 9950-9883', NULL, 
    '2025-07-25T15:47:59.162148+00:00', '2025-07-25T15:47:59.162148+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1107
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2084, 11, '084721-6', 'ELISABETH da Costa Aguiar Tavares', 'ELISABETH ', 
    '689.336.733-34', 'GIP 10.11342', '', '1975-10-07', 'F', 'COMB', 
    'TC', '1994-02-01', '2022-07-18', 'AT', 
    'elisabet-aguiar@hotmai.com', '(86) 3 2142-2426', '(86) 9 8842-3246', NULL, 
    '2025-07-25T15:47:58.211921+00:00', '2025-07-25T15:47:58.211921+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1106
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2074, 1, '080764-8', 'FREDMAN Wellington Lopes', 'FREDMAN ', 
    '428.570.403-00', 'GIP 10.10592', '', '1972-11-05', 'M', 'COMB', 
    'TC', '1993-02-01', '2014-07-18', 'AT', 
    'fredmanw@gmail.com', '(86) 3 2370-0434', '(86) 9 9478-1328', NULL, 
    '2025-07-25T15:47:48.036562+00:00', '2025-07-25T15:47:48.036562+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1096
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2076, 3, '080730-3', 'Glécio MENDES da Rocha', 'MENDES ', 
    '517.310.883-53', 'GIP 10.10581', '', '1974-03-31', 'M', 'COMB', 
    'TC', '1993-02-01', '2016-12-23', 'AT', 
    'protemacequipamentos@gmail.com', '(86) 3 2119-9844', '(86) 9 9948-8449', NULL, 
    '2025-07-25T15:47:49.970785+00:00', '2025-07-25T15:47:49.970785+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1098
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2079, 6, '088914-8', 'Jean SÉRGIO Gomes Melo', 'SÉRGIO ', 
    '680.378.303-06', 'GIP 10.12119', '', '1975-07-10', 'M', 'COMB', 
    'TC', '1995-02-01', '2022-07-18', 'AT', 
    'sergio_bombeiro@hotmail.com', '(86) 3 2226-6085', '(96) 9 9928-9494', NULL, 
    '2025-07-25T15:47:53.330815+00:00', '2025-07-25T15:47:53.330815+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1101
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2081, 8, '088915-6', 'Jullierme CHRISTIAN Lima Vale', 'CHRISTIAN ', 
    '382.118.232-68', 'GIP 10.12120', '', '1972-09-07', 'M', 'COMB', 
    'TC', '1995-02-01', '2022-07-18', 'AT', 
    'christianfirelogan666@gmail.com', '(86) 9 9316-6383', '(86) 9 8816-5464', NULL, 
    '2025-07-25T15:47:55.339180+00:00', '2025-07-25T15:47:55.339180+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1103
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2078, 5, '084169-2', 'Kelson Fernando CASTELO Branco da Silva', 'CASTELO BRANCO ', 
    '566.215.403-10', 'GIP 10.11131', '', '1975-01-19', 'M', 'COMB', 
    'TC', '1994-01-01', '2022-07-18', 'AT', 
    'kelsonfernandocbs@gmail.com', '(86) 9 9925-0080', '(86) 9 9925-0080', NULL, 
    '2025-07-25T15:47:52.364515+00:00', '2025-07-25T15:47:52.364515+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1100
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2077, 4, '080726-5', 'MARCELLO Rubem Santos Bastos', 'MARCELLO ', 
    '395.128.353-04', 'GIP 10.10588', '', '1971-01-07', 'M', 'COMB', 
    'TC', '1993-02-01', '2019-12-23', 'AT', 
    'mrsb193@hotmail.com', '(86) 9 9595-2992', '(86) 9 8812-4370', NULL, 
    '2025-07-25T15:47:50.959405+00:00', '2025-07-25T15:47:50.959405+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1099
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2083, 10, '092342-7', 'NAJRA Julite Moreira Nunes', 'NAJRA ', 
    '829.927.033-20', 'GIP 10.12142', '', '1979-10-10', 'F', 'COMB', 
    'TC', '1998-12-05', '2022-07-18', 'AT', 
    'najrajulitemn@hotmail.com', '(86) 9 9452-7106', '(86) 9 9452-7106', NULL, 
    '2025-07-25T15:47:57.262882+00:00', '2025-07-25T15:47:57.262882+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1105
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2082, 9, '082804-1', 'RIVELINO de Moura Silva', 'RIVELINO ', 
    '687.758.813-49', 'GIP 10.10726', '', '1971-07-06', 'M', 'COMB', 
    'TC', '1993-09-01', '2022-07-18', 'AT', 
    'rivelino193@hotmail.com', '(86) 3 3232-2865', '(86) 9 9949-8504', NULL, 
    '2025-07-25T15:47:56.305518+00:00', '2025-07-25T15:47:56.305518+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1104
);
INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    2075, 2, '080765-6', 'SÁRVIO Pereira de Sousa', 'SÁRVIO ', 
    '478.987.713-20', 'GIP 10.10594', '', '1973-01-19', 'M', 'COMB', 
    'TC', '1993-02-01', '2016-07-18', 'AT', 
    'sarviopereira@hotmail.com', '(86) 3 2131-1338', '(86) 9 8825-5573', NULL, 
    '2025-07-25T15:47:49.002028+00:00', '2025-07-25T15:47:49.002028+00:00', NULL, 
    false, false, 
    false, NULL, false, 
    false, false, 
    false, false, 
    false, false, NULL, 
    false, NULL, false, 
    true, NULL, NULL, 
    NULL, 1097
);

-- Resetar sequência
SELECT setval('militares_militar_id_seq', (SELECT MAX(id) FROM militares_militar));


-- Reabilitar triggers
SET session_replication_role = DEFAULT;

-- Verificar dados inseridos
SELECT 'Usuários' as tabela, COUNT(*) as total FROM auth_user;
SELECT 'Militares' as tabela, COUNT(*) as total FROM militares_militar;
SELECT 'Comissões' as tabela, COUNT(*) as total FROM militares_comissaopromocao;
SELECT 'Quadros' as tabela, COUNT(*) as total FROM militares_quadroacesso;