# Estrutura Inicial da API + Conexão com Banco de Dados
## Projeto: Bot Financeiro Multi-Canal (Telegram + WhatsApp)

Você é um engenheiro de software especialista em Python, arquitetura limpa (Clean Architecture) e desenvolvimento backend orientado a domínio.

Seu objetivo é gerar o esqueleto inicial completo de uma aplicação monolítica em Python para um bot financeiro multi-canal, com suporte atual para Telegram e preparado para WhatsApp futuramente.

O foco desta etapa é:

- Estrutura da aplicação
- Conexão com banco de dados
- Configuração do ambiente
- Models ORM
- Entidades de domínio
- Repositórios
- Injeção de dependência
- Inicialização da aplicação

A aplicação deve seguir uma abordagem simples, pragmática e pythonica de Clean Architecture, evitando overengineering.

NÃO utilizar:
- Abstract classes desnecessárias
- Factories complexas
- Container DI sofisticado
- Camadas excessivas
- Padrões enterprise artificiais

A prioridade é:
- Clareza
- Separação de responsabilidades
- Facilidade de manutenção
- Escalabilidade futura
- Simplicidade idiomática em Python

---

# Stack obrigatória

- Python 3.10+
- SQLAlchemy 2.0+
- PyMySQL
- python-dotenv

---

# Estrutura obrigatória de pastas

```text
piggy-money-api/
├── core/
│   ├── entity/
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── account.py
│   │   ├── credit_card.py
│   │   ├── benefit_card.py
│   │   ├── category.py
│   │   └── invoice.py
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   └── finance_service.py
│   │
│   └── ai/
│       └── intent_parser.py
│
├── infra/
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   └── repositories/
│       ├── user_repository.py
│       ├── transaction_repository.py
│       ├── account_repository.py
│       └── category_repository.py
│
├── channels/
│   ├── telegram/
│   │   └── handlers.py
│   │
│   └── whatsapp/
│       └── handlers.py
│
├── config/
│   └── settings.py
│
├── .env
├── requirements.txt
└── main.py
```

IMPORTANTE:

A estrutura acima representa apenas as PASTAS principais obrigatórias da arquitetura.

Os arquivos internos mostrados anteriormente eram apenas exemplos organizacionais.

Você possui liberdade para:
- criar subpastas
- criar arquivos adicionais
- reorganizar módulos internos
- separar responsabilidades

Desde que:
- mantenha a separação arquitetural
- preserve a simplicidade
- siga Clean Architecture de forma pragmática
- mantenha o projeto pythonico e fácil de evoluir

Exemplos válidos:
- `core/entity/`
- `core/services/`
- `infra/database/`
- `infra/repositories/`
- `infra/providers/`
- `channels/telegram/`
- `channels/whatsapp/`

A estrutura final deve ser definida conforme a necessidade real do projeto.

---

# Regras arquiteturais

## 1. Core = domínio puro

Tudo dentro de `core/` NÃO pode depender de:
- SQLAlchemy
- banco de dados
- frameworks externos
- Telegram
- WhatsApp

O core deve conhecer apenas:
- regras de negócio
- entidades
- serviços

---

# 2. Entidades de domínio

As entidades devem utilizar:
- dataclasses
OU
- Pydantic BaseModel

As entidades representam objetos reais do domínio financeiro.

Exemplos:
- User
- Transaction
- Account
- CreditCard
- BenefitCard
- Category
- Invoice

As entidades:
- NÃO possuem ORM
- NÃO possuem dependência de banco
- NÃO conhecem SQLAlchemy

Adicionar:
- validações simples
- valores default
- métodos utilitários básicos

---

# 3. Services

Os services representam casos de uso.

Eles:
- orquestram regras de negócio
- utilizam repositórios
- NÃO acessam banco diretamente
- NÃO usam SQLAlchemy diretamente

Exemplos:
- registrar usuário
- registrar gasto
- consultar saldo
- listar transações

Os services recebem os repositórios via construtor (injeção manual simples).

Exemplo:

```python
class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
```

NÃO usar:
- dependency injection framework
- containers

---

# 4. Infra

Responsável por:
- banco de dados
- SQLAlchemy
- ORM
- providers externos
- integração com APIs
- detalhes técnicos

Exemplos possíveis:
- `infra/database`
- `infra/repositories`
- `infra/providers`

Utilizar SQLAlchemy 2.0.

---

# 5. Repositórios

Os repositórios:
- acessam banco
- usam ORM
- convertem ORM <-> entidade de domínio

Os métodos devem retornar entidades do domínio e nunca models ORM diretamente.

Implementar operações básicas:
- create
- get_by_id
- list
- update
- delete

Sem complexidade excessiva.

---

# 6. Channels

Os channels são adaptadores de entrada.

Por enquanto:
- handlers simples
- placeholders
- apenas simulando recebimento de mensagens

Os handlers recebem services já prontos.

Exemplo:

```python
telegram_handler = TelegramHandler(user_service, finance_service)
```

NÃO implementar integração real ainda.

---

# 7. Configuração

Utilizar:
- python-dotenv

Centralizar configurações em:
- `config/settings.py`

Responsável por:
- carregar variáveis de ambiente
- montar DATABASE_URL
- centralizar configs do projeto

Exemplo esperado no `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=piggy-money-data
```

---

# 8. Banco de dados

Schema MySQL já modelado.

Implementar ORM SQLAlchemy para:

- usuario
- conta
- cartao_credito
- cartao_beneficio
- categoria
- fatura_cartao
- transacao

Todos relacionamentos com:
- ForeignKey
- ON DELETE CASCADE

Utilizar:
- mapped_column
- relationship
- DeclarativeBase

Compatível com SQLAlchemy 2.0.

---

# 9. main.py

O `main.py` deve:

1. Carregar configurações
2. Criar engine SQLAlchemy
3. Criar tabelas automaticamente

```python
Base.metadata.create_all(bind=engine)
```

4. Instanciar repositórios
5. Instanciar services
6. Injetar services nos handlers
7. Exibir mensagens de inicialização

Exemplo esperado:

```bash
[OK] Banco conectado
[OK] Tabelas carregadas
[OK] Telegram inicializado
```

---

# Requisitos importantes

O código gerado deve ser:
- funcional
- organizado
- executável
- simples
- idiomático em Python
- fácil de evoluir

Evitar:
- excesso de abstração
- padrões enterprise desnecessários
- arquitetura “Java em Python”

---

# Formato da resposta

Gerar TODOS os arquivos necessários para a aplicação funcionar.

Você tem liberdade para criar:
- novos módulos
- novos arquivos
- subpastas adicionais
- separações internas

Sempre respeitando:
- Clean Architecture pragmática
- simplicidade
- legibilidade
- separação de responsabilidades

Cada arquivo deve possuir cabeçalho no formato:

```text
### meu-app-bot/core/services/user_service.py
```

Incluir:
- código completo
- imports corretos
- comentários explicativos
- tipagem
- exemplos mínimos

Gerar uma base pronta para evolução futura do produto.
