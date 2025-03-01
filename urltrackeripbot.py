import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from urllib.parse import urljoin

# Função para coletar IPs
def coletar_ip(url, visited=None):
    if visited is None:
        visited = set()

    try:
        # Verifica se a URL já foi visitada
        if url in visited:
            return set()
        visited.add(url)

        response = requests.get(url)
        response.raise_for_status()  # Levanta erro se a requisição falhar

        # Expressão regular para identificar endereços IP
        ips = re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', response.text)

        # Buscando IPs em atributos HTML como href, src, data-src, etc.
        atributos_html = re.findall(r'(?:href|src|data-src)="([^"]+)"', response.text)
        for atributo in atributos_html:
            # Verifica se o atributo contém um IP
            ips.extend(re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', atributo))

        # Coleta IPs de links internos
        links_internos = re.findall(r'href="([^"]+)"', response.text)
        for link in links_internos:
            link_absoluto = urljoin(url, link)  # Converte para URL absoluta
            if link_absoluto not in visited:
                ips.extend(coletar_ip(link_absoluto, visited))  # Coleta IPs recursivamente

        # Remove duplicatas e retorna os IPs únicos
        return set(ips)
    except requests.exceptions.RequestException as e:
        return str(e)  # Retorna o erro caso a requisição falhe

# Função para o comando /coletarip
async def coletar_ip_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 1:
        url = context.args[0]
        ips = coletar_ip(url)
        if isinstance(ips, set) and ips:
            # Mensagem com emojis, mostrando todos os IPs encontrados
            await update.message.reply_text(f"🌐 IPs encontrados no site {url}:\n\n" + "🌟\n".join(ips) + " 🌟")
        else:
            await update.message.reply_text(f"🚫 Não foram encontrados IPs ou houve um erro: {ips} ⚠️")
    else:
        await update.message.reply_text("⚠️ Por favor, forneça a URL com o comando, por exemplo: /coletarip https://www.example.com/ 🌍")

# Função principal para configurar o bot
def main():
    # Substitua pelo seu token do bot
    application = Application.builder().token(" TOKEN DO SEU BOT ").build()

    # Adiciona o manipulador de comandos
    application.add_handler(CommandHandler("coletarip", coletar_ip_comando))

    # Inicia o bot
    application.run_polling()

if __name__ == '__main__':
    main()