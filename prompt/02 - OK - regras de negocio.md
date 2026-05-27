# 02 - regras de negocio.md

# Regras de Negócio — Bot Financeiro Multi-Canal

## Objetivo

Você é um engenheiro de software especialista em Python, DDD e Clean Architecture.

Sua tarefa é implementar TODAS as regras de negócio da aplicação financeira já estruturada anteriormente.

O foco agora é:

* Casos de uso (use cases)
* Regras de negócio
* Serviços
* Repositórios
* Validações
* Regras financeiras
* Filtros e consultas
* Regras de deleção
* Atualizações de saldo e limite

A implementação deve continuar:

* simples
* pythonica
* pragmática
* desacoplada
* fácil de manter

Evitar:

* overengineering
* patterns desnecessários
* abstrações artificiais
* interfaces excessivas

---

# Regras Gerais

## Regra global de nomes únicos

O usuário NÃO pode possuir dois registros do mesmo tipo com exatamente o mesmo nome.

Exemplos inválidos:

* duas contas chamadas "Nubank"
* dois cartões chamados "Visa Itaú"
* dois cartões benefício chamados "VA"
* duas categorias chamadas "Mercado"

A validação deve ocorrer:

* na criação
* na atualização

A validação deve considerar:

* mesmo usuário
* mesmo tipo de entidade
* comparação case insensitive

Exemplo:

* "visa"
* "Visa"
* "VISA"

Devem ser considerados iguais.

---

# Categorias

## Cadastro de categoria

Campos:

* nome
* usuario_id

Regras:

* nome obrigatório
* nome único por usuário

Criar use case dedicado:

* CreateCategoryUseCase

---

## Atualização de categoria

Permitir alterar:

* nome

Regras:

* manter unicidade do nome

Criar use case:

* UpdateCategoryUseCase

---

## Remoção de categoria

Ao remover uma categoria:

* NÃO deletar as transações
* mover automaticamente todas as transações para a categoria default

Categoria default:

* nome: "Sem categoria"
* deve existir automaticamente para todos os usuários

Caso não exista:

* criar automaticamente

Criar use case:

* DeleteCategoryUseCase

---

# Contas

## Cadastro de conta

Campos:

* nome
* saldo_inicial
* usuario_id

Regras:

* nome obrigatório
* saldo inicial obrigatório
* permitir múltiplas contas por usuário
* não permitir nomes duplicados

Criar use case:

* CreateAccountUseCase

---

## Atualização de conta

Permitir alterar:

* nome
* saldo_inicial

Regras:

* validar nome único

Criar use case:

* UpdateAccountUseCase

---

## Remoção de conta

Ao remover uma conta:

* remover todas as transações relacionadas
* remoção em cascata

Criar use case:

* DeleteAccountUseCase

---

# Cartão de Crédito

## Cadastro de cartão de crédito

Campos obrigatórios:

* nome
* limite_total
* dia_fechamento
* dia_vencimento
* usuario_id

Campos opcionais:

* conta_id

Regras:

* permitir múltiplos cartões
* nome único por usuário
* limite obrigatório
* fechamento obrigatório
* vencimento obrigatório

Criar use case:

* CreateCreditCardUseCase

---

## Atualização de cartão de crédito

Permitir alterar:

* nome
* limite_total
* dia_fechamento
* dia_vencimento
* conta_id

Regras:

* validar unicidade do nome

Criar use case:

* UpdateCreditCardUseCase

---

## Remoção de cartão de crédito

Ao remover:

* remover transações relacionadas
* remover faturas relacionadas
* deleção em cascata

Criar use case:

* DeleteCreditCardUseCase

---

# Cartão Benefício

## Cadastro de cartão benefício

Campos:

* nome
* saldo_inicial
* usuario_id

Regras:

* permitir múltiplos cartões
* nome único

Criar use case:

* CreateBenefitCardUseCase

---

## Atualização de cartão benefício

Permitir alterar:

* nome
* saldo_inicial

Regras:

* validar nome único

Criar use case:

* UpdateBenefitCardUseCase

---

## Remoção de cartão benefício

Ao remover:

* remover transações relacionadas
* deleção em cascata

Criar use case:

* DeleteBenefitCardUseCase

---

# Transações

## Cadastro de transação

Campos obrigatórios:

* valor
* descricao
* tipo_movimento
* origem financeira

A origem financeira obrigatoriamente deve ser UMA das opções:

* conta
* cartão de crédito
* cartão benefício

