# GeoFleet Microservices

Arquitetura de microsserviços otimizada para consultas geoespaciais em tempo real, projetada para escalar em direção a 1M+ requisições de leitura por segundo.

## Sobre o projeto

O **GeoFleet Microservices** é um projeto de estudo e portfólio inspirado em sistemas de localização em tempo real, como o recurso de encontrar motoristas próximos em aplicativos de mobilidade.

A ideia principal é construir, de forma incremental, uma arquitetura capaz de receber atualizações frequentes de localização de motoristas e responder rapidamente consultas por motoristas disponíveis dentro de um determinado raio.

O foco do projeto não é criar um clone da Uber, mas estudar e demonstrar decisões arquiteturais usadas em sistemas de alta escala, principalmente no caminho de leitura.

## Problema que o projeto busca resolver

Imagine um cenário com milhares ou milhões de motoristas enviando sua localização a cada poucos segundos.

Ao mesmo tempo, muitos usuários consultam o sistema procurando motoristas próximos.

Uma solução simples poderia consultar diretamente o banco de dados relacional a cada busca, mas isso tende a se tornar um gargalo quando o volume de leitura cresce.

Por isso, este projeto pretende separar dois fluxos principais:

```txt
Caminho de escrita:
motorista envia localização -> evento -> processamento assíncrono -> cache geoespacial

Caminho de leitura:
usuário busca motoristas próximos -> consulta rápida no cache geoespacial
```

## Objetivo

Construir uma arquitetura baseada em microsserviços para demonstrar como um sistema de localização em tempo real pode ser desenhado para:

* receber atualizações GPS frequentes;
* processar eventos de localização de forma assíncrona;
* armazenar a posição atual dos motoristas em um cache geoespacial;
* consultar motoristas próximos com baixa latência;
* evitar sobrecarga no banco de dados relacional;
* evoluir gradualmente para cenários de maior escala.

## Stack inicial planejada

A stack inicial do projeto será:

* **Python**
* **FastAPI**
* **PostgreSQL**
* **Redis**
* **Redis GEO**
* **Redis Streams**
* **Docker**
* **Docker Compose**

Com o tempo, o projeto pode evoluir para incluir:

* Prometheus;
* Grafana;
* testes de carga;
* particionamento por região/geohash;
* API Gateway;
* Kafka;
* observabilidade distribuída.

## Arquitetura planejada

A primeira versão será composta por alguns serviços principais:

```txt
+-------------------------+
| Driver Service          |
| Cadastro/status driver  |
+-------------------------+

+-------------------------+
| Location Ingest Service |
| Recebe updates GPS      |
+-------------------------+

+-----------------------------+
| Location Processor Service  |
| Processa eventos GPS        |
+-----------------------------+

+-------------------------+
| Nearby Search Service    |
| Busca drivers próximos   |
+-------------------------+

+-------------------------+
| Redis Streams           |
| Fila/eventos GPS         |
+-------------------------+

+-------------------------+
| Redis GEO               |
| Cache geoespacial       |
+-------------------------+

+-------------------------+
| PostgreSQL              |
| Dados persistentes      |
+-------------------------+
```

## Responsabilidade de cada serviço

### Driver Service

Serviço responsável pelos dados persistentes dos motoristas.

Inicialmente, ele deve permitir:

* cadastrar motoristas;
* consultar motoristas;
* alterar status do motorista;
* marcar motorista como disponível, ocupado ou offline.

Esses dados serão persistidos no PostgreSQL.

---

### Location Ingest Service

Serviço responsável por receber atualizações de localização dos motoristas.

Ele deve receber informações como:

```json
{
  "driver_id": "driver-001",
  "lat": -22.9068,
  "lng": -43.1729,
  "status": "available"
}
```

Esse serviço não deve fazer a busca geoespacial diretamente. A ideia é que ele apenas valide a requisição e publique um evento de localização.

---

### Location Processor Service

Serviço responsável por consumir os eventos de localização e atualizar o Redis GEO.

Ele será responsável por manter o estado atual da localização dos motoristas disponíveis.

Exemplo conceitual:

