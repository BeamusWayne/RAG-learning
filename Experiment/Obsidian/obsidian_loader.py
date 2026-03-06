from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import os
import time
from datetime import datetime

# ========== 核心配置（适配qwen3-vl:8b） ==========
Settings.llm = Ollama(
    model="qwen3-vl:8b",  # 改为qwen3-vl:8b模型
    base_url="http://localhost:11434",
    temperature=0.1,  # 问答场景调低温度，保证准确性
    num_ctx=8192,     # 增大上下文窗口，适配长文本
    timeout=300.0     # 延长超时时间，避免5G知识库处理中断
)

# Embedding 使用 qwen3-embedding:4b，请先拉取：ollama pull qwen3-embedding:4b
Settings.embed_model = OllamaEmbedding(
    model_name="qwen3-embedding:4b",
    base_url="http://localhost:11434",
)

# ========== 增量加载逻辑（适配5G大知识库） ==========
def load_obsidian_kb(vault_path, index_dir="./obsidian_index"):
    # 记录文件最后修改时间的缓存文件
    cache_file = os.path.join(index_dir, "file_cache.txt")
    os.makedirs(index_dir, exist_ok=True)
    
    # 读取已处理文件的修改时间
    processed_files = {}
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if line.strip():
                    path, mtime = line.strip().split("\t")
                    processed_files[path] = float(mtime)
    
    # 加载所有md文件
    reader = SimpleDirectoryReader(
        vault_path,
        required_exts=[".md"],
        recursive=True,
        exclude_hidden=True  # 排除Obsidian隐藏文件
    )
    all_files = reader.input_files  # 元素为 Path 或 str，即文件路径本身
    new_or_updated_files = []

    # 筛选新增/修改的文件
    for file_path in all_files:
        path_str = str(file_path)
        file_mtime = os.path.getmtime(path_str)
        if path_str not in processed_files or file_mtime > processed_files[path_str]:
            new_or_updated_files.append(file_path)
            processed_files[path_str] = file_mtime
    
    if not new_or_updated_files:
        print("✅ 没有新增/修改的文件，直接加载现有索引")
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
        return index
    
    print(f"📄 发现 {len(new_or_updated_files)} 个新增/修改的文件，开始处理...")
    # SimpleDirectoryReader 通过 input_files 指定文件列表，load_data() 无参数
    path_list = [str(p) for p in new_or_updated_files]
    reader_subset = SimpleDirectoryReader(input_files=path_list)
    documents = reader_subset.load_data()
    
    # 增量更新索引
    if os.path.exists(os.path.join(index_dir, "vector_store")):
        print("🔄 增量更新索引...")
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
        index.refresh_ref_docs(documents)
    else:
        print("🚀 首次构建索引...")
        index = VectorStoreIndex.from_documents(documents)
    
    # 保存索引和缓存
    index.storage_context.persist(persist_dir=index_dir)
    with open(cache_file, "w", encoding="utf-8") as f:
        for path, mtime in processed_files.items():
            f.write(f"{path}\t{mtime}\n")
    
    print(f"✅ 索引处理完成！时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return index

# ========== 主执行逻辑 ==========
if __name__ == "__main__":
    # 替换为你的Obsidian Vault路径
    obsidian_vault_path = "/Users/katya/Files/LakeLLM/lib"
    start_time = time.time()
    
    try:
        index = load_obsidian_kb(obsidian_vault_path)
        print(f"⏱️  总耗时：{round(time.time() - start_time, 2)} 秒")
    except Exception as e:
        print(f"❌ 处理失败：{str(e)}")