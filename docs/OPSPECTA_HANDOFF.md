# OPSPECTA - continuidade técnica

Documento de transferência para continuar o desenvolvimento, a operação ou a auditoria do produto em outra ferramenta. Não contém credenciais.

## Identidade e endereços

- Marca de apresentação: **OPSPECTA**.
- Domínio web canônico: `https://fpconnect.tec.br`.
- API de produção: `https://api.fpconnect.tec.br`.
- Repositório: `https://github.com/FPConnect/fpconnect-rca-copilot`.
- Projeto Vercel web: `fpconnect-rca-copilot`.
- Projeto Vercel API: `fpconnect-rca-copilot-main`.
- Equipe Vercel: `fpconnects-projects`.

FPConnect permanece como identificador técnico temporário em domínio, repositório e chaves locais. A troca desses identificadores exige migração própria para evitar quebra de URLs e sessões.

## Arquitetura

- Monorepo com frontend Next.js em `apps/web` e API FastAPI em `apps/api`.
- Autenticação por JWT, com token de acesso mantido na sessão do navegador.
- Banco PostgreSQL em produção.
- Deploy contínuo definido em `.github/workflows/deploy.yml`.
- Migração idempotente de colunas de produção em `apps/api/scripts/migrate_auth_schema.py`.

## Funcionalidades

- Cadastro controlado por lista de e-mails autorizados.
- Login, sessão, consulta e edição do perfil e alteração real de senha.
- Painel operacional, equipamentos, verificações de saúde, alertas e chamados.
- Análise assistida de causa raiz com resposta em português ou inglês.
- Métricas, manutenção, histórico e notificações.
- Playbooks e contratos/SLA com escrita restrita por nível de acesso.
- Controle de acesso e hipóteses estratégicas restritos a administradores.
- Interface bilíngue em português e inglês.

## Segurança operacional

- Nunca colocar tokens, senhas ou strings de conexão no repositório.
- Manter `PUBLIC_REGISTRATION_ENABLED=true` somente junto de `REGISTRATION_ALLOWED_EMAILS` restrita.
- Usuários criados publicamente recebem sempre papel `user` e nível 2.
- Rotas administrativas devem validar autorização na API; ocultar um item de menu não substitui autorização do servidor.
- Senhas exigem no mínimo 12 caracteres e complexidade; hashes atuais usam bcrypt.
- CORS de produção deve aceitar apenas os domínios públicos necessários.
- O limitador distribuído de autenticação usa `REDIS_URL` em produção; falha de Redis deve impedir a promoção do deployment da API.
- O envio de SMS retorna indisponível enquanto não houver provedor configurado; a interface não deve alegar ativação sem confirmação.

## Publicação

1. Executar lint, testes e build.
2. Executar a migração idempotente de produção.
3. Publicar a API e verificar `/health`, autenticação e autorização.
4. Publicar a web e verificar os fluxos no domínio público.
5. Confirmar aliases, logs e ausência de erros no navegador.

Consulte `README.md`, `docs/DEPLOYMENT.md` e `docs/DOMAIN_MIGRATION.md` para comandos e configuração detalhada.

## Limitações conhecidas

- SMS depende da contratação e configuração de um provedor externo.
- O domínio técnico ainda contém `fpconnect`; a migração para um domínio OPSPECTA deve preservar redirecionamentos e URLs de API.
- Dados ilustrativos devem permanecer explicitamente identificados e não podem ser apresentados como resultados reais de clientes.
