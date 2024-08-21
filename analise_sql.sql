-- 1. Quantos chamados foram abertos no dia 01/04/2023?
SELECT COUNT(*) as total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE DATE(data_inicio) = '2023-04-01';

-- Resultado:
-- 1756

-- 2. Qual o tipo de chamado que teve mais chamados abertos no dia 01/04/2023?
SELECT tipo, COUNT(*) as total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE DATE(data_inicio) = '2023-04-01'
GROUP BY tipo
ORDER BY total_chamados DESC
LIMIT 1;

-- Resultado:
-- Estacionamento irregular 366

-- 3. Quais os nomes dos 3 bairros que mais tiveram chamados abertos nesse dia?
SELECT b.nome as nome_bairro, COUNT(*) as total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
GROUP BY b.nome
ORDER BY total_chamados DESC
LIMIT 3;

-- Resultado:
-- Campo Grande     113
-- Tijuca           89
-- Barra da Tijuca  59

-- 4. Qual o nome da subprefeitura com mais chamados abertos nesse dia?
SELECT b.subprefeitura as nome_subprefeitura, COUNT(*) as total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
GROUP BY b.subprefeitura
ORDER BY total_chamados DESC
LIMIT 1;

-- Resultado:
-- Zona Norte 510

-- 5. Existe algum chamado aberto nesse dia que não foi associado a um bairro ou subprefeitura na tabela de bairros? Se sim, por que isso acontece?
SELECT COUNT(*) as chamados_sem_bairro_ou_subprefeitura
FROM `datario.adm_central_atendimento_1746.chamado` c
LEFT JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
  AND (b.nome IS NULL OR b.subprefeitura IS NULL);

-- Resultado:
-- 73
-- Explicação:
-- Os chamados sem associação a bairro ou subprefeitura parecem estar relacionados principalmente a serviços móveis, como ônibus. Isso faz sentido, pois esses serviços não estão necessariamente vinculados a um local específico.

-- 6. Quantos chamados com o subtipo "Perturbação do sossego" foram abertos desde 01/01/2022 até 31/12/2023 (incluindo extremidades)?
SELECT COUNT(*) as total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE subtipo = 'Perturbação do sossego'
  AND data_inicio BETWEEN '2022-01-01' AND '2023-12-31 23:59:59';

-- Resultado:
-- 42830

-- 7. Selecione os chamados com esse subtipo que foram abertos durante os eventos contidos na tabela de eventos (Reveillon, Carnaval e Rock in Rio).
SELECT c.*,  e.evento as evento
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON c.data_inicio BETWEEN e.data_inicial AND e.data_final
WHERE c.subtipo = 'Perturbação do sossego'
  AND e.evento IN ('Reveillon', 'Carnaval', 'Rock in Rio');

-- Resultado (primeiras linhas):
-- 1 18328998 13 2023-02-18T16:55:41 2023-02-24T10:23:40 128 4 204339 600 70 GM-RIO - Guarda Municipal do Rio de Janeiro GM-RIO - Guarda Municipal do Rio de Janeiro False Serviço 1615 Perturbação do sossego 5071 Perturbação do sossego Sem possibilidade de atendimento -43.3033175 -23.0145087 2023-02-25T16:55:00 null null null D F No prazo Encerrado Não atendido null 0 2023-02-01 Carnaval
-- 2 18331087 11 2023-02-19T20:40:28 2023-02-28T09:28:19 14 1 65987 30 70 GM-RIO - Guarda Municipal do Rio de Janeiro GM-RIO - Guarda Municipal do Rio de Janeiro False Serviço 1615 Perturbação do sossego 5071 Perturbação do sossego Sem possibilidade de atendimento -43.1893825 -22.9214794 2023-02-26T20:40:00 null null null D F Fora do prazo Encerrado Não atendido null 0 2023-02-01 Carnaval
-- 3 18331162 13 2023-02-19T21:52:47 2023-02-28T09:41:38 24 2 65896 1186 70 GM-RIO - Guarda Municipal do Rio de Janeiro GM-RIO - Guarda Municipal do Rio de Janeiro False Serviço 1615 Perturbação do sossego 5071 Perturbação do sossego Sem possibilidade de atendimento -43.1813203 -22.9694629 2023-02-26T21:52:00 null null null D F Fora do prazo Encerrado Não atendido null 1 2023-02-01 Carnaval
-- 4 17684278 11 2022-09-10T21:56:21 2022-09-19T08:27:10 24 2 65896 29 70 GM-RIO - Guarda Municipal do Rio de Janeiro GM-RIO - Guarda Municipal do Rio de Janeiro False Serviço 1615 Perturbação do sossego 5071 Perturbação do sossego Sem possibilidade de atendimento -43.187090900000008 -22.9753431 2022-09-17T21:56:00 null null null D F Fora do prazo Encerrado Não atendido null 0 2022-09-01 Rock in Rio
-- 5 17677832 11 2022-09-08T17:33:19 2022-09-16T10:39:58 144 5 43620 35 70 GM-RIO - Guarda Municipal do Rio de Janeiro GM-RIO - Guarda Municipal do Rio de Janeiro False Serviço 1615 Perturbação do sossego 5071 Perturbação do sossego Sem possibilidade de atendimento -43.5544735 -22.9028089 2022-09-15T17:33:00 null null null D F Fora do prazo Encerrado Não atendido null 2 2022-09-01 Rock in Rio