Nunca permitir múltiplas origens simultaneamente.

---

# Tipos de movimento

Tipos válidos:

* ENTRADA
* SAIDA

---

# Regras de cartão de crédito

Cartão de crédito:

* NÃO pode receber transações do tipo ENTRADA
* somente SAIDA

Exemplo inválido:

* adicionar salário em cartão de crédito

---

# Campos opcionais

Campos opcionais:

* efetivada
* data
* parcelas_total

Defaults:

* efetivada = True
* data = data atual
* parcelas_total = 1

---

# Parcelamento

Quando parcelas_total > 1:

* criar múltiplas transações
* uma para cada mês
* manter o mesmo valor dividido igualmente
* manter descrição
* manter categoria
* manter origem financeira

Exemplo:

Compra:

* valor total = 300
* parcelas_total = 3

Resultado:

* parcela 1 = 100
* parcela 2 = 100
* parcela 3 = 100

As parcelas devem:

* ser geradas nos meses seguintes
* manter o dia original sempre que possível
* ajustar automaticamente datas inválidas

Exemplo:

31/01

Próxima parcela:

* fevereiro deve ajustar para 28 ou 29

Todas as parcelas devem possuir:

* parcela_atual
* parcelas_total
* transacao_original_id

---

# Efetivação de transação

Quando uma transação for efetivada:

* atualizar saldo da conta
* atualizar saldo do benefício
* atualizar limite utilizado do cartão

---

# Regras de saldo

## Conta

ENTRADA:

* soma saldo

SAIDA:

* reduz saldo

---

## Cartão benefício

ENTRADA:

* soma saldo

SAIDA:

* reduz saldo

---

## Cartão crédito

SAIDA:

* consome limite disponível

ENTRADA:

* proibido

---

# Pagamento de fatura

Cartão de crédito deve permitir:

* pagamento parcial
* pagamento total da fatura

Quando pagamento for efetivado:

* liberar limite proporcional pago

Exemplo:

* limite total = 1000
* utilizado = 700
* pagamento = 300

Novo limite utilizado:

* 400

Criar use cases:

* PayCreditCardInvoiceUseCase
* GenerateInvoiceUseCase

---

# Atualização de transação

Permitir alterar:

* descrição
* valor
* categoria
* data
* efetivada

Regras:

* recalcular saldo
* recalcular limite
* recalcular fatura se necessário

Criar use case:

* UpdateTransactionUseCase

---

# Remoção de transação

Ao remover:

* desfazer impacto financeiro
* devolver saldo
* devolver limite

Criar use case:

* DeleteTransactionUseCase

---

# Consultas e filtros

Criar um único use case de consulta:

* ListTransactionsUseCase

Ele deve permitir filtros dinâmicos.

---

# Filtros suportados

Filtros possíveis:

* data_inicio
* data_fim
* categoria_id
* conta_id
* cartao_credito_id
* cartao_beneficio_id
* tipo_movimento
* efetivada

---

# Regras de filtro

Se informar:

* categoria
  => filtrar categoria

Se informar:

* categoria + data_inicio + data_fim
  => aplicar todos filtros

Se informar:

* conta + tipo_movimento
  => aplicar ambos

Os filtros devem ser:

* combináveis
* opcionais
* dinâmicos

Não criar múltiplos use cases de listagem.

Toda consulta deve ser centralizada em:

* ListTransactionsUseCase

---

# Repositórios

Criar todos os repositórios necessários.

Exemplos:

* UserRepository
* AccountRepository
* CategoryRepository
* TransactionRepository
* CreditCardRepository
* BenefitCardRepository
* InvoiceRepository

Os repositórios devem:

* acessar banco
* converter ORM -> entidade
* converter entidade -> ORM
* encapsular queries

---

# Organização esperada

Criar:

* entities
* repositories
* services
* use cases
* regras financeiras
* validações
* filtros
* cálculos

Separar responsabilidades.

---

# Requisitos importantes

O código deve ser:

* funcional
* simples
* limpo
* pythonico
* escalável
* desacoplado
* fácil de manter

Evitar:

* abstrações excessivas
* arquitetura Java-like
* patterns artificiais
* complexidade desnecessária

---

# Formato da resposta

Gerar todos os arquivos necessários.

Cada arquivo deve possuir cabeçalho:

```text
### caminho/do/arquivo.py
```

Incluir:

* código completo
* imports corretos
* tipagem
* comentários importantes
* exemplos mínimos

A implementação deve estar pronta para evolução futura do produto.
