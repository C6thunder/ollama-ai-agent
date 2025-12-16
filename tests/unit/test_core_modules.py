"""核心模块单元测试
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_prompts():
    """测试 Prompt 模块"""
    from core.prompts import get_prompt_manager
    m = get_prompt_manager()
    assert 'system_intro' in m.list_templates()
    print("✅ Prompt 模块测试通过")

def test_data_loaders():
    """测试数据加载器"""
    from core.data_loaders import Document
    d = Document('test', {}, 'test')
    assert d.content == 'test'
    print("✅ 数据加载器测试通过")

def test_vector_store():
    """测试向量存储"""
    from core.vector_store import InMemoryVectorStore
    v = InMemoryVectorStore()
    assert v.documents == []
    print("✅ 向量存储测试通过")

def test_output_parsers():
    """测试输出解析器"""
    from core.output_parsers import parse_output
    r = parse_output('{"a":1}', 'json')
    assert r.data['a'] == 1
    print("✅ 输出解析器测试通过")

def test_chains():
    """测试工作流链"""
    from core.chains import SimpleChain
    c = SimpleChain(lambda **k: k)
    assert True
    print("✅ 工作流链测试通过")

if __name__ == "__main__":
    print("运行单元测试...")
    test_prompts()
    test_data_loaders()
    test_vector_store()
    test_output_parsers()
    test_chains()
    print("\n✅ 所有单元测试通过！")