```txt
GEOADD drivers:available -43.1729 -22.9068 driver-001
```

Assim, a posição atual do motorista fica disponível para consultas rápidas.

---

### Nearby Search Service

Serviço responsável por consultar motoristas próximos a partir de uma latitude, longitude e raio.

Exemplo de consulta:

```txt
GET /nearby?lat=-22.9068&lng=-43.1729&radius_km=3
```

Esse serviço deve consultar o Redis GEO, e não o PostgreSQL, para evitar que o banco relacional fique no caminho crítico de leitura.

## Fluxo de escrita

```txt
Motorista
   |
   v
Location Ingest Service
   |
   v
Redis Streams
   |
   v
Location Processor Service
   |
   v
Redis GEO
```

Esse fluxo aceita consistência eventual. Ou seja, uma localização pode levar um pequeno intervalo até ser processada e aparecer nas consultas.

## Fluxo de leitura

```txt
Usuário
   |
   v
Nearby Search Service
   |
   v
Redis GEO
   |
   v
Motoristas próximos
```

Esse é o fluxo mais importante do projeto, pois representa o caminho que precisa ser otimizado para suportar alto volume de requisições.

## Por que Redis GEO?

O Redis GEO permite armazenar coordenadas geográficas e realizar buscas por raio em memória.

Isso é útil porque a busca por motoristas próximos precisa ser rápida e não deve depender diretamente de consultas pesadas no banco relacional.

O PostgreSQL será usado para dados persistentes, enquanto o Redis GEO será usado para o estado atual de localização.

## Por que Redis Streams?

O Redis Streams será usado inicialmente para representar a fila de eventos de localização.

A escolha foi feita para manter o projeto mais simples no começo, já que o Redis também será usado para o cache geoespacial.

No futuro, o Redis Streams pode ser substituído por Kafka, caso o projeto evolua para uma simulação mais robusta de ingestão em alta escala.

## Estratégia de evolução

A ideia é desenvolver o projeto em fases.

### Fase 1 — Base do projeto (Concluído)

* Criar estrutura com Docker Compose.
* Criar os serviços principais.
* Subir PostgreSQL e Redis.
* Criar endpoints básicos.
* Implementar cadastro e status de motoristas.

### Fase 2 — Localização em tempo real (Concluído)

* Criar endpoint para envio de localização.
* Publicar eventos no Redis Streams.
* Criar worker para consumir eventos.
* Atualizar posições no Redis GEO.
* Criar endpoint para buscar motoristas próximos.

### Fase 3 — Simulação (Concluído)

* Criar simulador de motoristas.
* Gerar localizações automaticamente.
* Simular updates a cada 4 segundos.
* Testar consultas por raio.

### Fase 4 — Performance (Concluído)

* Medir tempo de resposta das consultas.
* Comparar consulta via banco relacional com consulta via Redis GEO.
* Simular aumento de motoristas ativos.
* Documentar os resultados.

### Fase 5 — Escalabilidade (Em andamento)

* [x] Adicionar limite (COUNT) nas buscas de raio para evitar sobrecarga de payload.
* [x] Adicionar múltiplas instâncias dos serviços de leitura (Load Balancer com Nginx).
* [ ] Separar dados por cidade/região (Sharding geográfico).
* [ ] Estudar particionamento avançado por geohash ou H3.
* [ ] Avaliar uso de Redis Cluster.
* [ ] Avaliar substituição do Redis Streams por Kafka.

## Observação sobre escala

Este projeto não começa com a pretensão de suportar 1 milhão de requisições por segundo em ambiente local.

O objetivo é construir uma base arquitetural que demonstre como um sistema desse tipo poderia evoluir para alta escala.

O foco está nas decisões de arquitetura:

* tirar o banco relacional do caminho crítico de leitura;
* usar cache geoespacial em memória;
* processar updates GPS de forma assíncrona;
* separar responsabilidades em microsserviços;
* aceitar consistência eventual para localização;
* permitir particionamento por região ou geohash.

## Status do projeto

Projeto em fase inicial de planejamento e implementação.

## Licença

Projeto criado para fins de estudo, prática de arquitetura backend e portfólio.
