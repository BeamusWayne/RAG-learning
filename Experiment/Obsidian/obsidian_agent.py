from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import readline  # 提升命令行交互体验

# ========== 适配qwen3-vl:8b的配置 ==========
Settings.llm = Ollama(
    model="qwen3-vl:8b",
    base_url="http://localhost:11434",
    temperature=0.7,  # 写作场景适当提高温度，增加创造性
    num_ctx=8192,
    timeout=300.0
)

Settings.embed_model = OllamaEmbedding(
    model_name="qwen3-vl:8b",
    base_url="http://localhost:11434"
)

# ========== 加载本地索引 ==========
def load_local_index(index_dir="./obsidian_index"):
    if not os.path.exists(index_dir):
        raise FileNotFoundError(f"索引文件夹 {index_dir} 不存在，请先运行 obsidian_loader.py")
    
    storage_context = StorageContext.from_defaults(persist_dir=index_dir)
    index = load_index_from_storage(storage_context)
    # 优化检索配置（适配qwen3-vl）
    query_engine = index.as_query_engine(
        streaming=True,
        similarity_top_k=5,  # 取Top5相关文档，平衡精度和速度
        response_mode="compact"  # 紧凑回答模式，适合千问模型
    )
    return query_engine

# ========== 交互逻辑 ==========
def obsidian_agent():
    try:
        query_engine = load_local_index()
        print("=== Obsidian离线AI助手（qwen3-vl:8b）===")
        print("📌 功能说明：")
        print("   - 直接输入问题：基于知识库精准回答")
        print("   - 输入 write:标题/需求：辅助写作（如 write:5G技术总结）")
        print("   - 输入 exit：退出程序\n")
        
        while True:
            user_input = input("你：").strip()
            if not user_input:
                continue
            if user_input.lower() == "exit":
                print("👋 再见！")
                break
            
            # 写作模式（适配千问的中文写作风格）
            if user_input.startswith("write:"):
                write_topic = user_input.replace("write:", "").strip()
                prompt = f"""请基于我的Obsidian知识库，帮我完成以下写作任务：
                写作主题：{write_topic}
                写作要求：
                1. 严格结合知识库中的相关内容，保证内容的准确性
                2. 结构清晰，逻辑连贯，符合中文写作习惯
                3. 语言流畅自然，避免生硬的机器翻译风格
                4. 适当分点或分段，提升可读性
                """
            # 问答模式
            else:
                prompt = f"""请基于我的Obsidian知识库回答以下问题，仅使用知识库中的信息，不要编造内容：
                问题：{user_input}
                回答要求：
                1. 准确、简洁，直击问题核心
                2. 如果知识库中没有相关信息，请明确说明"未在知识库中找到相关信息"
                3. 用中文清晰表述，避免冗余
                """
            
            # 流式输出回答（避免等待过长）
            print("AI：", end="", flush=True)
            response = query_engine.query(prompt)
            for token in response.response_gen:
                print(token, end="", flush=True)
            print("\n" + "-"*50)
    
    except Exception as e:
        print(f"\n❌ 程序出错：{str(e)}")

if __name__ == "__main__":
    obsidian_agent()