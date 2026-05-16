# Migração do domínio para `fpconnect.tec.br`

Este documento descreve como publicar o FPConnect no domínio canônico `fpconnect.tec.br` e redirecionar o domínio antigo `hypersecit.com.br`.

## O que já fica preparado no código

- `NEXT_PUBLIC_SITE_URL` passa a ter o valor esperado `https://fpconnect.tec.br` nos exemplos de ambiente.
- A metadata do Next.js usa `NEXT_PUBLIC_SITE_URL` para canonical/Open Graph.
- `apps/web/next.config.js` redireciona permanentemente:
  - `https://hypersecit.com.br/*` → `https://fpconnect.tec.br/*`
  - `https://www.hypersecit.com.br/*` → `https://fpconnect.tec.br/*`
  - `https://www.fpconnect.tec.br/*` → `https://fpconnect.tec.br/*`

> Importante: o redirecionamento do domínio antigo só funciona se `hypersecit.com.br` continuar apontando para o mesmo projeto Vercel ou para uma camada/proxy que entregue esta aplicação.

## Pré-requisitos de acesso

Para fazer a transferência real, é necessário acesso a:

1. Conta do registrador/DNS do domínio `fpconnect.tec.br` — normalmente Registro.br ou o provedor DNS configurado nele.
2. Projeto Vercel que publica `apps/web`.
3. Projeto Railway/API pública usada em `NEXT_PUBLIC_API_URL`.
4. GitHub Actions secrets, se o deploy for automático.

## Configuração na Vercel

No projeto Vercel da Web:

1. Acesse **Project → Settings → Domains**.
2. Adicione o domínio principal:
   ```text
   fpconnect.tec.br
   ```
3. Opcionalmente adicione o alias:
   ```text
   www.fpconnect.tec.br
   ```
4. Configure as variáveis de produção:
   ```env
   NEXT_PUBLIC_SITE_URL=https://fpconnect.tec.br
   NEXT_PUBLIC_API_URL=https://<api-publica-de-producao>
   NEXT_PUBLIC_APP_NAME=FPConnect
   NEXT_PUBLIC_APP_VERSION=1.0.0
   ```
5. Faça um novo deploy de produção após alterar as variáveis.

## Configuração DNS

Use exatamente os registros indicados pela Vercel ao adicionar o domínio. O padrão costuma ser:

| Host | Tipo | Valor |
|---|---|---|
| `fpconnect.tec.br` | `A` | IP informado pela Vercel para apex/root domain |
| `www.fpconnect.tec.br` | `CNAME` | `cname.vercel-dns.com` ou valor informado pela Vercel |

Não adivinhe os registros em produção: copie os valores exibidos em **Vercel → Domains**, porque a Vercel valida o domínio com base nesses registros.

## Deploy

### Automático via GitHub Actions

O workflow `.github/workflows/deploy.yml` publica a Web quando há push na branch `main`, desde que o secret esteja configurado:

```text
VERCEL_TOKEN
```

Fluxo:

```bash
git push origin main
```

Depois acompanhe **GitHub → Actions → Deploy**.

### Manual via CLI

```bash
cd apps/web
npm ci
npm run build
vercel --prod
```

## Validação pós-migração

Após o DNS propagar e o deploy concluir:

```bash
curl -I https://fpconnect.tec.br
curl -I https://www.fpconnect.tec.br
curl -I https://hypersecit.com.br
```

Resultados esperados:

- `https://fpconnect.tec.br` responde `200`.
- `https://www.fpconnect.tec.br` redireciona para `https://fpconnect.tec.br`.
- `https://hypersecit.com.br` redireciona para `https://fpconnect.tec.br` enquanto o domínio antigo permanecer conectado.

## Rollback

Se houver problema:

1. Reverter o domínio principal no painel Vercel para o domínio anterior.
2. Fazer redeploy da versão anterior.
3. Se necessário, remover temporariamente os redirects em `apps/web/next.config.js`.
