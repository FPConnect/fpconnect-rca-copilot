import type { Metadata } from "next";
import Link from "next/link";
import BrandLogo from "@/components/BrandLogo";

export const metadata: Metadata = {
  title: "Privacidade e dados | OPSPECTA",
  description: "Informações sobre tratamento de dados no site público da OPSPECTA, contato, direitos de titulares e limites da análise operacional.",
  alternates: { canonical: "/privacidade" },
};

const contact = "https://wa.me/5547996789861?text=Ol%C3%A1%2C%20quero%20falar%20com%20a%20OPSPECTA%20sobre%20privacidade%20e%20tratamento%20de%20dados.";

export default function PrivacyPage() {
  return (
    <main id="conteudo-principal" className="min-h-screen bg-[#f4f8fa] text-[#071a3d]">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between gap-5 px-5 py-5 sm:px-8">
          <Link href="/" aria-label="OPSPECTA — início"><BrandLogo /></Link>
          <Link href="/ia-responsavel" className="text-sm font-bold text-[#075c63] underline underline-offset-4">IA responsável</Link>
        </div>
      </header>
      <article className="mx-auto max-w-4xl px-5 py-14 sm:px-8">
        <p className="text-xs font-black uppercase tracking-wide text-[#075c63]">Transparência institucional</p>
        <h1 className="mt-3 text-3xl font-black sm:text-5xl">Privacidade e tratamento de dados</h1>
        <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-700">
          A OPSPECTA desenvolve soluções de análise operacional para serviços de tecnologia em saúde.
          Esta página informa como tratamos a privacidade no <strong>site público</strong> e quais cuidados
          são necessários antes de usar dados técnicos em um diagnóstico.
        </p>
        <div className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm leading-7 text-amber-950">
          <strong>Escopo:</strong> este aviso público não substitui contratos, avisos específicos do
          ambiente autenticado, acordos de tratamento ou avaliação jurídica de cada projeto.
          A responsabilidade concreta pelo tratamento depende da finalidade, da fonte e dos papéis acordados.
        </div>

        <div className="mt-10 space-y-9 text-slate-700">
          <section aria-labelledby="dados-visitante">
            <h2 id="dados-visitante" className="text-2xl font-black text-[#071a3d]">1. Visitas ao site e fornecedores</h2>
            <p className="mt-3 leading-7">
              A infraestrutura de hospedagem e serviços de segurança podem processar registros técnicos
              necessários à entrega e proteção das páginas, como endereço IP, navegador, horário e erros.
              Serviços de terceiros são regidos também por suas próprias políticas.
              Não afirmamos que essas informações sejam anônimas nem que não existam logs.
            </p>
          </section>
          <section aria-labelledby="autoavaliacao">
            <h2 id="autoavaliacao" className="text-2xl font-black text-[#071a3d]">2. Checklist e autoavaliação</h2>
            <p className="mt-3 leading-7">
              No checklist de oito perguntas, os itens marcados são processados no próprio navegador
              para apresentar uma pontuação educativa. A ferramenta não possui um comando de envio
              dessas respostas à OPSPECTA. Não digite informações de pacientes, senhas ou logs confidenciais
              nas páginas públicas.
            </p>
          </section>
          <section aria-labelledby="contato">
            <h2 id="contato" className="text-2xl font-black text-[#071a3d]">3. Contato comercial</h2>
            <p className="mt-3 leading-7">
              Se você escolher entrar em contato pelo WhatsApp indicado nas páginas, a mensagem e os
              dados fornecidos serão tratados para responder à solicitação e avaliar a viabilidade
              da proposta. O WhatsApp também trata informações segundo sua própria política.
              Não envie dados de pacientes, credenciais nem arquivos técnicos restritos por esse canal.
              Antes de receber material operacional real, definiremos canal autorizado, finalidade,
              minimização, acesso, prazo de retenção e eliminação conforme o caso concreto.
            </p>
          </section>
          <section aria-labelledby="newsletter">
            <h2 id="newsletter" className="text-2xl font-black text-[#071a3d]">4. Newsletter e comunicação por e-mail</h2>
            <p className="mt-3 leading-7">
              O site público não oferece, nesta versão, cadastro operacional em newsletter.
              Nenhum visitante se torna assinante automaticamente ao utilizar o checklist.
              Quando for disponibilizada uma inscrição, a finalidade, o provedor, os termos
              e o cancelamento de inscrição devem estar informados antes da coleta do e-mail.
              Conversas comerciais não geram inscrição automática.
            </p>
          </section>
          <section aria-labelledby="direitos">
            <h2 id="direitos" className="text-2xl font-black text-[#071a3d]">5. Solicitações e direitos</h2>
            <p className="mt-3 leading-7">
              Você pode solicitar informações sobre dados pessoais relacionados a um atendimento,
              ou exercer os direitos aplicáveis à sua situação, pelo canal abaixo. Para evitar
              a exposição de dados, poderemos precisar verificar legitimidade e identidade
              antes de apresentar ou alterar informações.
            </p>
            <a
              href={contact}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-5 inline-flex min-h-12 items-center rounded-lg bg-[#071a3d] px-5 py-3 font-bold text-white hover:bg-[#0a7f86]"
            >
              Solicitar atendimento sobre privacidade
            </a>
          </section>
          <section aria-labelledby="limites">
            <h2 id="limites" className="text-2xl font-black text-[#071a3d]">6. Limites da inteligência operacional</h2>
            <p className="mt-3 leading-7">
              Resultados assistidos por IA são hipóteses e requerem revisão humana qualificada.
              Os exemplos publicados usam dados sintéticos. A OPSPECTA não utiliza resultados
              educativos das páginas públicas para automatizar decisões sobre pessoas, pacientes
              ou liberação de equipamentos médicos.
            </p>
            <p className="mt-3 leading-7">
              Consulte também a <Link href="/ia-responsavel" className="font-bold text-[#075c63] underline underline-offset-4">página de IA responsável</Link>,
              que detalha controles técnicos desenvolvidos e validações ainda pendentes.
            </p>
          </section>
        </div>
        <footer className="mt-12 border-t border-slate-200 pt-6 text-sm text-slate-600">
          Última atualização: 4 de novembro de 2026. Conteúdo informativo sujeito a revisão
          conforme o produto, os fornecedores e a finalidade do tratamento.
        </footer>
      </article>
    </main>
  );
}
