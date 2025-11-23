from celery import Celery, signals
from services.waha_service import send_message
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from redisvl.extensions.cache.llm import SemanticCache
load_dotenv()

app = Celery('tasks', broker='pyamqp://guest:guest@rabbitmq//')
app.conf.result_expires = 60

agent = None
cache = None

@signals.worker_process_init.connect
def initialize_global_resource(**kwargs):
    global agent, cache

    with open("data/reab.md", "r") as f:
        reab_doc = f.read()

    with open("data/prompt.xml", "r") as f:
        prompt_doc = f.read()

    cache = connect_semantic_cache()
    agent = Agent(
        model=OpenAIChat(id='gpt-4o-mini'),
        instructions="<fatos>" + "\n" + reab_doc + "\n" + "</fatos>" + "\n" + prompt_doc
        )

@app.task
def task_answer(chat_id, prompt):
    print(f"[DEBUG] Iniciando processamento para: {chat_id}")

    if response := get_semanctic_cache_answer(cache=cache, prompt=prompt):
        message = f"(cache) {response}"
    else:
        message = get_ai_answer(prompt=prompt)
        if message:
            set_semanctic_cache_answer(cache=cache, prompt=prompt, answer=message)
        else:
            print("[ERRO] A IA retornou uma mensagem vazia.")
            return


    try:
        response_waha = send_message(chat_id, message) 
        print(f"uD83D\uDCE4 [DEBUG] Retorno do Waha Service: {response_waha}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem para o Waha: {e}")


def get_semanctic_cache_answer(cache: SemanticCache, prompt: str) -> str | None:
    
    response = cache.check(prompt=prompt)

    if len(response) == 0:
        return None
    
    return response[0]["response"]


def set_semanctic_cache_answer(cache: SemanticCache, prompt: str, answer: str) -> None:
    
    cache.store(
        prompt=prompt,
        response=answer
    )


def get_ai_answer(prompt: str) -> str | None:
    try:
        result = agent.run(input=prompt)
        
        if hasattr(result, 'content'):
            return result.content
        return str(result)
        
    except Exception as e:
        print(f"[ERRO] Exceção na IA: {e}")
        return None


def connect_semantic_cache() -> SemanticCache:
    return SemanticCache(
        name="llmcache",
        ttl=360,
        redis_url="redis://redis:6379",
        distance_threshold=0.1
    )