-- 8. Quantos chamados desse subtipo foram abertos em cada evento?
SELECT e.evento, COUNT(*) as total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON c.data_inicio BETWEEN e.data_inicial AND e.data_final
WHERE c.subtipo = 'Perturbação do sossego'
  AND e.evento IN ('Reveillon', 'Carnaval', 'Rock in Rio')
GROUP BY e.evento;

-- Resultado:
-- Carnaval     197
-- Rock in Rio  518
-- Reveillon    81

-- 9. Qual evento teve a maior média diária de chamados abertos desse subtipo?
SELECT e.evento, 
       COUNT(*) / DATE_DIFF(e.data_final, e.data_inicial, DAY) as media_diaria_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON c.data_inicio BETWEEN e.data_inicial AND e.data_final
WHERE c.subtipo = 'Perturbação do sossego'
  AND e.evento IN ('Reveillon', 'Carnaval', 'Rock in Rio')
GROUP BY e.evento, e.data_inicial, e.data_final
ORDER BY media_diaria_chamados DESC
LIMIT 1;

-- Resultado:
-- Rock in Rio  106.0

-- 10. Compare as médias diárias de chamados abertos desse subtipo durante os eventos específicos (Reveillon, Carnaval e Rock in Rio) e a média diária de chamados abertos desse subtipo considerando todo o período de 01/01/2022 até 31/12/2023.
WITH eventos_media AS (
  SELECT e.evento, 
         COUNT(*) / DATE_DIFF(e.data_final, e.data_inicial, DAY) as media_diaria_chamados
  FROM `datario.adm_central_atendimento_1746.chamado` c
  JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
    ON c.data_inicio BETWEEN e.data_inicial AND e.data_final
  WHERE c.subtipo = 'Perturbação do sossego'
    AND e.evento IN ('Reveillon', 'Carnaval', 'Rock in Rio')
  GROUP BY e.evento, e.data_inicial, e.data_final
),
periodo_total_media AS (
  SELECT COUNT(*) / 730 as media_diaria_chamados  -- 730 dias entre 01/01/2022 e 31/12/2023
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE subtipo = 'Perturbação do sossego'
    AND data_inicio BETWEEN '2022-01-01' AND '2023-12-31 23:59:59'
)
SELECT 'Período Total' as periodo, media_diaria_chamados
FROM periodo_total_media
UNION ALL
SELECT evento, media_diaria_chamados
FROM eventos_media
ORDER BY media_diaria_chamados DESC;

-- Resultado:
-- Rock in Rio 106.0
-- Rock in Rio 102.0
-- Carnaval 65.666666666666671
-- Período Total 58.671232876712331
-- Reveillon 40.5


-- Análise dos resultados:
-- Os eventos específicos (Rock in Rio, Carnaval e Reveillon) têm médias diárias mais altas que a média do período total, o que faz sentido, pois são momentos de maior agitação na cidade.
-- O Rock in Rio se destaca com as maiores médias, possivelmente devido à sua localização concentrada e à natureza do evento (shows de rock tendem a ser mais barulhentos).
-- A divisao para o Rock in Rio com médias parecidas pode indicar que não houve variações entre os dias do evento.
-- O Carnaval, sendo um evento mais disperso pela cidade e de maior duração, tem uma média menor que o Rock in Rio, mas ainda significativamente acima da média total.
-- O Reveillon, apesar de ser um evento importante, tem a menor média entre os eventos específicos, possivelmente por ser mais curto e/ou mais tolerado pela população.