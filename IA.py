import flet as ft
from openai import OpenAI
import json

# Chave da API da DeepSeek / DeepSeek API Key
DEEPSEEK_API_KEY = ""  # sua chave da API deve ser escrita aqui / your API key should be written here
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Arquivo para histórico / History file
HISTORICO_ARQUIVO = "historico_conversas.json"


def carregar_historico() -> list[tuple[str, str]]:
    """
    Carrega o histórico de conversas de um arquivo JSON.
    Loads the conversation history from a JSON file.
    """
    try:
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(
            f"Arquivo de histórico '{HISTORICO_ARQUIVO}' não encontrado."
            " Iniciando com histórico vazio."
        )
        return []
    except json.JSONDecodeError:
        print(
            f"Erro ao decodificar o arquivo JSON '{HISTORICO_ARQUIVO}'."
            " Verifique se o arquivo está formatado corretamente."
        )
        return []


def salvar_historico(historico: list[tuple[str, str]]) -> None:
    """
    Salva o histórico de conversas em um arquivo JSON.
    Saves the conversation history to a JSON file.
    """
    try:
        with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar o histórico no arquivo: {e}")
        # Error saving history to the file

# Inicializa o histórico / Initialize history
historico = carregar_historico()


def resposta_bot(mensagens: list[tuple[str, str]]) -> str:
    """
    Gera uma resposta do bot usando a API da DeepSeek.
    Generates a bot response using the DeepSeek API.
    """
    mensagem_system = """Você é um assistente chamado Dip e trabalha para a empresa Diponto.
    Suas respostas não devem ser imaginativas, se baseie apenas em seu conhecimento.""" # O conhecimento pode ser adicionado aqui / knowledge can be added here

    mensagens_modelo = [{"role": "system", "content": mensagem_system}]
    mensagens_modelo += [
        {"role": role, "content": content} for role, content in mensagens
    ]

    response = client.chat.completions.create(
        model="deepseek-chat", messages=mensagens_modelo, stream=False
    )

    return response.choices[0].message.content


def main(pagina: ft.Page) -> None:
    """
    Configura a interface gráfica do assistente virtual.
    Sets up the virtual assistant's graphical interface.
    """
    pagina.title = "Assistente Virtual - Dip"
    pagina.vertical_alignment = ft.MainAxisAlignment.START

    # Interface do chat / Chat interface
    chat_texto = ft.TextField(
        label="Chat:",
        read_only=True,
        multiline=True,
        min_lines=15,
        max_lines=15,
        expand=True,
    )

    # Campo de entrada para o usuário / User input field
    entrada_texto = ft.TextField(label="Digite sua mensagem")

    def enviar_mensagem(e: ft.ControlEvent) -> None:
        """
        Envia a mensagem do usuário e exibe a resposta do bot.
        Sends the user's message and displays the bot's response.
        """
        pergunta = entrada_texto.value
        if not pergunta:
            return

        mensagens = []
        historico.append(("user", pergunta))  # Adiciona a pergunta ao histórico / Adds question to history
        resposta = resposta_bot(historico)  # Obtém a resposta do bot / Gets bot response
        historico.append(("assistant", resposta))  # Adiciona a resposta ao histórico / Adds response to history
        salvar_historico(historico)  # Salva o histórico / Saves history

        chat_texto.value += f"Você: {pergunta}\nDip: {resposta}\n\n"
        # You: {question}
        # Dip: {response}

        entrada_texto.value = ""
        pagina.update()

    # Botão para enviar a mensagem / Button to send message
    botao_enviar = ft.ElevatedButton("Enviar", on_click=enviar_mensagem)
    # "Send"

    # Layout da página / Page layout
    pagina.add(
        chat_texto,
        ft.Row(
            [entrada_texto, botao_enviar],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

# Inicializa o aplicativo Flet / Initializes the Flet app
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
