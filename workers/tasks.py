from celery import Celery, signals
from services.waha_service import send_message
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
load_dotenv()

app = Celery('tasks', broker='pyamqp://guest:guest@rabbitmq//')
app.conf.result_expires = 60

@signals.worker_process_init.connect
def initialize_global_resource(**kwargs):
    global agent

    with open("data/reab.md", "r") as f:
        reab_doc = f.read()

    with open("data/prompt.xml", "r") as f:
        prompt_doc = f.read()

    agent = Agent(
        model=OpenAIChat(id='gpt-4o-mini'),
        instructions="<fatos>" + "\n" + reab_doc + "\n" + "</fatos>" + "\n" + prompt_doc
        )

# ... (imports anteriores mantidos)

@app.task
def task_answer(chat_id, prompt):
    print(f"🚀 [DEBUG] Iniciando processamento para: {chat_id}")
    
    # 1. Verifica a resposta da IA
    message = get_ai_answer(prompt=prompt)
    print(f"🤖 [DEBUG] Resposta gerada pela IA: '{message}'")
    
    if not message:
        print("❌ [ERRO] A IA retornou uma mensagem vazia.")
        return

    # 2. Verifica o envio para o Waha
    try:
        # Aqui capturamos o retorno da função send_message para ver se deu status 200
        response_waha = send_message(chat_id, message) 
        print(f"uD83D\uDCE4 [DEBUG] Retorno do Waha Service: {response_waha}")
    except Exception as e:
        print(f"❌ [ERRO] Falha ao enviar mensagem para o Waha: {e}")

def get_ai_answer(prompt: str) -> str | None:
    try:
        # Dica: Não precisa prefixar com "VOCÊ ENVIOU", o agent já sabe que é input do user
        # prompt_formatado = f'VOCÊ ENVIOU: {prompt}' 
        
        result = agent.run(input=prompt)
        
        # Agno pode retornar objetos complexos, garantimos que é string
        if hasattr(result, 'content'):
            return result.content
        return str(result)
        
    except Exception as e:
        print(f"❌ [ERRO] Exceção na IA: {e}")
        return None
